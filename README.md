*This project has been created as part of the 42 curriculum by jamourgh*

# Fly-in

## Description

Fly-in is a graph-based simulation project built with Python.
The goal of the project is to simulate multiple drones traveling between hubs in a network while handling routing, collisions, and path optimization.

The program parses:

* Hubs (vertices / nodes)
* Connections between hubs (edges)
* Drone count
* Start and end hubs

After building the graph, the simulation calculates valid paths and moves drones from the start hub to the destination while respecting movement constraints and collision rules.

This project helped me better understand:

* Graph theory fundamentals
* Pathfinding algorithms
* Parsing and validation
* Simulation systems
* State management in graphs

---

# Features

* Parse graph maps from files
* Validate hubs, coordinates, and connections
* Build graph structures dynamically
* Find multiple valid paths
* Simulate drone movement step-by-step
* Handle drone collisions and blocking
* Error handling for invalid maps and malformed input

---

# Instructions

## Requirements

* Python 3.x
* Make
* flake8
* Mypy

## Run the project

Using Makefile:

```bash
make run
```

Or directly with Python:

```bash
python main.py <map_path>
```

Example:

```bash
python main.py maps/easy/01_linear_path.txt
```

---

# Project Structure

```bash
.
├── main.py
├── parser.py
├── classes.py
├── simulation.py
├── maps/
├── Makefile
└── README.md
```

---

# Algorithm Explanation

## Parsing Phase

The parser reads the map file line-by-line and validates:

* Number of drones
* Hub names
* Coordinates
* Metadata
* Connections between hubs

Invalid input immediately raises an error with a clear message.

---

## Graph Construction

After parsing, the program creates:

* Nodes representing hubs
* Edges representing connections

The graph is stored using adjacency relationships to make traversal efficient.

---

## Pathfinding

The program searches for valid paths between:

* `start_hub`
* `end_hub`

Different possible routes are explored to reduce congestion and improve drone flow.

The logic is inspired by:

* Depth-First search (DFS)
* Multi-path traversal techniques

---

## Simulation Logic

The simulation runs step-by-step until all drones reach the destination.

For every turn:

1. Check available paths
2. Move drones if the next hub is free
3. Prevent collisions between drones
4. Update hub occupancy
5. Continue until all drones arrive

The collision system affects drone movement dynamically, meaning one blocked drone can delay others.

---

# Design Decisions

Some important implementation choices:

* Using graph structures for efficient traversal
* Separating parsing, graph logic, and simulation into modules
* Using validation before simulation starts
* Keeping simulation iterative for easier debugging
* Avoiding unnecessary complexity in path selection

These decisions made the project easier to maintain and debug.

---

# Performance Analysis

## Accuracy

The parser validates:

* Invalid hub names
* Duplicate hubs
* Invalid coordinates
* Broken connections
* Missing start/end hubs

This reduces unexpected simulation behavior.

## Speed

The project performs efficiently because:

* Graph traversal is lightweight
* The simulation updates only active drones
* Data structures are simple and efficient

## Reliability

The program includes:

* Input validation
* Safe parsing
* Clear error messages
* Protection against malformed maps

---

# Challenges Faced

## Graph Traversal

At first, understanding how to move drones through multiple paths was difficult.

I solved this by:

* Studying BFS traversal
* Practicing graph problems
* Visualizing graph movement manually

---

## Collision Handling

Managing drone collisions without breaking the simulation was one of the hardest parts.

The main challenge was preventing:

* Multiple drones entering the same hub
* Deadlocks
* Infinite movement loops

I solved this by introducing occupancy checks before every move.

---

## Parsing

Parsing map files correctly required handling many edge cases:

* Invalid formatting
* Wrong metadata
* Missing connections
* Incorrect coordinates

Regex and structured validation helped simplify the parsing step.

---

# Resources

## Graph Theory Resources

These resources helped me understand graph theory and pathfinding concepts:

* Graph Theory Introduction
  [https://www.youtube.com/watch?v=-VgHk7UMPP4](https://www.youtube.com/watch?v=-VgHk7UMPP4)

* Graph Algorithms Basics
  [https://www.youtube.com/watch?v=LFKZLXVO-Dg](https://www.youtube.com/watch?v=LFKZLXVO-Dg)

* Graph Traversal and BFS/DFS (Very Important)
  [https://www.youtube.com/watch?v=tWVWeAqZ0WU](https://www.youtube.com/watch?v=tWVWeAqZ0WU)

* Pathfinding Concepts
  [https://youtu.be/bZkzH5x0SKU](https://youtu.be/bZkzH5x0SKU)

---

## Practice Problems

LeetCode problems that helped me practice graph concepts:

* Number of Provinces
  [https://leetcode.com/problems/number-of-provinces/](https://leetcode.com/problems/number-of-provinces/)

* Keys and Rooms
  [https://leetcode.com/problems/keys-and-rooms/](https://leetcode.com/problems/keys-and-rooms/)

* Find Center of Star Graph
  [https://leetcode.com/problems/find-center-of-star-graph/](https://leetcode.com/problems/find-center-of-star-graph/)

* All Paths From Source to Target
  [https://leetcode.com/problems/all-paths-from-source-to-target/](https://leetcode.com/problems/all-paths-from-source-to-target/)

---

# Example Usage

Example input map:

```txt
5
start A
end Z

A 1 1
B 2 3
C 4 5
Z 6 7

A-B
B-C
C-Z
```

Run:

```bash
python main.py maps/example.txt
```

Example output:

```txt
D0-A
D0-B
D1-A
D0-C
D1-B
...
```

---

# AI Usage

I used AI tools mainly for:

* Understanding project requirements
* Learning graph theory concepts
* Regex assistance
* README improvements
