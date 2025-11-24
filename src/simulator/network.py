from typing import List, Tuple

from .node import Node


class Network:
    def __init__(self, verbose: bool = False):
        self.nodes: List[Node] = []  # List of Node instances
        self.edges: List[Tuple[Node, Node, dict]] = (
            []
        )  # List of edges as tuples (u, v, attributes)
        self.verbose = verbose

        self.phase_fragment_depths = []

    def add_node(self, node: Node):
        """Add a node to the network."""
        if node not in self.nodes:
            self.nodes.append(node)
        else:
            raise ValueError(f"Node {node.node_id} already exists in the network.")

    def add_edge(self, u: Node, v: Node, **attributes):
        """Add an edge between two nodes u and v with optional attributes."""
        if u not in self.nodes or v not in self.nodes:
            raise ValueError("Both nodes must exist in the network to create an edge.")

        edge = (u, v, attributes)
        if edge in self.edges or (v, u, attributes) in self.edges:
            raise ValueError(
                f"Edge between Node {u.node_id} and Node {v.node_id} already exists."
            )

        self.edges.append(edge)
        self.update_ports(u, v, attributes)

    def update_ports(self, u: Node, v: Node, attributes: dict):
        """Update the ports for the nodes when a new edge is added, with each node aware of the other's port."""

        # Assign port IDs for both nodes
        u_port_id = len(u.ports)
        v_port_id = len(v.ports)

        # Update node `u`'s ports
        u.ports[u_port_id] = {
            "destination": v,
            "destination_port": v_port_id,  # Store the port ID of the destination node
            **attributes,
        }

        # Update node `v`'s ports
        v.ports[v_port_id] = {
            "destination": u,
            "destination_port": u_port_id,  # Store the port ID of the other node
            **attributes,
        }

    def deliver_messages(self):
        """Merge the staging inbox into the inbox for all nodes."""
        for node in self.nodes:
            # Use list extend to append staging inbox messages to the main inbox
            node.inbox.extend(node.staging_inbox)

            # Clear the staging inbox after merging
            node.staging_inbox.clear()

    def simulate_rounds(self):
        """Simulate multiple synchronous communication rounds."""
        round_num = 1
        terminated = False

        while terminated is False:
            if self.verbose:
                print(f"\n--- Simulating Round {round_num} ---")

            # 1. Perform computation for all nodes
            for node in self.nodes:
                node.compute(round_number=round_num)

            # 2. Deliver messages from outboxes to inboxes
            self.deliver_messages()

            for node in self.nodes:
                node.finalize_sleep(round_num)

            terminated = True
            for node in self.nodes:
                if node.terminated is False:
                    terminated = False
                    break
                elif node.rounds == 0:
                    node.rounds = round_num

            round_num += 1
