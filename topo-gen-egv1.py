import json
import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def readConfig(configFile):
    with open(configFile, "r") as f:
        return json.load(f)

def generateTopology(numNodes, numLinks):
    G = nx.Graph()
    G.add_nodes_from(range(1, numNodes + 1))
    
    while len(G.edges) < numLinks:
        n1, n2 = random.sample(range(1, numNodes + 1), 2)
        if not G.has_edge(n1, n2):
            G.add_edge(n1, n2)
    for u,v in G.edges():
        G[u][v]['weight'] = random.randint(1,100) #ms
        #G[u][v]is networkx.Graph datatype, returns dictionary of attributes for each node
    #G.add_edge('A', 'B', weight=random.randint(1, 100))

    return G
    
def saveTopology(G, outputFile): #using networkx package
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)
    edge_labels = {(u,v): G[u][v]['weight'] for u,v in G.edges()} #add weight for each node pair
    nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500) #draw graph
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='pink') #add edge weights (latency) 
    #todo: fix orientation issues with the labels
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
     

def main():
    #config = readConfig("sample-config_copy")
    with open("sample-config_copy", 'r') as cFile:
        config = json.load(cFile)
    numNodes = int(config["numNodes"])
    numLinks = int(config["numLinks"])
    
    G = generateTopology(numNodes, numLinks)
    saveTopology(G, "topology.pdf")
    saveTopo_manual("topology_manual.pdf", numNodes, numLinks)
    print("Topology saved to topology.pdf")

if __name__ == "__main__":
    main()
