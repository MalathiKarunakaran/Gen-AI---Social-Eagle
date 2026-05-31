import os
import json
import networkx as nx
import matplotlib.pyplot as plt

print("🚀 Starting GraphRAG Step 3: Local Graph Ingestion & Mapping...")

# 1. Load our compiled relationship dataset from Step 2
if not os.path.exists("graph_data.json"):
    print("❌ ERROR: Cannot find 'graph_data.json'. Please run graph_step2.py first!")
    exit()

with open("graph_data.json", "r", encoding="utf-8") as f:
    triplets = json.load(f)

print(f"📥 Loaded {len(triplets)} relationship pairs from memory storage.")

# 2. Instantiate a blank Directed Graph object (DiGraph)
# Directed graphs ensure connections have strict directions (e.g., A implies B)
G = nx.DiGraph()

# 3. Step through your triplets and append them into the Graph Architecture
for item in triplets:
    source = item["source"]
    target = item["target"]
    relation = item["relation"]
    
    # Add nodes and connect them with an edge containing the relationship attribute
    G.add_edge(source, target, label=relation)

print(f"✅ Graph Storage Loaded. Total Entities (Nodes): {G.number_of_nodes()}, Total Links (Edges): {G.number_of_edges()}")

# 4. Generate visual layout coordinates for rendering
print("🎨 Rendering visual graph blueprint window...")
plt.figure(figsize=(12, 8))

# Using spring_layout to push unconnected components away and pull links together organically
pos = nx.spring_layout(G, k=1.5, seed=42)

# Draw the underlying node circles
nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightblue")

# Draw the connection lines pointing from source to target
nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=15, edge_color="gray")

# Draw the text labels on top of the nodes
nx.draw_networkx_labels(G, pos, font_size=9, font_weight="bold")

# Extract edge attribute labels to display the RELATION strings on lines
edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, font_color="red")

plt.title("AI Trip Planner - Extracted Knowledge Graph Map", fontsize=14, fontweight="bold")
plt.axis("off") # Hide standard empty chart grids

print("📊 Displaying Graph Layout. (Close the pop-up window when finished to end the script)")
plt.show()

print("🏁 Step 3 Execution Finished Successfully.")