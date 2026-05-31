# Path Planning: A Comparative Study of Blind, Heuristic, and Swarm Intelligence Algorithms

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive comparison of four path planning algorithms — **Dijkstra**, **A\***, **Genetic Algorithm (GA)**, and **Ant Colony Optimization (ACO)** — across five grid-map scenarios. Part of the AI Course Design at South China University of Technology.

![Comprehensive Summary](figures/comprehensive_summary.png)

## Table of Contents

- [Overview](#overview)
- [Algorithms](#algorithms)
- [Scenarios](#scenarios)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Results](#results)
- [Reports](#reports)
- [License](#license)

## Overview

Path planning is a fundamental problem in AI and robotics: finding an optimal collision-free route from a start to a goal position. This project implements and benchmarks four algorithms spanning three major AI paradigms:

| Algorithm | Paradigm | Type |
|-----------|----------|------|
| **Dijkstra** | Blind (Uninformed) Search | Graph search — uniform cost expansion |
| **A\*** | Heuristic (Informed) Search | Graph search — heuristic-guided expansion |
| **Genetic Algorithm** | Evolutionary Computation | Population-based stochastic optimization |
| **Ant Colony Optimization** | Swarm Intelligence | Distributed pheromone-based coordination |

## Algorithms

### Dijkstra's Algorithm
Classic shortest-path algorithm. Expands nodes uniformly from the start in order of accumulated cost. **Guarantees optimality** but explores a large fraction of the free space.

### A\* Algorithm
Enhances Dijkstra with a heuristic function $h(n)$ estimating remaining cost to the goal. Explores **40–70% fewer nodes** than Dijkstra while maintaining optimality. Includes comparison of four heuristic functions:
- Manhattan distance
- Euclidean distance
- Diagonal distance
- Chebyshev distance

### Genetic Algorithm (GA)
Population-based evolutionary method:
- **Encoding:** Variable-length sequence of waypoints
- **Fitness:** Path length + collision penalty
- **Selection:** Roulette wheel + elite preservation
- **Crossover:** Single-point (rate = 0.80)
- **Mutation:** Insert, delete, modify, smooth (rate = 0.15)

### Ant Colony Optimization (ACO)
Swarm intelligence mimicking ant foraging behavior:
- **Pheromone:** Deposited on traversed cells, evaporates over time
- **Transition rule:** Pseudo-random proportional (exploration vs. exploitation)
- **Parameters:** α = 1.0 (pheromone weight), β = 3.0 (heuristic weight), ρ = 0.15 (evaporation)

## Scenarios

Five 30×30 grid-map scenarios test different environmental challenges:

| # | Scenario | Obstacle Rate | Challenge |
|---|----------|:---:|---|
| 1 | Random Scatter – Low Density | 10% | Baseline easy navigation |
| 2 | Random Scatter – Medium Density | 20% | Moderate obstacle avoidance |
| 3 | Random Scatter – High Density | 30% | Dense obstacles, narrow corridors |
| 4 | Maze-like Obstacles | ~24% | Structured walls (recursive division) |
| 5 | Narrow Passage | ~23% | Small 1–2 cell wall gaps |

All maps use fixed random seeds for reproducibility. Start at (0,0), goal at (29,29).

### Sample Visualizations

**Path comparison (all 4 algorithms overlaid):**

| Low Density (10%) | Maze | Narrow Passage |
|:---:|:---:|:---:|
| ![Low](figures/overview_随机散点-低密度(10%).png) | ![Maze](figures/overview_迷宫式障碍.png) | ![Narrow](figures/overview_窄通道场景.png) |

**Search diffusion (Dijkstra vs. A\*):**

| Dijkstra (Blind) | A* (Heuristic) |
|:---:|:---:|
| ![Dijkstra](figures/diffusion_随机散点-低密度(10%).png) | *Same figure, top vs. bottom row* |

## Project Structure

```
path_planning/
├── main.py                  # Entry point — runs all experiments
├── map_generator.py         # Grid map generation (5 scenarios)
├── dijkstra.py              # Dijkstra's algorithm
├── astar.py                 # A* algorithm (4 heuristics)
├── ga.py                    # Genetic Algorithm
├── aco.py                   # Ant Colony Optimization
├── visualize.py             # Visualization suite (7 figure types)
├── generate_report.py       # Automated Word report generation
├── report.md                # English scientific report (Markdown)
├── report.pdf               # English scientific report (PDF)
├── 课程设计报告_路径规划.docx # Chinese course design report (Word)
├── figures/                 # All generated figures (~43 images)
│   ├── map_*.png                       # Raw grid maps
│   ├── path_comparison_*.png           # 2×2 per-algorithm subplots
│   ├── overview_*.png                  # Single-map 4-algorithm overlay
│   ├── search_process_*.png            # Individual search diffusion
│   ├── diffusion_*.png                 # Dijkstra vs A* side-by-side
│   ├── performance_*.png               # 1×3 performance bar charts
│   ├── convergence_*.png               # GA + ACO convergence curves
│   ├── heuristic_*.png                 # Heuristic function comparison
│   └── comprehensive_summary.png       # Cross-scenario summary
└── .gitignore
```

## Installation

```bash
# Clone the repository
git clone https://github.com/XLi-hub/path-planning-comparison.git
cd path-planning-comparison

# Install dependencies
pip install numpy matplotlib
```

## Usage

```bash
# Run all experiments (generates all figures)
python main.py

# Generate the Word report
python generate_report.py
```

Output figures are saved to `./figures/`. The script prints a summary table to stdout with all quantitative results.

### Quick Example

```python
from map_generator import MapGenerator
from astar import AStar

# Generate a 30×30 map with 20% obstacles
gen = MapGenerator(30, 30)
grid = gen.generate_random_obstacles(obstacle_ratio=0.20, seed=42)

# Run A*
astar = AStar(grid, heuristic='manhattan')
result = astar.find_path((0, 0), (29, 29))

print(f"Path length: {result['path_length']:.1f}")
print(f"Nodes explored: {result['explored_count']}")
print(f"Runtime: {result['runtime']:.4f}s")
```

## Results

### Key Findings

1. **A\*** achieves the best balance — optimal paths while exploring **40–70% fewer nodes** than Dijkstra
2. **Dijkstra** is the optimality benchmark — exhaustive but guaranteed shortest path
3. **ACO** finds near-optimal paths (5–15% longer) with distributed exploration
4. **GA** produces feasible paths (10–30% longer) but with higher variance and runtime

### Performance Summary

| Scenario | Best Path | Best Efficiency | Notes |
|----------|:---------:|:---------------:|-------|
| Low Density (10%) | Dijkstra / A* | A* | All algorithms succeed easily |
| Medium Density (20%) | Dijkstra / A* | A* | Moderate challenge |
| High Density (30%) | Dijkstra / A* | A* | Narrow corridors emerge |
| Maze | Dijkstra / A* | A* | Structured walls favor heuristics |
| Narrow Passage | Dijkstra / A* | A* | Small gaps test exploration |

### Convergence Behavior

- **GA:** Rapid fitness improvement in first 20–30 generations, then gradual refinement
- **ACO:** Best path length drops sharply in first 10–20 iterations; pheromone evaporation ($\rho = 0.15$) prevents premature convergence

## Reports

- **[report.md](report.md)** — Full English scientific report (Markdown, ~500 lines)
  - Abstract, problem formulation, algorithm design with pseudocode
  - Experimental setup, results & analysis across 5 scenarios
  - Discussion, algorithm selection guidelines, references
- **[report.pdf](report.pdf)** — PDF version of the above
- **[课程设计报告_路径规划.docx](课程设计报告_路径规划.docx)** — Complete Chinese course design report (Word, ~30 pages)

## License

MIT License — feel free to use, modify, and distribute.

---

*Course: 人工智能课程设计 (046101421), School of Automation Science and Engineering, South China University of Technology, 2026.*
