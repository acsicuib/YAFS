# Edge-Fog-Cloud Application Scheduling Simulation with YAFS

## Overview
This project is a basic simulation of application scheduling in an Edge-Fog-Cloud environment using **YAFS** (Yet Another Fog Simulator). The simulation includes a network topology, application workflow, and a resource-aware scheduling strategy.

## Specifications
- **Network Topology**:
  - 1 Cloud Node
  - 5 Fog Nodes
  - 5 Edge Nodes
  
- **Applications**:
  - 3 distinct applications
  - Each application comprises 4 tasks (modules)

## Steps to Follow

### 1. Define the Network Topology
- Construct a simple network with nodes and communication links.
- Use **NetworkX** to establish edges between nodes.
- Consider hardware constraints for each node:
  - CPU cores and processing speed
  - Memory and storage capacity
- Implement code that generates a **JSON output** containing the network topology details.

### 2. Define the Application Workflow
- Design an application with multiple tasks (modules).
- Define task characteristics:
  - Each task has an input and output message.
  - Each task has resource requirements (CPU, memory, storage, etc.).
- Implement code that generates a **JSON output** describing the application workflow.

### 3. Implement a Scheduling Strategy
- Ensure processing is prioritized at Edge and Fog nodes before offloading to the Cloud.
  - Only offload tasks to the Cloud if Edge and Fog resources are insufficient.
- Implement resource-aware scheduling:
  - Verify available resources before assigning tasks.
  - Upon task assignment, update the resource availability for the selected node.

### 4. Run the Simulation & Analyze Results
- Collect simulation results in a **CSV file**.
- Analyze request handling, including:
  - Network utilization
  - Processing times

## Deliverables

### Source Code
- Application workflow
- Network topology
- Scheduling strategy

### CSV Files
- Network performance data
- Processing time results