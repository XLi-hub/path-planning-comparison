"""
主程序入口 - 运行所有路径规划算法测试
生成所有报告所需的可视化图表
"""

import os
import sys
import time
import numpy as np
from typing import Dict, Tuple

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from map_generator import MapGenerator
from dijkstra import Dijkstra
from astar import AStar
from ga import GeneticAlgorithm
from aco import AntColonyOptimization
from visualize import Visualizer


def print_separator(title: str):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def run_algorithm(algo_name: str, algo_instance, start, goal,
                  record_snapshots=True) -> dict:
    """运行单个算法并打印结果"""
    print(f"\n  Running {algo_name}...")
    t0 = time.time()

    result = algo_instance.find_path(start, goal,
                                     record_snapshots=record_snapshots)

    elapsed = time.time() - t0
    if result['path']:
        print(f"    Path found! Length: {result['path_length']:.2f}, "
              f"Explored: {result['explored_count']} nodes, "
              f"Time: {result['runtime']:.4f}s")
    else:
        print(f"    NO PATH FOUND! Time: {result['runtime']:.4f}s")

    return result


def run_heuristic_comparison(grid, start, goal):
    """比较不同启发函数对A*的影响"""
    heuristics = {
        'manhattan': 'Manhattan',
        'euclidean': 'Euclidean',
        'diagonal': 'Diagonal',
        'chebyshev': 'Chebyshev',
    }
    results = {}
    for heur_key, heur_name in heuristics.items():
        astar = AStar(grid, heuristic=heur_key)
        result = astar.find_path(start, goal, record_snapshots=False)
        results[heur_name] = result
        status = "OK" if result['path'] else "FAIL"
        print(f"    A* ({heur_name:12s}): {status}, "
              f"Len={result['path_length']:.1f}, "
              f"Explored={result['explored_count']}, "
              f"Time={result['runtime']:.4f}s")
    return results


def main():
    """主函数"""
    print_separator("AI Path Planning - Algorithm Comparison")
    print("  4 Algorithms: Dijkstra | A* | Genetic Algorithm | Ant Colony")
    print("  5 Scenes: Random(10%/20%/30%) | Maze | Narrow Passage")

    # 初始化
    gen = MapGenerator(30, 30)
    viz = Visualizer(output_dir='./figures')

    # 生成所有场景
    scenes = gen.generate_all_scenes()

    # 存储所有结果
    all_results = {}       # scene_name -> {algo: result}
    all_heuristic_results = {}  # scene_name -> {heuristic: result}

    # 对每个场景运行所有算法
    for scene_idx, (scene_name, (grid, start, goal)) in enumerate(scenes.items()):
        print_separator(f"Scene {scene_idx+1}: {scene_name}")
        print(f"  Grid: {grid.shape}, Obstacles: "
              f"{np.sum(grid)}/{grid.size} ({np.sum(grid)/grid.size*100:.1f}%)")

        # 绘制原始地图
        viz.plot_grid_map(grid, start, goal,
                         title=f'Scene: {scene_name}',
                         filename=f'map_{scene_name.replace(" ", "_")}.png')

        scene_results = {}

        # 1. Dijkstra
        dijkstra = Dijkstra(grid)
        result_d = run_algorithm('Dijkstra', dijkstra, start, goal)
        scene_results['dijkstra'] = result_d

        # 2. A* (使用manhattan启发函数)
        astar = AStar(grid, heuristic='manhattan')
        result_a = run_algorithm('A*', astar, start, goal)
        scene_results['astar'] = result_a

        # 3. Genetic Algorithm
        ga = GeneticAlgorithm(grid, pop_size=80, max_generations=150,
                             mutation_rate=0.15, crossover_rate=0.8)
        result_g = run_algorithm('GA', ga, start, goal,
                                record_snapshots=False)
        scene_results['ga'] = result_g

        # 4. Ant Colony Optimization
        aco = AntColonyOptimization(grid, n_ants=40, max_iterations=80,
                                    alpha=1.0, beta=3.0, rho=0.15)
        result_ac = run_algorithm('ACO', aco, start, goal,
                                  record_snapshots=False)
        scene_results['aco'] = result_ac

        # 保存结果
        all_results[scene_name] = scene_results

        # ============================================================
        # 生成可视化
        # ============================================================

        # 图1: 路径对比图 (4个子图)
        print(f"\n  Generating visualizations...")
        viz.plot_path_comparison(grid, start, goal, scene_results,
                                scene_name=scene_name)

        # 图2: 综合概览图 (4条路径在同一图上)
        viz.plot_all_scenes_overview(grid, start, goal, scene_results,
                                    scene_name=scene_name)

        # 图3: 搜索过程图 (Dijkstra和A*的探索扩散)
        if result_d.get('snapshots') and result_a.get('snapshots'):
            viz.plot_search_process(grid, start, goal,
                                   result_d['snapshots'],
                                   'dijkstra', scene_name)
            viz.plot_search_process(grid, start, goal,
                                   result_a['snapshots'],
                                   'astar', scene_name)

        # 图4: 搜索扩散对比图 (Dijkstra vs A*)
        viz.plot_search_diffusion_comparison(grid, start, goal,
                                            result_d, result_a,
                                            scene_name=scene_name)

        # 图5: 性能对比柱状图
        viz.plot_performance_comparison(scene_results, scene_name)

        # 图6: 收敛曲线 (GA + ACO)
        viz.plot_convergence(result_g, result_ac, scene_name)

        # 图7: 启发函数对比（仅对第一个场景和迷宫场景）
        if scene_idx == 0 or '迷宫' in scene_name:
            print(f"\n  Running heuristic comparison...")
            heur_results = run_heuristic_comparison(grid, start, goal)
            all_heuristic_results[scene_name] = heur_results
            viz.plot_heuristic_comparison(grid, start, goal, heur_results,
                                         scene_name=scene_name)

    # ============================================================
    # 综合汇总图
    # ============================================================
    print_separator("Generating Comprehensive Summary")
    viz.plot_comprehensive_summary(all_results)

    # ============================================================
    # 打印汇总表格
    # ============================================================
    print_separator("RESULTS SUMMARY")
    print(f"\n{'Scene':<25s} {'Algorithm':<10s} {'Path Len':>10s} "
          f"{'Explored':>10s} {'Time(s)':>10s} {'Status':>8s}")
    print("-" * 75)

    for scene_name, scene_results in all_results.items():
        for algo in ['dijkstra', 'astar', 'ga', 'aco']:
            r = scene_results.get(algo, {})
            path_len = f"{r.get('path_length', 0):.1f}"
            explored = str(r.get('explored_count', 0))
            runtime = f"{r.get('runtime', 0):.4f}"
            status = "OK" if r.get('path') else "FAIL"
            print(f"{scene_name:<25s} {algo:<10s} {path_len:>10s} "
                  f"{explored:>10s} {runtime:>10s} {status:>8s}")

    print(f"\n{'='*60}")
    print(f"  All figures saved to: {os.path.abspath(viz.output_dir)}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
