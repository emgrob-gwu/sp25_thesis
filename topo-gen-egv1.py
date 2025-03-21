import json
import random
import networkx as nx
import matplotlib.pyplot as plt

def generate_fixed_topology(numNodes, numLinks):
    G = nx.Graph()
    G.add_nodes_from(range(1, numNodes + 1))
    
    while len(G.edges) < numLinks:
        n1, n2 = random.sample(range(1, numNodes + 1), 2)
        if not G.has_edge(n1, n2):
            G.add_edge(n1, n2)
    
    for u in G.nodes():
        G.nodes[u]['CPU'] = 0  # Initialize CPU resources to zero
    
    for u, v in G.edges():
        G[u][v]['bandwidth'] = 0  # Initialize bandwidth to zero
    
    return G

def generate_service_instance():
    service_type = random.choice(['star', 'clique'])
    G = nx.Graph()
    
    if service_type == 'star':
        center = 'S1'
        nodes = ['S2', 'S3', 'S4', 'S5']
        G.add_node(center, CPU=2)
        for node in nodes:
            G.add_node(node, CPU=1)
            G.add_edge(center, node, bandwidth=1)
    else:  # clique
        nodes = ['C1', 'C2', 'C3', 'C4']
        G.add_nodes_from(nodes, CPU=1)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                G.add_edge(nodes[i], nodes[j], bandwidth=1)
    
    return G, service_type

def heuristic_placement(G, service_G):
    mapping = {}
    available_nodes = list(G.nodes())

    for service_node in service_G.nodes():
        if mapping:  
            # Try placing on an existing mapped node to reduce network usage
            mapped_node = random.choice(list(mapping.values()) + available_nodes)
        else:
            mapped_node = random.choice(available_nodes)

        mapping[service_node] = mapped_node

    placed_edges = []
    for u, v in service_G.edges():
        phys_u, phys_v = mapping[u], mapping[v]
        
        if phys_u != phys_v:  # Only add network flow if different physical nodes
            path = nx.shortest_path(G, phys_u, phys_v)
            placed_edges.extend(zip(path[:-1], path[1:]))

    return mapping, placed_edges


def update_resource_requirements(G, placements, service_instances):
    for service_G, mapping in zip(service_instances, placements):
        for service_node, phys_node in mapping.items():
            G.nodes[phys_node]['CPU'] += service_G.nodes[service_node]['CPU']
        
        for u, v in service_G.edges():
            phys_u, phys_v = mapping[u], mapping[v]
            path = nx.shortest_path(G, phys_u, phys_v)
            for i in range(len(path) - 1):
                G[path[i]][path[i + 1]]['bandwidth'] += service_G[u][v]['bandwidth']

def save_topology(G, filename, placed_nodes=None, placed_edges=None, label_mapping=None):
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)

    # Build reverse mapping: physical node -> list of service nodes
    reverse_mapping = {}
    if label_mapping:
        for service_node, phys_node in label_mapping.items():
            reverse_mapping.setdefault(phys_node, []).append(service_node)

    # Create labels
    labels = {}
    for node in G.nodes():
        if node in reverse_mapping:
            # Join multiple service node names
            labels[node] = ", ".join(sorted(reverse_mapping[node]))
        else:
            labels[node] = str(node)

    node_colors = ['red' if node in (placed_nodes or []) else 'gray' for node in G.nodes()]
    nx.draw(G, pos, labels=labels, with_labels=True, node_color=node_colors, edge_color='gray', node_size=500)
    nx.draw_networkx_edges(G, pos, edgelist=placed_edges or [], edge_color='red', width=2)
    plt.savefig(filename, format="pdf")
    plt.close()


def save_service_instance(service_G, filename, service_type):
    plt.figure(figsize=(6, 5))
    pos = nx.spring_layout(service_G, seed=42)  # Layout for readability
    labels = {node: str(node) for node in service_G.nodes()}

    nx.draw(service_G, pos, labels=labels, with_labels=True, node_color='blue', edge_color='black', node_size=500)
    plt.title(f"Service Instance ({service_type})")
    plt.savefig(filename, format="pdf")
    plt.close()

def main():
    with open("sample-config_copy", 'r') as cFile:
        config = json.load(cFile)
    
    numNodes = int(config["numNodes"])
    numLinks = int(config["numLinks"])
    numServiceInstances = int(config.get("numServiceInstances", 5))
    
    # Generate the physical network topology
    G = generate_fixed_topology(numNodes, numLinks)
    save_topology(G, "original_network.pdf")
    
    service_instances = []
    placements = []
    
    for i in range(numServiceInstances):
        # Generate a service instance (star or clique)
        service_G, service_type = generate_service_instance()
        
        # Save the service instance visualization before placement
        save_service_instance(service_G, f"service_instance_{i + 1}.pdf", service_type)
        
        # Perform heuristic placement
        mapping, placed_edges = heuristic_placement(G, service_G)
        service_instances.append(service_G)
        placements.append(mapping)
        
        # Save placement visualization
        save_topology(G, f"placement_{i + 1}.pdf", placed_nodes=mapping.values(), placed_edges=placed_edges, label_mapping=mapping)
    
    # Update resource allocations based on placements
    update_resource_requirements(G, placements, service_instances)
    
    # Print final resource allocations
    print("Final resource allocations:")
    for node in G.nodes():
        print(f"Node {node}: CPU {G.nodes[node]['CPU']}")
    for u, v in G.edges():
        print(f"Edge ({u}, {v}): Bandwidth {G[u][v]['bandwidth']}")
    
if __name__ == "__main__":
    main()

    