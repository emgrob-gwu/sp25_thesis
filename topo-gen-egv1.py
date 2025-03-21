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
    
    if service_type == 'star': #note: these are fixed-shape topologies for now
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
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)

    # Build reverse mapping: physical node -> list of service nodes
    reverse_mapping = {}
    if label_mapping:
        for service_node, phys_node in label_mapping.items():
            reverse_mapping.setdefault(phys_node, []).append(service_node)

    # Create labels with CPU info
    labels = {}
    for node in G.nodes():
        label_parts = []
        if node in reverse_mapping:
            label_parts.append(", ".join(sorted(reverse_mapping[node])))
        else:
            label_parts.append(str(node))
        
        cpu_value = G.nodes[node]['CPU']
        label_parts.append(f"CPU: {cpu_value}")
        
        labels[node] = "\n".join(label_parts)  # Multi-line label

    node_colors = ['red' if node in (placed_nodes or []) else 'gray' for node in G.nodes()]
    nx.draw(G, pos, labels=labels, with_labels=True, node_color=node_colors, edge_color='gray', node_size=800, font_size=8)
    nx.draw_networkx_edges(G, pos, edgelist=placed_edges or [], edge_color='red', width=2)

    # Add bandwidth labels to all edges
    edge_labels = {}
    for u, v in G.edges():
        bw_value = G[u][v]['bandwidth']
        edge_labels[(u, v)] = f"BW: {bw_value}"

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    plt.tight_layout()
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
    placements_per_instance = int(config.get("placementsPerInstance", 2))  # New config value
    
    # Generate the physical network topology
    G = generate_fixed_topology(numNodes, numLinks)
    save_topology(G, "original_network.pdf")
    
    service_instances = []
    all_placements = []
    
    for i in range(numServiceInstances):
        service_G, service_type = generate_service_instance()
        save_service_instance(service_G, f"service_instance_{i + 1}.pdf", service_type)
        
        instance_placements = []
        for j in range(placements_per_instance):
            mapping, placed_edges = heuristic_placement(G, service_G)
            instance_placements.append(mapping)
            update_resource_requirements(G, [mapping], [service_G])

            filename = f"service{i + 1}_placement{j + 1}.pdf"
            save_topology(G, filename, placed_nodes=mapping.values(), placed_edges=placed_edges, label_mapping=mapping)
        
        service_instances.append(service_G)
        all_placements.append(instance_placements)
    
    
    # Print final resource allocations
    print("Final resource allocations:")
    for node in G.nodes():
        print(f"Node {node}: CPU {G.nodes[node]['CPU']}")
    for u, v in G.edges():
        print(f"Edge ({u}, {v}): Bandwidth {G[u][v]['bandwidth']}")


    
if __name__ == "__main__":
    main()

    