import networkx as nx
import random
import json
import matplotlib.pyplot as plt

def generate_cloud_fog_edge_network(cloud_count, fog_count, edge_count, filename='data/network.json'):
    G = nx.Graph()

    node_id = 0
    node_mapping = {}
    node_positions = {}
    node_colors = []

    # Add cloud nodes
    # AWS EC2 instance types (t3.xlarge, t3.2xlarge, m5.4xlarge)
    cloud_specs = [
        {'RAM': 16, 'HD': 20, 'IPT': 4},  # t3.xlarge
        {'RAM': 32, 'HD': 40, 'IPT': 8},  # t3.2xlarge 
        {'RAM': 64, 'HD': 100, 'IPT': 16}  # m5.4xlarge
    ]
    for _ in range(cloud_count):
        spec = random.choice(cloud_specs)
        G.add_node(node_id, RAM=spec['RAM'], HD=spec['HD'], IPT=spec['IPT'], type='CLOUD')
        node_mapping[f'cloud_{node_id}'] = node_id
        node_positions[node_id] = (random.uniform(0.4, 0.6), 1)
        node_colors.append('red')
        node_id += 1

    # Add fog nodes
    for _ in range(fog_count):
        G.add_node(node_id, RAM=random.randint(16, 32), HD=1, IPT=1, type='FOG')
        node_mapping[f'fog_{node_id}'] = node_id
        node_positions[node_id] = (random.uniform(0.2, 0.8), 0.5)
        node_colors.append('blue')
        node_id += 1

    # Add edge nodes
    for _ in range(edge_count):
        G.add_node(node_id, RAM=random.randint(4, 16), HD=1, IPT=1, type='EDGE')
        node_mapping[f'edge_{node_id}'] = node_id
        node_positions[node_id] = (random.uniform(0, 1), 0)
        node_colors.append('green')
        node_id += 1

    links = []

    # Connect fog nodes to cloud nodes
    for fog_node in [n for n, d in G.nodes(data=True) if d['type'] == 'FOG']:
        cloud_node = random.choice([n for n, d in G.nodes(data=True) if d['type'] == 'CLOUD'])
        PR = random.randint(1, 5)
        BW = random.randint(50000, 100000)
        G.add_edge(fog_node, cloud_node, PR=PR, BW=BW)
        links.append({'s': fog_node, 'd': cloud_node, 'PR': PR, 'BW': BW})

    # Connect edge nodes to fog nodes
    for edge_node in [n for n, d in G.nodes(data=True) if d['type'] == 'EDGE']:
        fog_node = random.choice([n for n, d in G.nodes(data=True) if d['type'] == 'FOG'])
        PR = random.randint(1, 5)
        BW = random.randint(50000, 100000)
        G.add_edge(edge_node, fog_node, PR=PR, BW=BW)
        links.append({'s': edge_node, 'd': fog_node, 'PR': PR, 'BW': BW})

    entities = []
    for node, data in G.nodes(data=True):
        entity = {
            'id': node,
            'RAM': data['RAM'],
            'HD': data['HD'],
            'IPT': data['IPT'],
            'type': data['type']
        }
        entities.append(entity)

    network_data = {
        'entity': entities,
        'link': links
    }

    with open(filename, 'w') as f:
        json.dump(network_data, f, indent=4)

    print(f'Network data saved to {filename}')

    # Visualization
    nx.draw(G, pos=node_positions, with_labels=True, node_color=node_colors, node_size=500)


# example usage
generate_cloud_fog_edge_network(cloud_count=1, fog_count=1, edge_count=3)
