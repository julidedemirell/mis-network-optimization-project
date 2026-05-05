"""
E-Commerce Logistics Network Optimization
MIS Project - Shortest Path Problem

Problem: An Istanbul-based e-commerce company needs to determine the fastest
delivery routes from its central warehouse to two customer delivery zones,
passing through regional hubs and distribution centers.

--- Code Explanation ---
The graph was created using NetworkX as a Directed Graph (DiGraph).
Nodes represent physical locations in the Istanbul delivery network:
the central warehouse, regional hubs, distribution centers, and customer zones.
Edges represent direct road connections between these locations.
Each edge carries three attributes: travel_time_min (the primary optimization
weight), distance_km, and cost_usd.
The Dijkstra shortest path algorithm calculates the fastest possible delivery
route from the central warehouse to each customer zone, minimizing total
travel time in minutes.
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import os

# ─────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────

# Load the edge dataset from the CSV file.
# Each row represents a one-way connection between two locations.
# Columns: source node, target node, travel time (minutes), distance (km), cost (USD)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(BASE_DIR, "data", "network_data.csv")
df = pd.read_csv(data_path)

print("=" * 60)
print("NETWORK DATA LOADED")
print("=" * 60)
print(df.to_string(index=False))
print()

# ─────────────────────────────────────────
# 2. BUILD THE GRAPH
# ─────────────────────────────────────────

# We use a directed graph (DiGraph) because deliveries flow in one direction:
# from Warehouse → Hubs → Distribution Centers → Customer Zones.
# Each edge carries three attributes: travel_time, distance, and cost.

G = nx.DiGraph()

for _, row in df.iterrows():
    G.add_edge(
        row["source"],
        row["target"],
        travel_time_min=row["travel_time_min"],
        distance_km=row["distance_km"],
        cost_usd=row["cost_usd"]
    )

print(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
print(f"Nodes: {list(G.nodes())}")
print()

# ─────────────────────────────────────────
# 3. SHORTEST PATH ANALYSIS
# ─────────────────────────────────────────

# We apply Dijkstra's algorithm — the standard shortest path algorithm —
# to find the optimal route from the Warehouse to each Customer Zone.
# We optimize for travel_time_min as the primary decision criterion,
# since delivery speed is the top priority in e-commerce operations.

source_node = "Warehouse_Istanbul"
targets = ["Customer_Zone_A", "Customer_Zone_B"]

results = {}

print("=" * 60)
print("SHORTEST PATH RESULTS (optimized for travel time)")
print("=" * 60)

for target in targets:
    # nx.shortest_path uses Dijkstra's algorithm when weight is specified
    path = nx.shortest_path(G, source=source_node, target=target, weight="travel_time_min")
    length = nx.shortest_path_length(G, source=source_node, target=target, weight="travel_time_min")

    # Calculate total distance and cost along the optimal path
    total_distance = sum(G[path[i]][path[i+1]]["distance_km"] for i in range(len(path)-1))
    total_cost = sum(G[path[i]][path[i+1]]["cost_usd"] for i in range(len(path)-1))

    results[target] = {
        "path": path,
        "travel_time_min": length,
        "distance_km": total_distance,
        "cost_usd": total_cost
    }

    print(f"\nTarget: {target}")
    print(f"  Optimal Route : {' → '.join(path)}")
    print(f"  Travel Time   : {length} minutes")
    print(f"  Total Distance: {total_distance} km")
    print(f"  Total Cost    : ${total_cost}")

# ─────────────────────────────────────────
# 4. NETWORK VISUALIZATION
# ─────────────────────────────────────────

# We draw the full network and highlight the two optimal delivery paths.
# Node colors indicate the role of each location in the supply chain:
#   - Red    : Central Warehouse (source)
#   - Orange : Regional Hubs (intermediate relay points)
#   - Blue   : Distribution Centers (last-mile entry points)
#   - Green  : Customer Zones (destinations)

# Define positions manually for a clean left-to-right flow layout
pos = {
    "Warehouse_Istanbul":   (0, 2),
    "Hub_Kadikoy":          (2, 3),
    "Hub_Besiktas":         (2, 2),
    "Hub_Sisli":            (2, 1),
    "Distribution_Atasehir":(4, 3.5),
    "Distribution_Maltepe": (4, 2.5),
    "Distribution_Sariyer": (4, 1.5),
    "Distribution_Kagithane":(4, 0.8),
    "Distribution_Eyup":    (4, 0.1),
    "Customer_Zone_A":      (6, 3),
    "Customer_Zone_B":      (6, 1),
}

# Assign colors by node type
node_colors = []
for node in G.nodes():
    if "Warehouse" in node:
        node_colors.append("#e74c3c")
    elif "Hub" in node:
        node_colors.append("#e67e22")
    elif "Distribution" in node:
        node_colors.append("#3498db")
    else:
        node_colors.append("#2ecc71")

fig, ax = plt.subplots(figsize=(16, 9))
ax.set_facecolor("#f8f9fa")
fig.patch.set_facecolor("#f8f9fa")

# Draw all edges (base network in light gray)
nx.draw_networkx_edges(
    G, pos, ax=ax,
    edge_color="#cccccc", arrows=True,
    arrowstyle="-|>", arrowsize=20,
    width=1.5, connectionstyle="arc3,rad=0.1"
)

# Highlight shortest paths with distinct colors
path_colors = {"Customer_Zone_A": "#e74c3c", "Customer_Zone_B": "#8e44ad"}

for target, color in path_colors.items():
    path = results[target]["path"]
    path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
    nx.draw_networkx_edges(
        G, pos, edgelist=path_edges, ax=ax,
        edge_color=color, arrows=True,
        arrowstyle="-|>", arrowsize=25,
        width=3.5, connectionstyle="arc3,rad=0.1"
    )

# Draw nodes
nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=1800)

# Draw labels with clean formatting
labels = {n: n.replace("_", "\n") for n in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=7, font_weight="bold")

# Draw edge weight labels (travel time)
edge_labels = {(u, v): f"{d['travel_time_min']}min" for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(
    G, pos, edge_labels=edge_labels, ax=ax,
    font_size=6.5, label_pos=0.35
)

# Legend
legend_elements = [
    mpatches.Patch(color="#e74c3c", label="Warehouse (Source)"),
    mpatches.Patch(color="#e67e22", label="Regional Hub"),
    mpatches.Patch(color="#3498db", label="Distribution Center"),
    mpatches.Patch(color="#2ecc71", label="Customer Zone"),
    mpatches.Patch(color="#e74c3c", label="Shortest Path → Zone A"),
    mpatches.Patch(color="#8e44ad", label="Shortest Path → Zone B"),
]
ax.legend(handles=legend_elements, loc="lower left", fontsize=9, framealpha=0.9)

ax.set_title(
    "E-Commerce Logistics Network — Shortest Path Optimization\n"
    "Istanbul Delivery Network (edge labels = travel time in minutes)",
    fontsize=13, fontweight="bold", pad=15
)
ax.axis("off")
plt.tight_layout()

results_dir = os.path.join(BASE_DIR, "results")
os.makedirs(results_dir, exist_ok=True)
viz_path = os.path.join(results_dir, "network_visualization.png")
plt.savefig(viz_path, dpi=150, bbox_inches="tight")
print(f"\nVisualization saved to: {viz_path}")
plt.close()

# ─────────────────────────────────────────
# 5. SAVE OUTPUT SUMMARY
# ─────────────────────────────────────────

output_path = os.path.join(results_dir, "solution_output.txt")
with open(output_path, "w") as f:
    f.write("E-COMMERCE LOGISTICS NETWORK OPTIMIZATION\n")
    f.write("Shortest Path Analysis Results\n")
    f.write("=" * 60 + "\n\n")
    for target, res in results.items():
        f.write(f"Target: {target}\n")
        f.write(f"  Route        : {' → '.join(res['path'])}\n")
        f.write(f"  Travel Time  : {res['travel_time_min']} minutes\n")
        f.write(f"  Distance     : {res['distance_km']} km\n")
        f.write(f"  Cost         : ${res['cost_usd']}\n\n")
    f.write("\nManagerial Interpretation\n")
    f.write("-" * 60 + "\n")
    f.write(
        "The shortest path algorithm reveals that both customer zones can be\n"
        "reached within 53-63 minutes from the central warehouse. Zone A is best\n"
        "served via the Kadikoy hub route, while Zone B benefits from the Sisli-\n"
        "Kagithane corridor. Management should prioritize maintaining capacity on\n"
        "these two critical corridors and consider buffer routing through Besiktas\n"
        "during peak hours to avoid bottlenecks.\n"
    )

print(f"Solution output saved to: {output_path}")
print("\nDone! All results generated successfully.")
