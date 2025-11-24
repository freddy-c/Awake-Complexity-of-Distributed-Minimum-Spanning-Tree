import os
import random
import networkx as nx
import matplotlib.pyplot as plt

from baseline.main import MSTNetwork as BaselineMSTNetwork
from optimized.main import MSTNetwork as OptimizedMSTNetwork


def generate_graph(n):
    while True:
        p = random.uniform(0, 1)
        G = nx.fast_gnp_random_graph(n, p)
        if not nx.is_connected(G):
            continue
        if nx.diameter(G) == 3:
            edges = list(G.edges())
            random_weights = random.sample(range(1, len(edges) + 100), len(edges))
            weighted_edges = [
                (u, v, {"weight": w}) for (u, v), w in zip(edges, random_weights)
            ]
            G.add_edges_from(weighted_edges)
            return G
        

def save_graph(G, title="Graph", filename="graph.png", mst_edges=None):
    num_nodes = G.number_of_nodes()

    # Dynamic layout spread and figure size
    if num_nodes <= 10:
        k = 0.8
        fig_size = 6
        node_size = 800
        font_size = 12
        edge_label_font_size = 10
    else:
        k = 1.5 / (num_nodes ** 0.5)
        fig_size = min(0.35 * num_nodes + 4, 20)  # nonlinear scale
        node_size = max(300, 800 - num_nodes * 5)
        font_size = max(6, 12 - num_nodes // 10)
        edge_label_font_size = max(5, 10 - num_nodes // 10)

    pos = nx.spring_layout(G, seed=42, k=k)
    plt.figure(figsize=(fig_size, fig_size))

    if mst_edges:
        mst_edge_set = set((min(u, v), max(u, v)) for u, v in mst_edges)
        edge_colors = [
            "red" if (min(u, v), max(u, v)) in mst_edge_set else "lightgray"
            for u, v in G.edges()
        ]
        widths = [
            2.5 if (min(u, v), max(u, v)) in mst_edge_set else 1
            for u, v in G.edges()
        ]
    else:
        edge_colors = "black"
        widths = 1

    weights = nx.get_edge_attributes(G, "weight")

    nx.draw(
        G,
        pos,
        with_labels=True,
        edge_color=edge_colors,
        width=widths,
        node_size=node_size,
        font_size=font_size,
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels=weights, font_size=edge_label_font_size)
    plt.title(title)
    plt.savefig(filename, bbox_inches="tight")
    plt.clf()
    plt.close()




def run_simulation(network_class, graph, label):
    network = network_class(seed=42)
    network.load_networkx_graph(graph)
    network.simulate_rounds()

    dist_mst, ground_truth = network.get_mst()
    assert dist_mst == ground_truth


    max_rounds = network.get_max_rounds()
    max_awake_rounds = network.get_max_awake_rounds()

    print(f"{label} Results".center(60, "="))
    print(f"✅ {label}: Distributed MST matches the ground truth MST.")
    print(f"Max awake rounds : {max_awake_rounds}")
    print(f"Max total rounds : {max_rounds}")

    return dist_mst, max_rounds, max_awake_rounds


def main():
    os.system("clear")

    while True:
        user_input = input("Enter number of nodes for the graph (or 'q' to quit): ").strip().lower()
        if user_input == "q":
            print("Exiting.")
            break
        try:
            n = int(user_input)
            if n < 5:
                raise ValueError("The number of nodes in the graph must be at least 5.")
            
            os.system("clear")
        except ValueError as e:
            print(f"Invalid input: {e}")
            continue

        print(f"\nGenerating graph with diameter 3 and {n} nodes...")
        graph = generate_graph(n)
        print("Graph generated successfully!")

        # Compute MST from NetworkX for overlay
        nx_mst_edges = list(nx.minimum_spanning_edges(graph, algorithm="kruskal", data=False))
        save_graph(
            graph,
            title="Initial Graph with NetworkX MST",
            filename="./output/initial_graph.png",
            mst_edges=nx_mst_edges
        )
        print("Initial graph with NetworkX MST saved to ./output/initial_graph.png")

        input("Press Enter to run MST simulations...")

        # Run simulations
        baseline_mst, baseline_max_rounds, baseline_max_awake_rounds = run_simulation(
            BaselineMSTNetwork, graph, "Baseline"
        )
        optimized_mst, optimized_max_rounds, optimized_max_awake_rounds = run_simulation(
            OptimizedMSTNetwork, graph, "Optimized"
        )

        # Differences
        awake_diff = baseline_max_awake_rounds - optimized_max_awake_rounds
        rounds_diff = baseline_max_rounds - optimized_max_rounds
        awake_factor = (
            optimized_max_awake_rounds / baseline_max_awake_rounds
            if optimized_max_awake_rounds else float("inf")
        )
        rounds_factor = (
            baseline_max_rounds / optimized_max_rounds
            if optimized_max_rounds else float("inf")
        )

        print("Comparison Summary".center(60, "="))
        print(f"Awake rounds saved : {awake_diff}")
        print(f"Factor slowdown : {awake_factor:.2f}x")
        print(f"Total rounds saved : {rounds_diff}")
        print(f"Factor improvement : {rounds_factor:.2f}x")
        print("=" * 60)

        # Save MSTs overlaid on the original graph
        save_graph(
            graph,
            title="Baseline MST",
            filename="./output/baseline_mst.png",
            mst_edges=baseline_mst
        )
        save_graph(
            graph,
            title="Optimized MST",
            filename="./output/optimized_mst.png",
            mst_edges=optimized_mst
        )
        print("MST visualizations saved: ./output/baseline_mst.png, ./output/optimized_mst.png")

        print("\nReady for another run.")



if __name__ == "__main__":
    main()