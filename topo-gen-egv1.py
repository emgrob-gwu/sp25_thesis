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
        #G[u][v]is networkx.Graph datatype, returns dictionary of attributes for each node
    #G.add_edge('A', 'B', weight=random.randint(1, 100))
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

def saveTopology_old(G, outputFile): #using networkx package
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)
    edge_labels = {(u,v): G[u][v]['weight'] for u,v in G.edges()} #add weight for each node pair
    nx.draw(G, pos, with_labels=True, node_color='gray', edge_color='gray', node_size=500) #draw graph

    cpu_labels = {node: f"CPU: {G.nodes[node]['CPU']}" for node in G.nodes()}
    print(cpu_labels)
    nx.draw_networkx_edge_labels(G, pos, labels=cpu_labels, edge_labels=edge_labels, font_color='pink') #add edge weights (latency) 
    plt.savefig(outputFile, format="pdf")
    plt.close()

def saveTopology(G, outputFile): #added different colors
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G,seed=42)
    edge_labels = {(u, v): G[u][v]['weight'] for u, v in G.edges()} 

    node_colors = []
    for node in G.nodes():
        if isinstance(node, str) and node.isalpha():  
            node_colors.append('red')  
        else:
            node_colors.append('gray') 

    cpu_labels = {node: f"CPU: {G.nodes[node]['CPU']}" for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=cpu_labels, font_color='blue', font_size=10, verticalalignment='bottom')

    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=500)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='pink')  

    plt.savefig(outputFile, format="pdf")
    plt.close()


def saveTopo_manual(outputFile, numNodes, numLinks): #without networkx
    links = set()
    nodes = {i: (random.uniform(0, 10), random.uniform(0, 10)) for i in range(1, numNodes + 1)} #init node x,y positions, todo: change into a set? to avoid duplicate positions

    while len(links) < numLinks:
        n1, n2 = random.sample(range(1, numNodes +1), 2)
        if (n1, n2) not in links and (n2, n1) not in links:
            links.add((n1, n2))
    fig, ax = plt.subplots()
    for n1, n2 in links:
        x_vals = [nodes[n1][0], nodes[n2][0]]
        y_vals = [nodes[n1][1], nodes[n2][1]]
        ax.plot(x_vals, y_vals, '-k')
    for n, (x,y) in nodes.items(): 
        ax.plot(x,y, "or", ms=10, mfc="red", mec="black", mew=2)
    ax.set_xlim([-1, 11])
    ax.set_ylim([-1, 11])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid()
    
    pdf = PdfPages(outputFile + ".pdf")
    pdf.savefig(fig)
    pdf.close()
     
def place_single_node(G, new_node_name, numNodes): #currently integrates one node into existing topography (just renames existing node)
    node = random.sample(range(1,numNodes+1), 1)
    temp = node[0]
    mapping ={temp:new_node_name}
    G = nx.relabel_nodes(G, mapping)
    return G


def place_topology(G, new_topo, numNodes): #integrates new topology onto existing network 
    mapping = {}

    #new_topo is a networkx datatype
    existing_nodes = np.arange(1, numNodes+1)
    for node in new_topo.nodes:
        if(len(existing_nodes) ==0):
            break
        node_to_rename = np.random.choice(existing_nodes)
        new_name = new_topo.nodes[node].get("label", node)
        mapping[node_to_rename] = new_name

        #CPU update:
        if G.nodes[node_to_rename]['CPU'] >0: #CPU cannot go below 0
            G.nodes[node_to_rename]['CPU']-=1 #decrease CPU by one for each node (can change this)
        #existing_nodes=np.delete(existing_nodes,node_to_replace-1)
        existing_nodes=np.delete(existing_nodes,np.where(existing_nodes== node_to_rename))

    G=nx.relabel_nodes(G, mapping)
    return G
    



def main():
    #config = readConfig("sample-config_copy")
    with open("sample-config_copy", 'r') as cFile:
        config = json.load(cFile)
    numNodes = int(config["numNodes"])
    numLinks = int(config["numLinks"])
    
    G = generateTopology(numNodes, numLinks)
    saveTopology(G, "topology.pdf")
    saveTopo_manual("topology_manual", numNodes, numLinks)
    print("Topology saved to topology.pdf")
    new_node = 'test'
    #G =place_single_node(G,new_node, numNodes)
    
    new_topo = generateTopology_new(numNodes, numLinks) #new topo to be placed
    G = place_topology(G, new_topo, 3)
    saveTopology(G, "topology_after.pdf")

if __name__ == "__main__":
    main()
