import pandas as pd

import pandas as pd
import json

import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use("TkAgg")

def load_cost_mapping(network_path):
    with open(network_path) as f:
        network_data = json.load(f)
    return {entity['id']: entity['cost_per_hour'] for entity in network_data['entity']}

def calculate_total_cost(trace_path, network_path):
    df = pd.read_csv(trace_path)
    df.rename(columns={'TOPO.dst': 'node_id', 'time_in': 'start_time', 'time_out': 'end_time'}, inplace=True)

    cost_per_hour = load_cost_mapping(network_path)

    df['duration_hours'] = (df['end_time'] - df['start_time']) / 3600.0

    df['cost_rate'] = df['node_id'].map(cost_per_hour)
    df['cost'] = df['duration_hours'] * df['cost_rate']

    total_cost = df['cost'].sum()

    print(f"Total execution cost: ${total_cost:.4f}")
    return df[['id', 'node_id', 'start_time', 'end_time', 'duration_hours', 'cost']]

def calculate_makespan(csv_path):
    # Load simulation data
    df = pd.read_csv(csv_path)

    # Calculate makespan
    start_time = df['time_in'].min()
    end_time = df['time_out'].max()
    makespan = end_time - start_time

    print(f"Makespan of scheduled applications: {makespan:.2f} seconds")

def plot_gantt_chart(df):
    plt.figure(figsize=(12, 6))
    for idx, row in df.iterrows():
        plt.plot([row['start_time'], row['end_time']], [row['node_id'], row['node_id']], lw=4)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Node ID")
    plt.title("Gantt Chart - Task Scheduling Across Nodes")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/gantt_chart.png")
    plt.close()

def plot_cost_per_task(df):
    plt.figure(figsize=(12, 6))
    df_sorted = df.sort_values("cost", ascending=False)
    sns.barplot(x="id", y="cost", hue="id", data=df_sorted, palette="viridis", legend=False)
    plt.xlabel("Task ID")
    plt.ylabel("Cost ($)")
    plt.title("Cost per Task")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("results/cost_per_task.png")
    plt.close()

def plot_cost_per_node(df):
    cost_per_node = df.groupby('node_id')['cost'].sum().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(x="node_id", y="cost", hue="node_id", data=cost_per_node, palette="magma", legend=False)
    plt.xlabel("Node ID")
    plt.ylabel("Total Cost ($)")
    plt.title("Total Cost per Node")
    plt.tight_layout()
    plt.savefig("results/cost_per_node.png")
    plt.close()

if __name__ == "__main__":
    calculate_makespan("results/sim_trace.csv")

    trace_file = 'results/sim_trace.csv'
    network_file = 'data/network.json'
    cost_report = calculate_total_cost(trace_file, network_file)

    plot_gantt_chart(cost_report)
    plot_cost_per_task(cost_report)
    plot_cost_per_node(cost_report)
