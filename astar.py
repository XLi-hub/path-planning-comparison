"""
A*算法实现 - 启发式搜索算法
支持多种启发函数: 曼哈顿距离、欧几里得距离、对角线距离
"""

import heapq
import time
import numpy as np
from typing import List, Tuple, Optional


class AStar:
    """A*路径搜索算法，支持多种启发函数"""

    # 启发函数类型
    HEURISTICS = ['manhattan', 'euclidean', 'diagonal', 'chebyshev']

    def __init__(self, grid: np.ndarray, heuristic: str = 'manhattan'):
        """
        初始化A*算法

        Args:
            grid: 栅格地图 (0=空地, 1=障碍物)
            heuristic: 启发函数类型
        """
        self.grid = grid
        self.rows, self.cols = grid.shape
        self.heuristic = heuristic
        # 8个移动方向
        self.directions = [
            (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)
        ]
        self.explored_nodes = []
        self.explored_snapshots = []

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                  record_snapshots: bool = True) -> dict:
        """
        使用A*算法搜索路径

        Args:
            start: 起点
            goal: 终点
            record_snapshots: 是否记录快照

        Returns:
            dict: 搜索结果
        """
        start_time = time.time()
        self.explored_nodes = []
        self.explored_snapshots = []

        # g_score: 从起点到当前节点的实际代价
        g_score = {start: 0}
        # f_score: g_score + 启发函数值
        f_score = {start: self._heuristic_cost(start, goal)}
        # 前驱节点
        prev = {}
        # 优先队列: (f_score, g_score, row, col)
        pq = [(f_score[start], 0, start[0], start[1])]
        # 已访问但可能更新的节点
        open_set = {start}
        # 已关闭节点
        closed_set = set()
        # 探索计数
        explored_count = 0

        free_cells = int(self.rows * self.cols - np.sum(self.grid))
        # 使用绝对数量快照 + 百分比快照，确保在任何情况下都有快照
        snapshot_points = sorted(set(
            [5, 15, 30, 50] +
            [max(1, int(free_cells * s)) for s in [0.25, 0.50, 0.75]]
        ))
        snapshot_labels = {
            sp: min(1.0, sp / max(1, free_cells)) for sp in snapshot_points
        }
        next_snapshot_idx = 0

        while pq:
            f, g, r, c = heapq.heappop(pq)

            if (r, c) in closed_set:
                continue

            closed_set.add((r, c))
            self.explored_nodes.append((r, c))
            explored_count += 1

            # 记录快照
            if record_snapshots and next_snapshot_idx < len(snapshot_points) and \
               explored_count >= snapshot_points[next_snapshot_idx]:
                self.explored_snapshots.append({
                    'explored': list(self.explored_nodes),
                    'percent': snapshot_labels[snapshot_points[next_snapshot_idx]],
                    'count': explored_count
                })
                next_snapshot_idx += 1
                # 跳到下一个未被满足的快照点
                while next_snapshot_idx < len(snapshot_points) and \
                      explored_count >= snapshot_points[next_snapshot_idx]:
                    next_snapshot_idx += 1

            # 到达目标
            if (r, c) == goal:
                if record_snapshots and \
                   (not self.explored_snapshots or
                    self.explored_snapshots[-1]['percent'] < 1.0):
                    self.explored_snapshots.append({
                        'explored': list(self.explored_nodes),
                        'percent': 1.0,
                        'count': explored_count
                    })
                break

            # 扩展邻居
            for dr, dc, move_cost in self.directions:
                nr, nc = r + dr, c + dc
                if not self._is_valid(nr, nc):
                    continue
                if (nr, nc) in closed_set:
                    continue

                tentative_g = g_score[(r, c)] + move_cost

                if (nr, nc) not in g_score or tentative_g < g_score[(nr, nc)]:
                    g_score[(nr, nc)] = tentative_g
                    h = self._heuristic_cost((nr, nc), goal)
                    f_score[(nr, nc)] = tentative_g + h
                    prev[(nr, nc)] = (r, c)
                    heapq.heappush(pq, (f_score[(nr, nc)], tentative_g,
                                        nr, nc))
                    open_set.add((nr, nc))

        path = self._reconstruct_path(prev, start, goal)
        runtime = time.time() - start_time

        return {
            'path': path,
            'explored': self.explored_nodes,
            'explored_count': explored_count,
            'path_length': self._calc_path_length(path),
            'runtime': runtime,
            'snapshots': self.explored_snapshots
        }

    def _heuristic_cost(self, pos: Tuple[int, int],
                        goal: Tuple[int, int]) -> float:
        """
        计算启发函数值

        Args:
            pos: 当前位置
            goal: 目标位置

        Returns:
            启发函数估计代价
        """
        dr = abs(pos[0] - goal[0])
        dc = abs(pos[1] - goal[1])

        if self.heuristic == 'manhattan':
            # 曼哈顿距离: |dx| + |dy|
            return float(dr + dc)

        elif self.heuristic == 'euclidean':
            # 欧几里得距离: sqrt(dx^2 + dy^2)
            return np.sqrt(dr ** 2 + dc ** 2)

        elif self.heuristic == 'diagonal':
            # 对角线距离: max(dx, dy) + (sqrt(2)-1)*min(dx, dy)
            return max(dr, dc) + (1.414 - 1) * min(dr, dc)

        elif self.heuristic == 'chebyshev':
            # 切比雪夫距离: max(|dx|, |dy|)
            return float(max(dr, dc))

        else:
            return float(dr + dc)

    def _is_valid(self, r: int, c: int) -> bool:
        """检查坐标有效性"""
        return (0 <= r < self.rows and 0 <= c < self.cols
                and self.grid[r, c] == 0)

    def _reconstruct_path(self, prev: dict, start: Tuple[int, int],
                          goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """回溯重建路径"""
        path = []
        current = goal
        while current != start:
            path.append(current)
            if current not in prev:
                return []
            current = prev[current]
        path.append(start)
        path.reverse()
        return path

    @staticmethod
    def _calc_path_length(path: List[Tuple[int, int]]) -> float:
        """计算路径总长度"""
        if not path:
            return float('inf')
        length = 0.0
        for i in range(1, len(path)):
            dr = abs(path[i][0] - path[i-1][0])
            dc = abs(path[i][1] - path[i-1][1])
            if dr == 1 and dc == 1:
                length += 1.414
            else:
                length += 1.0
        return length
