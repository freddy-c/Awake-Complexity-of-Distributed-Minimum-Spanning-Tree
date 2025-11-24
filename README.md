# Awake Complexity of Distributed Minimum Spanning Tree

This repository contains a Python implementation of the randomized, awake-optimal distributed Minimum Spanning Tree (MST) algorithm from:

> **Awake Complexity of Distributed Minimum Spanning Tree**  
> John Augustine, William K. Moses Jr., Gopal Pandurangan  
> SIROCCO 2024  
> arXiv: https://arxiv.org/abs/2204.08385

This project includes:

- A simulator for implementing distributed algorithms in Python for the sleeping (CONGEST) model
- A baseline implementation of the awake-optimal randomized MST algorithm from the paper
- An **optimized** implementation of the same randomized awake-optimal MST algorithm, specialized for graphs of diameter 3 (see `src/optimized`)
    - For details about the optimized algorithm see [`my university research project paper`](L3_Project_Paper.pdf). If you have any question feel free to reach out to me, you can find my email on my [`Github Profile`](https://github.com/freddy-c).

The script `src/main.py` provides a simple command-line interface that:

- Generates connected graphs of user-chosen size with diameter exactly 3 and random edge weights
- Runs both the baseline and optimized distributed MST implementations on the same graph
- Verifies that both implementations compute the same MST as NetworkX
- Reports and compares the total number of rounds and the maximum number of awake rounds for each implementation

## Setup and Reproducibility with `uv`

This project is configured to use [`uv`](https://github.com/astral-sh/uv) for managing the Python environment and dependencies via `pyproject.toml` and `uv.lock`.

1. Install `uv` (if you do not already have it):

    Follow their guide here [`Installing uv`](https://docs.astral.sh/uv/getting-started/installation/).

2. From the project root, create/prepare the environment and install dependencies exactly as in the reference environment:

    ```bash
    uv sync --locked
    ```

    Using `--locked` tells `uv` to respect the existing `uv.lock` file, recreating the precise versions of all dependencies that were used when the code was confirmed to run successfully.

If you do not care about exact reproducibility, you can instead run:

```bash
uv sync
```

which will resolve dependencies from `pyproject.toml` and update `uv.lock` as needed.

## Running the CLI in `src/main.py`

From the project root, you can run the comparison CLI with:

```bash
uv run src/main.py
```

## How the Network is Modeled
The simulator models the network as an undirected graph $G=(V,E)$.

### Nodes
Each vertex in the graph is represented by an instance of `Node` (`src/simulator/node.py`).

Nodes maintain:
```python
self.ports: Dict[int, Dict]             # local view of incident edges
self.inbox: List[(port, msg)]           # messages received this round
self.staging_inbox: List[(port, msg)]   # messages to be sent
self.terminated: bool                   # whether the node has terminated
```

Algorithms subclass `Node` and override `_compute()`.

### Edges
Edges are stored in the `Network` as tuples:

```python
(u, v, {"weight": w})
```

When an edge is added, the simulator automatically assigns the edge to a local port number for each incident node.

### Ports and Local Port Numbering
This simulator adopts the port-numbering model:
- Each node numbers its incident edges locally, starting from 0.
- The two nodes incident to an edge can assign different port number to that edge.

Example:
```python
u.ports[0] = {"destination": v, "destination_port": 5}
v.ports[5] = {"destination": u, "destination_port": 0}
```
There is no global edge ID.

## How Communication Works
The simulator runs in synchronous rounds.

### Sending Messages
Nodes send messages using their own port numbering:
```python
self.send_message(port_id=0, message="hello")
```

This looks up:
- the neigbour node
- the neighbour's local port for this edge

and places:
```python
(destination_port, message)
```
into the neighbour's `staging_inbox`.

### Message Delivery
At the end of the round, the network delivers messages:
```python
node.inbox.extend(node.staging_inbox)
```
So messages arrive tagged with the receiver’s own port ID.

Example delivery to `v`:
```python
(5, "hello")
```

Which means:
> “You received "hello" on your port 5.”

This is precisely what the sentence means:

> Messages are sent using the sender’s local port number and arrive labeled with the receiver’s local port number.


## How to Implement Algorithms on the Simulator
### Subclass the Node class
```python
from simulator import Node

class MyNode(Node):
    def __init__(self, node_id):
        super().__init__(node_id)
        ...

    def _compute(self, round_number):
        # process inbound messages
        for port, msg in self.inbox:
            ...

        # send outbound messages
        self.send_message(port_id=0, message="hello")

        # optionally sleep or termiante
        # self.sleep(wake_round=round_number + k)
        # self.terminated = True
```

### The `compute()` lifecycle
Each round:
1. `compute()` handles sleep/wake logic.
2. If awake, `_compute()` is called.
3. Messages sent go to neighbours' `staging_inbox`.
4. After all nodes compute, messages are delivered into `inbox`.

### Building and Running a Network
```python
from simulator import Network

network = Network()

# create nodes
for i in range(5):
    network.add_node(MyNode(i))

# add edges
network.add_edge(0, 1, weight=3)
network.add_edge(1, 2, weight=5)

# run simulation
network.simulate_rounds()
```

The simulation will keep running indefinitely unless all nodes set `self.terminated` to `True`.

## MST Algorithm
The repository also includes an implementation of the awake-optimal randomized MST algorithm from the paper. The focus is on minimising worst case awake complexity, the maximum number of rounds in which any node is awake.