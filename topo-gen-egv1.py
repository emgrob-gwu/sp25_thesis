import json
import random
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def readConfig(configFile):
    with open(configFile, "r") as f:
        return json.load(f)

def generateTopology(numNodes, numLinks):
    G=nx.Graph()
    G.add_nodes_from(range(1, numNodes + 1))

    while len(G.edges) < numLinks:
        n1, n2 = random.sample(range(1, numNodes + 1), 2)
        if not G.has_edge(n1, n2):
            G.add_edge(n1, n2)
    for u,v in G.edges():
        G[u][v]['weight'] = random.randint(1,100) #ms
    
    for node in G.nodes():
        G.nodes[node]['CPU'] = random.randint(1, 10)  # Assign random CPU

    return G

def generateTopology_new(numNodes, numLinks):
    G = nx.Graph()
    
    node_labels = [chr(65 + i) if i < 26 else chr(65 + (i // 26) - 1) + chr(65 + (i % 26)) for i in range(numNodes)]
    
    G.add_nodes_from(node_labels)

    while len(G.edges) < numLinks:
        n1, n2 = random.sample(node_labels, 2)  # Sample two distinct node names
        if not G.has_edge(n1, n2):
            G.add_edge(n1, n2)

    for u, v in G.edges():
        G[u][v]['weight'] = random.randint(1, 100)  # Assign random latency (ms)

    return G

def saveTopology(G, outputFile, isnetwork=1):
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    edge_labels = {(u, v): G[u][v]['weight'] for u, v in G.edges()} 

    node_colors = []
    for node in G.nodes():
        if isinstance(node, str) and node.isalpha():  
            node_colors.append('red')  
        else:
            node_colors.append('gray') 
    if(isnetwork==1):
        cpu_labels = {node: f"CPU: {G.nodes[node]['CPU']}" for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=cpu_labels, font_color='blue', font_size=10, verticalalignment='bottom')



    #cpu_labels = {node: f"CPU: {G.nodes[node]['CPU']}" for node in G.nodes()}
    #nx.draw_networkx_labels(G, pos, labels=cpu_labels, font_color='blue', font_size=10, verticalalignment='bottom')

    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=500)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='pink')  

    plt.savefig(outputFile, format="pdf")
    plt.close()

def place_topology(G, new_topo, numNodes):
    mapping = {}
    cpu_requirements = {}
    latency_requirements = {}

    existing_nodes = np.arange(1, numNodes+1)
    for node in new_topo.nodes:
        if len(existing_nodes) == 0:
            break
        node_to_rename = np.random.choice(existing_nodes)
        new_name = new_topo.nodes[node].get("label", node)
        mapping[node_to_rename] = new_name

        # CPU update and tracking
        original_cpu = G.nodes[node_to_rename]['CPU']
       # if original_cpu > 0:
       #     G.nodes[node_to_rename]['CPU'] -= 1
       #cpu_requirements[new_name] = original_cpu - G.nodes[node_to_rename]['CPU']
        cpu_requirements[new_name] = original_cpu

        existing_nodes = np.delete(existing_nodes, np.where(existing_nodes == node_to_rename))

    G = nx.relabel_nodes(G, mapping)

    # Latency requirement tracking
    for u, v in G.edges():
        if u in mapping.values() and v in mapping.values():
            latency = G[u][v]['weight']
            latency_requirements[(u, v)] = (latency, 1000)  # Range [latency, 1000]
    
    print("Inferred CPU Requirements:", cpu_requirements)
    print("Inferred Latency Requirements:", latency_requirements)
    
    return G

def main():
    with open("sample-config_copy", 'r') as cFile:
        config = json.load(cFile)
    numNodes = int(config["numNodes"])
    numLinks = int(config["numLinks"])
    
    G = generateTopology(numNodes, numLinks)
    saveTopology(G, "topology.pdf")
    
    new_topo = generateTopology_new(numNodes, numLinks) 
    saveTopology(new_topo, "placed.pdf", 0)
    G = place_topology(G, new_topo, 3)
    saveTopology(G, "topology_after.pdf")

if __name__ == "__main__":
    main()
