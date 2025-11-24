from collections import deque
import random
import numpy
import networkx as nx
import matplotlib.pyplot as plt

from simulator import Network, Node

from baseline.procedures import (
    fragment_broadcast,
    _fragment_broadcast_handler,
    upcast_min,
    _upcast_min_handler,
    transmit_neighbor,
    _transmit_neighbor_handler,
    transmit_adjacent,
    _transmit_adjacent_handler,
    merge_up,
    _merge_up_handler,
    merge_down,
    _merge_down_handler,
)

from baseline.stages import (
    find_moe_entry,
    upcast_moe_entry,
    upcast_moe_exit,
    broadcast_moe_entry,
    broadcast_moe_exit,
    transmit_adjacent_moe_entry,
    transmit_adjacent_moe_exit,
    coin_flip_broadcast_entry,
    coin_flip_broadcast_exit,
    transmit_adjacent_flip_entry,
    transmit_adjacent_flip_exit,
    upcast_validity_entry,
    upcast_validity_exit,
    broadcast_validity_entry,
    broadcast_validity_exit,
    transmit_adjacent_state_entry,
    transmit_adjacent_state_exit,
    merge_initial_entry,
    merge_initial_exit,
    merge_final_entry,
    merge_final_exit,
)

from baseline.shared import Procedure, TransmissionRound, EdgeState, Stage, Flip


class MSTNetwork(Network):
    def __init__(self, verbose: bool = False, seed: int = None):
        super().__init__(verbose)

        if seed is not None:
            random.seed(seed)
            numpy.random.seed(seed)

    def initalize_random_diameter_3_network(self, n: int):
        G = None

        while True:
            # Randomly sample p between 0 and 1
            p = random.uniform(0, 1)

            # Generate a random graph with sampled p
            G = nx.fast_gnp_random_graph(n, p)

            if not nx.is_connected(G):
                continue

            if nx.diameter(G) == 3:
                edges = list(G.edges())
                random_weights = random.sample(
                    range(1, len(edges) + 100), len(edges)
                )  # Generate distinct weights
                weighted_edges = [
                    (u, v, {"weight": w}) for (u, v), w in zip(edges, random_weights)
                ]
                G.add_edges_from(weighted_edges)
                break

        self.load_networkx_graph(G)

    def initalize_random_network(self, n: int):
        G = None
        connected = False

        while not connected:
            m = random.randint(n - 1, int(((n * (n - 1)) / 2)))
            G = nx.gnm_random_graph(n, m)

            if nx.is_connected(G):
                connected = True

        # Assign unique random weights to edges
        unique_weights = random.sample(
            range(1, G.number_of_edges() + 100), G.number_of_edges()
        )
        for i, (u, v) in enumerate(G.edges()):
            G.edges[u, v]["weight"] = unique_weights[i]

        self.load_networkx_graph(G)

    def load_networkx_graph(self, G: nx.Graph):
        # Create a mapping of networkx nodes to ExampleNode instances
        id_to_node = {}

        n = G.number_of_nodes()

        # Create ExampleNode objects for each node in the networkx graph
        for node_id in G.nodes:
            node = MSTNode(
                node_id,
                i=0,
                n=n,
                fragment_id=node_id,
                root=True,
                verbose=self.verbose,
            )
            id_to_node[node_id] = node

        # Add nodes to the Network
        for node in id_to_node.values():
            self.add_node(node)

        # Add edges to the Network
        for node1_id, node2_id, edge_data in G.edges(data=True):
            if "weight" not in edge_data:
                raise KeyError("The 'weight' key is missing from edge_data")

            weight = edge_data["weight"]

            self.add_edge(
                id_to_node[node1_id],
                id_to_node[node2_id],
                weight=weight,
                state=EdgeState.BASIC,
            )

    def to_networkx(self):
        nx_graph = nx.Graph()

        # Add nodes to the networkx graph
        for node in self.nodes:
            nx_graph.add_node(node.node_id)

        # Add edges to the networkx graph
        for edge in self.edges:
            node1, node2, attribtues = edge
            nx_graph.add_edge(node1.node_id, node2.node_id, weight=attribtues["weight"])

        return nx_graph

    def visualize_network(self, filename="network_visualization.png", mst_edges=None):
        nx_graph = self.to_networkx()

        pos = nx.spring_layout(nx_graph, seed=44)  # Layout for visualization
        weights = nx.get_edge_attributes(nx_graph, "weight")

        plt.figure(figsize=(10, 7))
        nx.draw(
            nx_graph,
            pos,
            with_labels=True,
            node_color="skyblue",
            node_size=500,
            font_size=10,
            font_weight="bold",
            edge_color="gray",
        )

        if mst_edges:
            # Highlight MST edges
            nx.draw_networkx_edges(
                nx_graph,
                pos,
                edgelist=mst_edges,
                width=3,
                edge_color="red",
                # style="dashed",
            )

        nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=weights, font_size=8)
        plt.title("Network Visualization", fontsize=14)
        plt.savefig(filename)
        plt.close()

    def get_mst(self):
        nx_graph = self.to_networkx()
        ground_truth = nx.minimum_spanning_tree(nx_graph)
        ground_truth = sorted(list(ground_truth.edges()))
        ground_truth = sorted([tuple(sorted(edge)) for edge in ground_truth])

        mst_edges = []

        for node in self.nodes:
            for port, attributes in node.ports.items():
                state = attributes.get("state")
                if state == EdgeState.BRANCH:
                    mst_edges.append(
                        tuple(sorted((node.node_id, attributes["destination"].node_id)))
                    )

        mst_edges = sorted(list(set(mst_edges)))
        mst_edges = sorted([tuple(sorted(edge)) for edge in mst_edges])
        return mst_edges, ground_truth

    def get_max_rounds(self):
        return max([node.rounds for node in self.nodes])

    def get_max_awake_rounds(self):
        return max([node.awake_rounds for node in self.nodes])


class MSTNode(Node):

    def __init__(
        self,
        node_id,
        i: int,
        n: int,
        fragment_id,
        root: bool = False,
        verbose: bool = False,
    ):
        super().__init__(node_id, verbose)
        self.parent_port: int = None
        self.child_ports: list[int] = []
        self.i: int = i  # Distance to the root
        self.n: int = n  # Total number of nodes
        self.root: bool = root  # Whether this node is the root
        self.schedule = deque()  # Transmission schedule queue
        self.stage: Stage = Stage.FIND_MOE
        self.fragment_id = fragment_id

        # Procedure-specific fields
        self.broadcast_message = None  # Value being broadcasted
        self.upcast_value: int = None  # Value being upcasted
        self.neighbor_message = None
        self.adjacent_message = None

        self.procedures = {
            Procedure.FRAGMENT_BROADCAST: self._fragment_broadcast_handler,
            Procedure.UPCAST_MIN: self._upcast_min_handler,
            Procedure.TRANSMIT_NEIGHBOR: self._transmit_neighbor_handler,
            Procedure.TRANSMIT_ADJACENT: self._transmit_adjacent_handler,
            Procedure.MERGE_UP: self._merge_up_handler,
            Procedure.MERGE_DOWN: self._merge_down_handler,
        }

        self.received_neighbor_messages = {}  # Dictionary with ports as keys
        self.fragment_flip: Flip = None
        self.local_moe_port: int = None  # Port ID of the local MOE
        self.is_fragment_moe: bool = False  # Boolean flag for fragment MOE
        self.valid_moe: bool = False
        self.new_fragment_id: int = None
        self.new_level_num: int = None
        self.new_parent_port: int = None
        self.new_child_ports: list[int] = []
        self.adjacent_moe = {}
        self.adjacent_flip = {}

    fragment_broadcast = fragment_broadcast
    _fragment_broadcast_handler = _fragment_broadcast_handler
    upcast_min = upcast_min
    _upcast_min_handler = _upcast_min_handler
    transmit_neighbor = transmit_neighbor
    _transmit_neighbor_handler = _transmit_neighbor_handler
    transmit_adjacent = transmit_adjacent
    _transmit_adjacent_handler = _transmit_adjacent_handler
    merge_up = merge_up
    _merge_up_handler = _merge_up_handler
    merge_down = merge_down
    _merge_down_handler = _merge_down_handler

    find_moe_entry = find_moe_entry
    upcast_moe_entry = upcast_moe_entry
    upcast_moe_exit = upcast_moe_exit
    broadcast_moe_entry = broadcast_moe_entry
    broadcast_moe_exit = broadcast_moe_exit
    transmit_adjacent_moe_entry = transmit_adjacent_moe_entry
    transmit_adjacent_moe_exit = transmit_adjacent_moe_exit
    coin_flip_broadcast_entry = coin_flip_broadcast_entry
    coin_flip_broadcast_exit = coin_flip_broadcast_exit
    transmit_adjacent_flip_entry = transmit_adjacent_flip_entry
    transmit_adjacent_flip_exit = transmit_adjacent_flip_exit
    upcast_validity_entry = upcast_validity_entry
    upcast_validity_exit = upcast_validity_exit
    broadcast_validity_entry = broadcast_validity_entry
    broadcast_validity_exit = broadcast_validity_exit
    transmit_adjacent_state_entry = transmit_adjacent_state_entry
    transmit_adjacent_state_exit = transmit_adjacent_state_exit
    merge_initial_entry = merge_initial_entry
    merge_initial_exit = merge_initial_exit
    merge_final_entry = merge_final_entry
    merge_final_exit = merge_final_exit

    def print_state(self):
        """Print the current state of the node."""
        self.logger.info("")

        self.logger.info(f"  Parent Port: {self.parent_port}")
        self.logger.info(f"  Child Ports: {self.child_ports}")
        self.logger.info(f"  Distance to Root (i): {self.i}")
        self.logger.info(f"  Root: {self.root}")
        self.logger.info(f"  Fragment ID: {self.fragment_id}")
        self.logger.info(f"  Edge State:")
        for port, attributes in self.ports.items():
            state = attributes.get("state")
            self.logger.info(f"    Port: {port}, State: {state}")

    def handle_stage(
        self,
        stage,
        next_stage,
        round_number,
        entry_logic=None,
        exit_logic=None,
    ):
        if not self.schedule:
            if entry_logic:
                entry_logic(round_number)
            return

        # Handle the current schedule item
        _, procedure, phase = self.schedule.popleft()

        if phase == TransmissionRound.END:
            self.logger.info(
                "Stage %s completed. Executing exit logic and transitioning to %s.",
                stage,
                next_stage,
            )

            if exit_logic:
                exit_logic()

            self.stage = next_stage
            return

        if procedure in self.procedures:
            self.procedures[procedure](phase)
        else:
            self.logger.info("No handler for procedure %s.", procedure.value)

        # Schedule the next wake-up
        if self.schedule:
            next_round, _, _ = self.schedule[0]
            self.sleep(next_round)

    def _compute(self, round_number: int):
        """Execute the current phase and schedule the next wake-up."""
        if self.stage == Stage.TERMINATED:
            self.logger.info("TERMINATED")
            return

        if self.stage == Stage.FIND_MOE:
            self.handle_stage(
                stage=Stage.FIND_MOE,
                next_stage=Stage.UPCAST_MOE,
                entry_logic=self.find_moe_entry,
                round_number=round_number,
            )

        if self.stage == Stage.UPCAST_MOE:
            self.handle_stage(
                stage=Stage.UPCAST_MOE,
                next_stage=Stage.BROADCAST_MOE,
                entry_logic=self.upcast_moe_entry,
                exit_logic=self.upcast_moe_exit,
                round_number=round_number,
            )

        if self.stage == Stage.BROADCAST_MOE:
            self.handle_stage(
                stage=Stage.BROADCAST_MOE,
                next_stage=Stage.TRANSMIT_ADJACENT_MOE,
                round_number=round_number,
                entry_logic=self.broadcast_moe_entry,
                exit_logic=self.broadcast_moe_exit,
            )

        if self.stage == Stage.TRANSMIT_ADJACENT_MOE:
            self.handle_stage(
                stage=Stage.TRANSMIT_ADJACENT_MOE,
                next_stage=Stage.COIN_FLIP_BROADCAST,
                round_number=round_number,
                entry_logic=self.transmit_adjacent_moe_entry,
                exit_logic=self.transmit_adjacent_moe_exit,
            )

        if self.stage == Stage.COIN_FLIP_BROADCAST:
            self.handle_stage(
                stage=Stage.COIN_FLIP_BROADCAST,
                next_stage=Stage.TRANSMIT_ADJACENT_FLIP,
                round_number=round_number,
                entry_logic=self.coin_flip_broadcast_entry,
                exit_logic=self.coin_flip_broadcast_exit,
            )

        if self.stage == Stage.TRANSMIT_ADJACENT_FLIP:
            self.handle_stage(
                stage=Stage.TRANSMIT_ADJACENT_FLIP,
                next_stage=Stage.UPCAST_VALIDITY,
                round_number=round_number,
                entry_logic=self.transmit_adjacent_flip_entry,
                exit_logic=self.transmit_adjacent_flip_exit,
            )

        if self.stage == Stage.UPCAST_VALIDITY:
            self.handle_stage(
                stage=Stage.UPCAST_VALIDITY,
                next_stage=Stage.BROADCAST_VALIDITY,
                round_number=round_number,
                entry_logic=self.upcast_validity_entry,
                exit_logic=self.upcast_validity_exit,
            )

        if self.stage == Stage.BROADCAST_VALIDITY:
            self.handle_stage(
                stage=Stage.BROADCAST_VALIDITY,
                next_stage=Stage.TRANSMIT_ADJACENT_STATE,
                round_number=round_number,
                entry_logic=self.broadcast_validity_entry,
                exit_logic=self.broadcast_validity_exit,
            )

        if self.stage == Stage.TRANSMIT_ADJACENT_STATE:
            self.handle_stage(
                stage=Stage.TRANSMIT_ADJACENT_STATE,
                next_stage=Stage.MERGE_INITIAL,
                round_number=round_number,
                entry_logic=self.transmit_adjacent_state_entry,
                exit_logic=self.transmit_adjacent_state_exit,
            )

        if self.stage == Stage.MERGE_INITIAL:
            self.handle_stage(
                stage=Stage.MERGE_INITIAL,
                next_stage=Stage.MERGE_FINAL,
                round_number=round_number,
                entry_logic=self.merge_initial_entry,
                exit_logic=self.merge_initial_exit,
            )

        if self.stage == Stage.MERGE_FINAL:
            self.handle_stage(
                stage=Stage.MERGE_FINAL,
                next_stage=Stage.FIND_MOE,
                round_number=round_number,
                entry_logic=self.merge_final_entry,
                exit_logic=self.merge_final_exit,
            )
