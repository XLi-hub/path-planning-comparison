"""
蚁群算法(ACO)实现 - 群体智能算法
用于栅格地图路径规划
"""

import time
import numpy as np
from typing import List, Tuple, Optional


class AntColonyOptimization:
    """蚁群算法路径规划"""

    def __init__(self, grid: np.ndarray, n_ants: int = 50,
                 max_iterations: int = 100, alpha: float = 1.0,
                 beta: float = 3.0, rho: float = 0.1,
                 q0: float = 0.1):
        """
        初始化蚁群算法

        Args:
            grid: 栅格地图
            n_ants: 蚂蚁数量
            max_iterations: 最大迭代次数
            alpha: 信息素权重
            beta: 启发因子权重
            rho: 信息素挥发率
            q0: 伪随机比例参数
        """
        self.grid = grid
        self.rows, self.cols = grid.shape
        self.n_ants = n_ants
        self.max_iterations = max_iterations
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q0 = q0

        # 信息素矩阵 (每个单元格一个值，表示到达该格的偏好)
        self.pheromone = None
        self.best_length_history = []
        self.avg_length_history = []

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                  record_snapshots: bool = True) -> dict:
        """
        使用蚁群算法搜索路径

        Args:
            start: 起点
            goal: 终点
            record_snapshots: 是否记录快照

        Returns:
            dict: 搜索结果
        """
        start_time = time.time()
        self.best_length_history = []
        self.avg_length_history = []

        # 初始化信息素
        tau0 = 1.0 / (self.rows * self.cols)
        self.pheromone = np.full((self.rows, self.cols), tau0)

        # 启发式信息（到目标的距离的倒数）
        heuristic = np.zeros((self.rows, self.cols))
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r, c] == 0:
                    dist = np.sqrt((r - goal[0])**2 + (c - goal[1])**2)
                    heuristic[r, c] = 1.0 / (dist + 0.01)
                else:
                    heuristic[r, c] = 0

        best_path = []
        best_length = float('inf')
        explored_cells = set()

        for iteration in range(self.max_iterations):
            all_paths = []
            all_lengths = []

            # 每只蚂蚁构建路径
            for ant in range(self.n_ants):
                path = self._construct_path(start, goal, heuristic)
                if path:
                    length = self._calc_path_length(path)
                    all_paths.append(path)
                    all_lengths.append(length)
                    # 记录探索的单元格
                    for pt in path:
                        explored_cells.add(pt)

            if not all_paths:
                continue

            # 更新最佳路径
            min_idx = np.argmin(all_lengths)
            if all_lengths[min_idx] < best_length:
                best_length = all_lengths[min_idx]
                best_path = all_paths[min_idx][:]

            # 记录
            self.best_length_history.append(best_length)
            self.avg_length_history.append(np.mean(all_lengths))

            # 信息素挥发
            self.pheromone *= (1.0 - self.rho)

            # 信息素更新（只更新找到路径的蚂蚁，且只更新优秀路径）
            sorted_indices = np.argsort(all_lengths)
            # 只取前25%的优秀蚂蚁
            elite_count = max(1, len(sorted_indices) // 4)
            for rank, idx in enumerate(sorted_indices[:elite_count]):
                path = all_paths[idx]
                delta_tau = 1.0 / (all_lengths[idx] + 0.01)
                # 排名越靠前，信息素越多
                delta_tau *= (elite_count - rank) / elite_count
                for r, c in path:
                    self.pheromone[r, c] += delta_tau

        runtime = time.time() - start_time

        return {
            'path': best_path,
            'explored': list(explored_cells),
            'explored_count': len(explored_cells),
            'path_length': best_length,
            'runtime': runtime,
            'best_length_history': self.best_length_history,
            'avg_length_history': self.avg_length_history,
            'iterations': self.max_iterations
        }

    def _construct_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                        heuristic: np.ndarray) -> Optional[List[Tuple[int, int]]]:
        """
        单只蚂蚁构建路径

        使用伪随机比例规则选择下一步
        """
        path = [start]
        current = start
        visited = {start}
        max_steps = self.rows * self.cols * 2  # 防止无限循环

        for _ in range(max_steps):
            if current == goal:
                return path

            # 获取可行邻居
            neighbors = self._get_neighbors(current, visited)
            if not neighbors:
                # 没有可行邻居，尝试回退
                if len(path) > 1:
                    path.pop()
                    current = path[-1]
                    continue
                else:
                    return None

            # 选择下一个节点
            next_cell = self._select_next(current, neighbors, heuristic)
            if next_cell is None:
                return None

            path.append(next_cell)
            visited.add(next_cell)
            current = next_cell

        # 如果还没到，用贪心补充
        if path[-1] != goal:
            extension = self._greedy_extend(path[-1], goal)
            if extension:
                for pt in extension[1:]:
                    if pt not in visited:
                        path.append(pt)
                        visited.add(pt)

        return path if path[-1] == goal else None

    def _get_neighbors(self, pos: Tuple[int, int],
                       visited: set) -> List[Tuple[int, int]]:
        """获取可行邻居列表"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        neighbors = []
        for dr, dc in directions:
            nr, nc = pos[0] + dr, pos[1] + dc
            if (0 <= nr < self.rows and 0 <= nc < self.cols
                    and self.grid[nr, nc] == 0
                    and (nr, nc) not in visited):
                neighbors.append((nr, nc))
        return neighbors

    def _select_next(self, current: Tuple[int, int],
                     neighbors: List[Tuple[int, int]],
                     heuristic: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        使用伪随机比例规则选择下一步

        q < q0: 选择概率最大的（开发）
        q >= q0: 使用轮盘赌选择（探索）
        """
        if not neighbors:
            return None

        # 计算每个邻居的转移概率
        probabilities = []
        total = 0.0

        for nr, nc in neighbors:
            tau = self.pheromone[nr, nc] ** self.alpha
            eta = heuristic[nr, nc] ** self.beta
            prob = tau * eta
            probabilities.append(prob)
            total += prob

        if total == 0:
            return neighbors[np.random.randint(len(neighbors))]

        q = np.random.random()

        if q < self.q0:
            # 确定性选择: 选概率最大的
            best_idx = np.argmax(probabilities)
            return neighbors[best_idx]
        else:
            # 轮盘赌选择
            probabilities = [p / total for p in probabilities]
            r = np.random.random()
            cumulative = 0
            for i, p in enumerate(probabilities):
                cumulative += p
                if r <= cumulative:
                    return neighbors[i]
            return neighbors[-1]

    def _greedy_extend(self, start: Tuple[int, int],
                       goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """贪心扩展: 从当前点走向目标"""
        path = [start]
        current = start
        visited = {start}
        max_steps = abs(goal[0] - start[0]) + abs(goal[1] - start[1]) + 20

        for _ in range(max_steps):
            if current == goal:
                return path

            neighbors = self._get_neighbors(current, visited)
            if not neighbors:
                return None

            # 选最接近目标的
            best = min(neighbors, key=lambda p:
                       abs(p[0] - goal[0]) + abs(p[1] - goal[1]))
            path.append(best)
            visited.add(best)
            current = best

        return path if path[-1] == goal else None

    @staticmethod
    def _calc_path_length(path: List[Tuple[int, int]]) -> float:
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
