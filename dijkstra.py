"""
Dijkstra算法实现 - 盲目搜索算法（无启发函数）
用于路径规划的基准对比
"""

import heapq
import time
import numpy as np
from typing import List, Tuple, Optional


class Dijkstra:
    """Dijkstra最短路径算法"""

    def __init__(self, grid: np.ndarray):
        """
        初始化Dijkstra算法

        Args:
            grid: 栅格地图 (0=空地, 1=障碍物)
        """
        self.grid = grid
        self.rows, self.cols = grid.shape
        # 8个移动方向: 上下左右 + 四个对角线
        self.directions = [
            (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)
        ]
        # 探索记录
        self.explored_nodes = []
        self.explored_snapshots = []

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                  record_snapshots: bool = True) -> dict:
        """
        使用Dijkstra算法搜索最短路径

        Args:
            start: 起点坐标 (row, col)
            goal: 终点坐标 (row, col)
            record_snapshots: 是否记录搜索过程快照

        Returns:
            dict: {
                'path': 路径坐标列表,
                'explored': 已探索节点列表,
                'explored_count': 探索节点数,
                'path_length': 路径长度,
                'runtime': 运行时间(秒),
                'snapshots': 搜索过程快照
            }
        """
        start_time = time.time()
        self.explored_nodes = []
        self.explored_snapshots = []

        # 距离字典: (r, c) -> 最短距离
        dist = {start: 0}
        # 前驱节点字典: (r, c) -> (prev_r, prev_c)
        prev = {}
        # 优先队列: (距离, 行, 列)
        pq = [(0, start[0], start[1])]
        # 已访问集合
        visited = set()
        # 探索计数
        explored_count = 0

        free_cells = self.rows * self.cols - int(np.sum(self.grid))
        snapshot_intervals = [0.25, 0.50, 0.75, 1.0]
        snapshot_targets = [max(1, int(free_cells * s))
                           for s in snapshot_intervals]

        while pq:
            d, r, c = heapq.heappop(pq)

            if (r, c) in visited:
                continue

            visited.add((r, c))
            self.explored_nodes.append((r, c))
            explored_count += 1

            # 记录搜索过程快照
            if record_snapshots and snapshot_targets and \
               explored_count >= snapshot_targets[0]:
                self.explored_snapshots.append({
                    'explored': list(self.explored_nodes),
                    'percent': snapshot_intervals[len(self.explored_snapshots)],
                    'count': explored_count
                })
                snapshot_targets.pop(0)

            # 到达目标
            if (r, c) == goal:
                # 捕获最终快照（如果还没达到100%）
                if record_snapshots and len(self.explored_snapshots) < 4:
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
                if (nr, nc) in visited:
                    continue

                new_dist = d + move_cost
                if (nr, nc) not in dist or new_dist < dist[(nr, nc)]:
                    dist[(nr, nc)] = new_dist
                    prev[(nr, nc)] = (r, c)
                    heapq.heappush(pq, (new_dist, nr, nc))

        # 回溯路径
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

    def _is_valid(self, r: int, c: int) -> bool:
        """检查坐标是否有效（在边界内且非障碍物）"""
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
                return []  # 无法到达
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
                length += 1.414  # 对角线
            else:
                length += 1.0
        return length
