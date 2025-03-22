import json

def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def get_available_nodes(network, exclude_types=None):
    if exclude_types is None:
        exclude_types = []
    return [entity for entity in network['entity'] if entity.get('type') not in exclude_types]

def allocate_task_to_node(task_ram, nodes):
    for node in nodes:
        if node['RAM'] >= task_ram:
            node['RAM'] -= task_ram
            return node['id']
    return None

def generate_allocations(apps, network):
    edge_fog_nodes = get_available_nodes(network, exclude_types=['CLOUD'])
    cloud_nodes = get_available_nodes(network, exclude_types=[])

    initial_allocations = []

    for app in apps:
        for module in app['module']:
            assigned_node = allocate_task_to_node(module['RAM'], edge_fog_nodes)
            if assigned_node is None:
                assigned_node = allocate_task_to_node(module['RAM'], cloud_nodes)
            initial_allocations.append({
                "module_name": module['name'],
                "app": app['name'],
                "id_resource": assigned_node
            })
    return {"initialAllocation": initial_allocations}

def main():
    app_definition = load_json('data/appDefinition.json')
    network_definition = load_json('data/network.json')

    allocation_result = generate_allocations(app_definition, network_definition)

    save_json(allocation_result, 'data/allocDefinition.json')

if __name__ == "__main__":
    main()
