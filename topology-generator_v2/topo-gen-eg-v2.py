import json
import random
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


def generateTopology(numNodes, numLinks):
    """Generates a network topology with random CPU values on nodes and bandwidth on edges."""
    G = nx.Graph()
    G.add_nodes_from(range(1, numNodes + 1))

    while len(G.edges) < numLinks:
        n1, n2 = random.sample(range(1, numNodes + 1), 2)
        if not G.has_edge(n1, n2):
            G.add_edge(n1, n2)

    for u, v in G.edges():
        G[u][v]['bandwidth'] = random.randint(10, 100)  # Assign random bandwidth

   # for node in G.nodes():
   #     G.nodes[node]['CPU'] = random.randint(1, 10)  # Assign random CPU

    return G


def generateTopology_new(numNodes, numLinks):
    """Generates a new topology to be placed onto the original network."""
    G = nx.Graph()
    node_labels = [chr(65 + i) if i < 26 else chr(65 + (i // 26) - 1) + chr(65 + (i % 26)) for i in range(numNodes)]
    G.add_nodes_from(node_labels)

    while len(G.edges) < numLinks:
        n1, n2 = random.sample(node_labels, 2)
        if not G.has_edge(n1, n2):
            G.add_edge(n1, n2)

    return G


def saveTopology(G, outputFile, placed_nodes=None, placed_edges=None):
    """Saves the topology as a PDF with different colors for placed nodes and edges."""
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)

    #edge_labels = { (u,v): f"{G[u][v]['bandwidth']}ms, {G[u][v]['bandwidth']}Gbps" for u, v in G.edges() }
    edge_labels = {(u, v): f"{G[u][v].get('bandwidth', 'N/A')} Mbps" for u, v in G.edges()}

    # Ensure placed_nodes and placed_edges are valid lists (default to empty)
    placed_nodes = placed_nodes if placed_nodes is not None else []
    #print(placed_nodes)
    placed_edges = placed_edges if placed_edges is not None else []

    # Separate edges into gray (original) and red (placed)
    gray_edges = [edge for edge in G.edges() if edge not in placed_edges]
    red_edges = placed_edges

    # Node colors: Red for placed nodes, gray for original nodes
    node_colors = ['red' if node in placed_nodes else 'gray' for node in G.nodes()]

    # Draw the network
    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=500)  # Original network in gray
    nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='red', width=2)  # Highlight placed edges in red
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='blue', font_size=8)

    # Add labels
   # cpu_labels = {node: f"CPU: {G.nodes[node].get('CPU', 'N/A')}" for node in G.nodes()}
    #nx.draw_networkx_labels(G, pos, labels=cpu_labels, font_color='blue', font_size=10, verticalalignment='bottom')
    plt.savefig(outputFile, format="pdf")
    plt.close()



def generate_all_possible_placements(G, new_topo):
    """Generate all possible placements of new_topo onto G using existing connections."""
    from itertools import permutations

    new_topo_nodes = list(new_topo.nodes())
    new_topo_edges = list(new_topo.edges())

    G_nodes = list(G.nodes())

    # Generate all possible mappings
    for idx, perm in enumerate(permutations(G_nodes, len(new_topo_nodes))):
        mapping = {new_topo_nodes[i]: perm[i] for i in range(len(new_topo_nodes))}

        # Ensure all mapped nodes exist before accessing them
        if any(node not in mapping for node in new_topo_nodes):
            continue  # Skip if mapping is incomplete

        # Determine placed nodes
        placed_nodes = list(mapping.values())

        # Determine placed edges using existing paths
        placed_edges = []
        for u, v in new_topo_edges:
            mapped_u, mapped_v = mapping[u], mapping[v]
            if nx.has_path(G, mapped_u, mapped_v):  # Ensure a path exists
                shortest_path = nx.shortest_path(G, mapped_u, mapped_v)  # Find shortest existing path
                placed_edges.extend(zip(shortest_path[:-1], shortest_path[1:]))  # Add path edges

        # Save possibility
        saveTopology(G, f"possibility_{idx + 1}.pdf", placed_nodes, placed_edges)




def main():
    # Read config
    with open("sample-config_copy", 'r') as cFile:
        config = json.load(cFile)
    
    numNodes = int(config["numNodes"])
    numLinks = int(config["numLinks"])
    
    # Generate and save the original network
    G = generateTopology(numNodes, numLinks)
    saveTopology(G, "original_network.pdf")
    
    # Generate and save the topology to be placed
    new_topo = generateTopology_new(3, 3)
    saveTopology(new_topo, "placed_topo.pdf", placed_nodes=new_topo.nodes())
    
    # Generate and save all possible placements
    generate_all_possible_placements(G, new_topo)


if __name__ == "__main__":
    main()
