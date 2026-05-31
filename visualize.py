"""
可视化模块 - 生成报告所需的所有静态图表
包括: 路径对比图、搜索过程图、性能对比图、收敛曲线等
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
from typing import List, Tuple, Dict, Optional
import os

# 尝试使用中文字体
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei',
                                        'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except Exception:
    pass


# ============================================================
# 颜色方案
# ============================================================
COLORS = {
    'free': '#F5F5F5',          # 空地 - 浅灰
    'obstacle': '#2C3E50',      # 障碍物 - 深灰蓝
    'start': '#27AE60',          # 起点 - 绿
    'goal': '#E74C3C',           # 终点 - 红
    'dijkstra': '#3498DB',       # Dijkstra路径 - 蓝
    'astar': '#F39C12',          # A*路径 - 橙
    'ga': '#9B59B6',             # GA路径 - 紫
    'aco': '#1ABC9C',            # ACO路径 - 青
    'explored': '#AED6F1',       # 已探索 - 浅蓝
    'explored_astar': '#FDEBD0',  # A*已探索 - 浅橙
}

ALGORITHM_NAMES = {
    'dijkstra': 'Dijkstra (盲目搜索)',
    'astar': 'A* (启发式搜索)',
    'ga': '遗传算法 GA',
    'aco': '蚁群算法 ACO',
}


class Visualizer:
    """可视化生成器"""

    def __init__(self, output_dir: str = './figures'):
        """
        初始化可视化器

        Args:
            output_dir: 图片输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_grid_map(self, grid: np.ndarray, start: Tuple[int, int],
                      goal: Tuple[int, int], title: str = None,
                      filename: str = None, show: bool = False):
        """绘制原始栅格地图"""
        fig, ax = plt.subplots(figsize=(8, 8))

        rows, cols = grid.shape
        # 绘制网格
        for r in range(rows):
            for c in range(cols):
                if grid[r, c] == 1:
                    ax.add_patch(plt.Rectangle(
                        (c, rows - 1 - r), 1, 1,
                        facecolor=COLORS['obstacle'],
                        edgecolor='#1a1a2e', linewidth=0.3))
                else:
                    ax.add_patch(plt.Rectangle(
                        (c, rows - 1 - r), 1, 1,
                        facecolor=COLORS['free'],
                        edgecolor='#d5d5d5', linewidth=0.3))

        # 起点和终点
        ax.add_patch(plt.Rectangle(
            (start[1], rows - 1 - start[0]), 1, 1,
            facecolor=COLORS['start'], alpha=0.8))
        ax.text(start[1] + 0.5, rows - 1 - start[0] + 0.5, 'S',
                ha='center', va='center', fontsize=12, fontweight='bold',
                color='white')

        ax.add_patch(plt.Rectangle(
            (goal[1], rows - 1 - goal[0]), 1, 1,
            facecolor=COLORS['goal'], alpha=0.8))
        ax.text(goal[1] + 0.5, rows - 1 - goal[0] + 0.5, 'G',
                ha='center', va='center', fontsize=12, fontweight='bold',
                color='white')

        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])

        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)

        # 图例
        legend_elements = [
            mpatches.Patch(facecolor=COLORS['free'],
                           edgecolor='#d5d5d5', label='Free Space'),
            mpatches.Patch(facecolor=COLORS['obstacle'],
                           edgecolor='#1a1a2e', label='Obstacle'),
            mpatches.Patch(facecolor=COLORS['start'],
                           label='Start'),
            mpatches.Patch(facecolor=COLORS['goal'],
                           label='Goal'),
        ]
        ax.legend(handles=legend_elements, loc='upper right',
                  fontsize=9, framealpha=0.9)

        plt.tight_layout()
        if filename:
            plt.savefig(os.path.join(self.output_dir, filename),
                       dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def plot_path_comparison(self, grid: np.ndarray,
                             start: Tuple[int, int],
                             goal: Tuple[int, int],
                             results: Dict[str, dict],
                             scene_name: str = '',
                             show: bool = False):
        """
        绘制路径对比图 - 4种算法在同一地图上

        Args:
            grid: 栅格地图
            start: 起点
            goal: 终点
            results: {算法名: result_dict}
            scene_name: 场景名称
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 14))
        axes = axes.flatten()

        algo_keys = ['dijkstra', 'astar', 'ga', 'aco']
        algo_colors = [COLORS['dijkstra'], COLORS['astar'],
                       COLORS['ga'], COLORS['aco']]

        for ax, algo, color in zip(axes, algo_keys, algo_colors):
            self._draw_grid_base(ax, grid, start, goal)
            result = results.get(algo)
            if result and result['path']:
                self._draw_path(ax, result['path'], color, linewidth=2.5)
                info_text = (
                    f"Path Length: {result['path_length']:.1f}\n"
                    f"Explored: {result['explored_count']}\n"
                    f"Time: {result['runtime']:.3f}s"
                )
                ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                        fontsize=9, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white',
                                 alpha=0.85))
            else:
                ax.text(0.5, 0.5, 'NO PATH FOUND',
                       transform=ax.transAxes, ha='center', va='center',
                       fontsize=14, color='red', fontweight='bold')

            ax.set_title(ALGORITHM_NAMES.get(algo, algo),
                        fontsize=13, fontweight='bold')

        fig.suptitle(f'Path Planning Comparison — {scene_name}',
                     fontsize=15, fontweight='bold', y=0.98)
        plt.tight_layout()
        filename = f'path_comparison_{scene_name.replace(" ", "_")}.png'
        plt.savefig(os.path.join(self.output_dir, filename),
                   dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def plot_all_scenes_overview(self, grid: np.ndarray,
                                 start: Tuple[int, int],
                                 goal: Tuple[int, int],
                                 results: Dict[str, dict],
                                 scene_name: str = '',
                                 show: bool = False):
        """
        绘制综合概览图 - 单个场景，4个算法合并在一张图上
        用于报告的核心展示图
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        self._draw_grid_base(ax, grid, start, goal)

        algo_colors = {
            'dijkstra': COLORS['dijkstra'],
            'astar': COLORS['astar'],
            'ga': COLORS['ga'],
            'aco': COLORS['aco'],
        }
        line_styles = {
            'dijkstra': '-',
            'astar': '-',
            'ga': '--',
            'aco': '-.',
        }

        legend_elements = [
            mpatches.Patch(facecolor=COLORS['free'],
                           edgecolor='#d5d5d5', label='Free'),
            mpatches.Patch(facecolor=COLORS['obstacle'],
                           edgecolor='#1a1a2e', label='Obstacle'),
            mpatches.Patch(facecolor=COLORS['start'], label='Start'),
            mpatches.Patch(facecolor=COLORS['goal'], label='Goal'),
        ]

        for algo in ['dijkstra', 'astar', 'ga', 'aco']:
            result = results.get(algo)
            color = algo_colors[algo]
            style = line_styles[algo]
            if result and result['path']:
                self._draw_path(ax, result['path'], color,
                               linewidth=2.5, linestyle=style)
            legend_elements.append(
                plt.Line2D([0], [0], color=color, linestyle=style,
                          linewidth=2, label=ALGORITHM_NAMES.get(algo, algo))
            )

        ax.legend(handles=legend_elements, loc='lower left',
                 fontsize=9, framealpha=0.9, ncol=2)
        ax.set_title(f'Path Planning — All Algorithms — {scene_name}',
                     fontsize=14, fontweight='bold', pad=15)

        plt.tight_layout()
        filename = f'overview_{scene_name.replace(" ", "_")}.png'
        plt.savefig(os.path.join(self.output_dir, filename),
                   dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def plot_search_process(self, grid: np.ndarray,
                            start: Tuple[int, int],
                            goal: Tuple[int, int],
                            snapshots: List[dict],
                            algorithm_name: str,
                            scene_name: str = '',
                            show: bool = False):
        """
        绘制搜索过程图 - 2×2 子图展示不同阶段的已探索节点

        Args:
            snapshots: 探索过程快照列表 [{explored, percent, count}, ...]
        """
        if not snapshots:
            return

        n_snaps = len(snapshots)
        if n_snaps <= 2:
            nrows, ncols = 1, n_snaps
        elif n_snaps <= 4:
            nrows, ncols = 2, 2
        else:
            nrows, ncols = 2, 3

        fig, axes = plt.subplots(nrows, ncols, figsize=(6*ncols, 6*nrows))
        if nrows * ncols == 1:
            axes = [axes]
        else:
            axes = axes.flatten()

        for i in range(nrows * ncols):
            ax = axes[i]
            if i < n_snaps:
                snap = snapshots[i]
                self._draw_grid_base(ax, grid, start, goal)

                # 绘制已探索节点
                explored = snap['explored']
                if explored:
                    rows, cols = grid.shape
                    for r, c in explored:
                        ax.add_patch(plt.Rectangle(
                            (c, rows - 1 - r), 1, 1,
                            facecolor=COLORS['explored'],
                            edgecolor='none', alpha=0.5))

                ax.set_title(
                    f"{snap['percent']*100:.0f}% Explored ({snap['count']} nodes)",
                    fontsize=12, fontweight='bold')
            else:
                ax.set_visible(False)

        fig.suptitle(
            f'Search Process — {ALGORITHM_NAMES.get(algorithm_name, algorithm_name)}\n{scene_name}',
            fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout()
        filename = (f'search_process_{algorithm_name}_'
                   f'{scene_name.replace(" ", "_")}.png')
        plt.savefig(os.path.join(self.output_dir, filename),
                   dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def plot_performance_comparison(self, results: Dict[str, dict],
                                    scene_name: str = '',
                                    show: bool = False):
        """
        绘制性能对比柱状图
        """
        algorithms = ['dijkstra', 'astar', 'ga', 'aco']
        names = ['Dijkstra\n(Blind)', 'A*\n(Heuristic)', 'GA\n(Evolution)',
                 'ACO\n(Swarm)']

        path_lengths = []
        explored_counts = []
        runtimes = []

        for algo in algorithms:
            result = results.get(algo, {})
            path_lengths.append(result.get('path_length', 0))
            explored_counts.append(result.get('explored_count', 0))
            runtimes.append(result.get('runtime', 0))

        fig, axes = plt.subplots(1, 3, figsize=(16, 5))

        colors = [COLORS['dijkstra'], COLORS['astar'],
                  COLORS['ga'], COLORS['aco']]

        # 路径长度
        ax = axes[0]
        bars = ax.bar(names, path_lengths, color=colors, edgecolor='white',
                      linewidth=1.2)
        ax.set_title('Path Length Comparison', fontsize=13, fontweight='bold')
        ax.set_ylabel('Path Length')
        for bar, val in zip(bars, path_lengths):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f'{val:.1f}', ha='center', fontsize=10, fontweight='bold')

        # 探索节点数
        ax = axes[1]
        bars = ax.bar(names, explored_counts, color=colors, edgecolor='white',
                      linewidth=1.2)
        ax.set_title('Explored Nodes', fontsize=13, fontweight='bold')
        ax.set_ylabel('Nodes Explored')
        for bar, val in zip(bars, explored_counts):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                    str(val), ha='center', fontsize=10, fontweight='bold')

        # 运行时间
        ax = axes[2]
        bars = ax.bar(names, runtimes, color=colors, edgecolor='white',
                      linewidth=1.2)
        ax.set_title('Runtime', fontsize=13, fontweight='bold')
        ax.set_ylabel('Time (seconds)')
        for bar, val in zip(bars, runtimes):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f'{val:.3f}s', ha='center', fontsize=10, fontweight='bold')

        fig.suptitle(f'Algorithm Performance Comparison — {scene_name}',
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        filename = f'performance_{scene_name.replace(" ", "_")}.png'
        plt.savefig(os.path.join(self.output_dir, filename),
                   dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def plot_convergence(self, result_ga: dict, result_aco: dict,
                         scene_name: str = '', show: bool = False):
        """
        绘制GA和ACO的收敛曲线
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # GA收敛曲线
        ax = axes[0]
        if result_ga and 'fitness_history' in result_ga:
            gen = range(len(result_ga['fitness_history']))
            best = result_ga['fitness_history']
            avg = result_ga.get('avg_fitness_history', [])
            ax.plot(gen, best, color=COLORS['ga'], linewidth=2,
                   label='Best Fitness')
            if avg:
                ax.plot(gen, avg, color=COLORS['ga'], alpha=0.3,
                       linewidth=1, label='Avg Fitness')
            ax.set_title('GA Convergence Curve', fontsize=13, fontweight='bold')
            ax.set_xlabel('Generation')
            ax.set_ylabel('Fitness')
            ax.legend()
            ax.grid(True, alpha=0.3)

        # ACO收敛曲线
        ax = axes[1]
        if result_aco and 'best_length_history' in result_aco:
            iters = range(len(result_aco['best_length_history']))
            best = result_aco['best_length_history']
            avg = result_aco.get('avg_length_history', [])
            ax.plot(iters, best, color=COLORS['aco'], linewidth=2,
                   label='Best Path Length')
            if avg:
                ax.plot(iters, avg, color=COLORS['aco'], alpha=0.3,
                       linewidth=1, label='Avg Path Length')
            ax.set_title('ACO Convergence Curve', fontsize=13, fontweight='bold')
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Path Length')
            ax.legend()
            ax.grid(True, alpha=0.3)

        fig.suptitle(f'Convergence Analysis — {scene_name}',
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        filename = f'convergence_{scene_name.replace(" ", "_")}.png'
        plt.savefig(os.path.join(self.output_dir, filename),
                   dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def plot_heuristic_comparison(self, grid: np.ndarray,
                                  start: Tuple[int, int],
                                  goal: Tuple[int, int],
                                  heuristic_results: Dict[str, dict],
                                  scene_name: str = '',
                                  show: bool = False):
        """
        绘制不同启发函数的A*对比
        """
        heuristics = list(heuristic_results.keys())
        n = len(heuristics)

        fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
        if n == 1:
            axes = [axes]

        for ax, heur_name in zip(axes, heuristics):
            result = heuristic_results[heur_name]
            self._draw_grid_base(ax, grid, start, goal)

            # 绘制已探索节点
            explored = result.get('explored', [])
            if explored:
                rows, cols = grid.shape
                for r, c in explored:
                    ax.add_patch(plt.Rectangle(
                        (c, rows - 1 - r), 1, 1,
                        facecolor=COLORS['explored_astar'],
                        edgecolor='none', alpha=0.4))

            # 绘制路径
            if result.get('path'):
                self._draw_path(ax, result['path'], COLORS['astar'],
                               linewidth=2.5)

            info = (f"h = {heur_name}\n"
                   f"Len: {result['path_length']:.1f}\n"
                   f"Explored: {result['explored_count']}\n"
                   f"Time: {result['runtime']:.3f}s")
            ax.text(0.02, 0.98, info, transform=ax.transAxes,
                   fontsize=9, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.85))
            ax.set_title(f'A* with {heur_name}', fontsize=12, fontweight='bold')

        fig.suptitle(f'Heuristic Function Comparison — {scene_name}',
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        filename = f'heuristic_{scene_name.replace(" ", "_")}.png'
        plt.savefig(os.path.join(self.output_dir, filename),
                   dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def plot_comprehensive_summary(self,
                                   all_scene_results: Dict[str, dict],
                                   show: bool = False):
        """
        绘制综合汇总图 - 所有场景的对比表格图
        """
        scenes = list(all_scene_results.keys())
        algorithms = ['dijkstra', 'astar', 'ga', 'aco']
        algo_labels = ['Dijkstra', 'A*', 'GA', 'ACO']

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # 为每个指标创建分组柱状图
        metrics = ['path_length', 'explored_count', 'runtime']
        metric_labels = ['Path Length', 'Nodes Explored', 'Runtime (s)']
        colors = [COLORS['dijkstra'], COLORS['astar'],
                  COLORS['ga'], COLORS['aco']]

        for ax, metric, metric_label in zip(axes, metrics, metric_labels):
            x = np.arange(len(scenes))
            width = 0.2

            for i, (algo, label, color) in enumerate(zip(algorithms,
                                                         algo_labels,
                                                         colors)):
                values = []
                for scene in scenes:
                    result = all_scene_results[scene].get(algo, {})
                    val = result.get(metric, 0)
                    if metric == 'runtime':
                        val = min(val, 5.0)  # 限制显示范围
                    values.append(val)

                offset = (i - 1.5) * width
                ax.bar(x + offset, values, width, label=label, color=color,
                      edgecolor='white', linewidth=0.8)

            ax.set_title(metric_label, fontsize=13, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(scenes, rotation=30, ha='right', fontsize=8)
            if metric == 'runtime':
                ax.set_ylabel('Seconds')
            ax.legend(fontsize=8, loc='upper right')

        fig.suptitle('Comprehensive Performance Summary Across All Scenes',
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir,
                                'comprehensive_summary.png'),
                   dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def plot_search_diffusion_comparison(self, grid: np.ndarray,
                                         start: Tuple[int, int],
                                         goal: Tuple[int, int],
                                         dijkstra_result: dict,
                                         astar_result: dict,
                                         scene_name: str = '',
                                         show: bool = False):
        """
        绘制Dijkstra vs A* 的搜索扩散对比图
        直观展示盲目搜索(均匀扩散) vs 启发式搜索(定向扩散)
        """
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))

        titles = ['25%', '50%', '75%', '100%']

        for row, (result, algo_name, explored_color) in enumerate([
            (dijkstra_result, 'Dijkstra (Blind Search)',
             COLORS['explored']),
            (astar_result, 'A* (Heuristic Search)',
             COLORS['explored_astar'])
        ]):
            snapshots = result.get('snapshots', [])
            for col in range(4):
                ax = axes[row, col]
                self._draw_grid_base(ax, grid, start, goal)

                if col < len(snapshots):
                    snap = snapshots[col]
                    explored = snap['explored']
                    if explored:
                        rows, cols = grid.shape
                        for r, c in explored:
                            ax.add_patch(plt.Rectangle(
                                (c, rows - 1 - r), 1, 1,
                                facecolor=explored_color,
                                edgecolor='none', alpha=0.5))

                    # 如果到了100%，显示最终路径
                    if col == len(snapshots) - 1 and result.get('path'):
                        path_color = COLORS['dijkstra'] if row == 0 \
                                     else COLORS['astar']
                        self._draw_path(ax, result['path'], path_color,
                                       linewidth=2)

                    ax.set_title(f'{titles[col]} ({snap["count"]} cells)',
                                fontsize=10, fontweight='bold')
                else:
                    ax.set_title(f'{titles[col]} (N/A)', fontsize=10)

            # 行标签
            axes[row, 0].set_ylabel(algo_name, fontsize=13, fontweight='bold',
                                   labelpad=20)

        fig.suptitle(
            f'Search Diffusion: Blind vs. Heuristic — {scene_name}',
            fontsize=15, fontweight='bold', y=0.98)
        plt.tight_layout()
        filename = f'diffusion_{scene_name.replace(" ", "_")}.png'
        plt.savefig(os.path.join(self.output_dir, filename),
                   dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    # ============================================================
    # 辅助绘图方法
    # ============================================================

    def _draw_grid_base(self, ax, grid, start, goal):
        """绘制基础网格"""
        rows, cols = grid.shape
        for r in range(rows):
            for c in range(cols):
                if grid[r, c] == 1:
                    ax.add_patch(plt.Rectangle(
                        (c, rows - 1 - r), 1, 1,
                        facecolor=COLORS['obstacle'],
                        edgecolor='#1a1a2e', linewidth=0.2))

        # 起点
        ax.add_patch(plt.Rectangle(
            (start[1], rows - 1 - start[0]), 1, 1,
            facecolor=COLORS['start'], alpha=0.9))
        ax.text(start[1] + 0.5, rows - 1 - start[0] + 0.5, 'S',
                ha='center', va='center', fontsize=10, fontweight='bold',
                color='white')

        # 终点
        ax.add_patch(plt.Rectangle(
            (goal[1], rows - 1 - goal[0]), 1, 1,
            facecolor=COLORS['goal'], alpha=0.9))
        ax.text(goal[1] + 0.5, rows - 1 - goal[0] + 0.5, 'G',
                ha='center', va='center', fontsize=10, fontweight='bold',
                color='white')

        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])

    def _draw_path(self, ax, path: List[Tuple[int, int]], color: str,
                   linewidth: float = 2.5, linestyle: str = '-'):
        """在图上绘制路径"""
        if not path or len(path) < 2:
            return
        rows = self._get_grid_rows(ax)
        # 转换坐标: (row, col) -> (x=col+0.5, y=rows-1-row+0.5)
        xs = [p[1] + 0.5 for p in path]
        ys = [rows - 1 - p[0] + 0.5 for p in path]
        ax.plot(xs, ys, color=color, linewidth=linewidth, linestyle=linestyle,
               alpha=0.9, solid_capstyle='round', solid_joinstyle='round')
        # 起点和终点标记
        ax.scatter([xs[0]], [ys[0]], color=color, s=60, zorder=5)
        ax.scatter([xs[-1]], [ys[-1]], color=color, s=60, zorder=5)

    def _get_grid_rows(self, ax) -> int:
        """获取当前子图中的网格行数"""
        # 从绘制的patch推断
        return 30  # 默认值
