import json
import random

def generate_random_tasks(num_apps=1, tasks_per_app=2, filename='data/appDefinition.json'):
    apps = []
    task_id_counter = 0
    message_id_counter = 0

    for app_id in range(num_apps):
        modules = []
        messages = []
        transmissions = []

        for task_num in range(tasks_per_app):
            module_name = f"{app_id}_{task_num:02d}"
            message_name = f"M.USER.APP.{app_id}.{task_num}"

            module = {
                "id": task_id_counter,
                "name": module_name,
                "type": "MODULE",
                "RAM": random.randint(1, 4)
            }
            modules.append(module)

            message = {
                "id": message_id_counter,
                "name": message_name,
                "s": "None" if task_num == 0 else f"{app_id}_{task_num-1:02d}",
                "d": module_name,
                "bytes": random.randint(10, 50),
                "instructions": random.randint(20, 100)
            }
            messages.append(message)

            transmission = {
                "message_in": message_name,
                "module": module_name
            }
            transmissions.append(transmission)

            task_id_counter += 1
            message_id_counter += 1

        app = {
            "id": app_id,
            "name": str(app_id),
            "HwReqs": random.randint(1, 3),
            "MaxReqs": random.randint(100, 500),
            "MaxLatency": random.randint(10, 100),
            "transmission": transmissions,
            "module": modules,
            "message": messages
        }
        apps.append(app)

    # Save to JSON
    with open(filename, 'w') as f:
        json.dump(apps, f, indent=4)

    print(f"Random application workflow saved to {filename}")

generate_random_tasks()