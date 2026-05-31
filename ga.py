"""
遗传算法(GA)实现 - 用于栅格地图路径规划
编码方案: 路径点序列（变长染色体）
"""

import time
import numpy as np
from typing import List, Tuple, Optional


class GeneticAlgorithm:
    """遗传算法路径规划"""

    def __init__(self, grid: np.ndarray, pop_size: int = 100,
                 max_generations: int = 200, mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8, elite_ratio: float = 0.05):
        """
        初始化遗传算法

        Args:
            grid: 栅格地图
            pop_size: 种群大小
            max_generations: 最大迭代代数
            mutation_rate: 变异率
            crossover_rate: 交叉率
            elite_ratio: 精英保留比例
        """
        self.grid = grid
        self.rows, self.cols = grid.shape
        self.pop_size = pop_size
        self.max_generations = max_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = max(1, int(pop_size * elite_ratio))
        self.fitness_history = []
        self.best_fitness_history = []
        self.avg_fitness_history = []

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                  record_snapshots: bool = True) -> dict:
        """
        使用遗传算法搜索路径

        Args:
            start: 起点
            goal: 终点
            record_snapshots: 是否记录快照

        Returns:
            dict: 搜索结果
        """
        start_time = time.time()
        self.fitness_history = []
        self.best_fitness_history = []
        self.avg_fitness_history = []

        # 初始化种群
        population = self._init_population(start, goal)
        best_individual = None
        best_fitness = -float('inf')
        explored_cells = set()

        for gen in range(self.max_generations):
            # 计算适应度
            fitness_scores = [self._fitness(ind, start, goal)
                             for ind in population]

            # 记录历史
            gen_best_fitness = max(fitness_scores)
            gen_avg_fitness = np.mean(fitness_scores)
            self.best_fitness_history.append(gen_best_fitness)
            self.avg_fitness_history.append(gen_avg_fitness)

            # 更新全局最佳
            best_idx = np.argmax(fitness_scores)
            if fitness_scores[best_idx] > best_fitness:
                best_fitness = fitness_scores[best_idx]
                best_individual = population[best_idx][:]

            # 记录探索过的单元格
            for ind in population:
                for pt in ind:
                    explored_cells.add(tuple(pt))

            # 检查是否找到有效路径
            if best_fitness > 0:
                # 收敛判断
                if gen > 50 and abs(gen_best_fitness -
                                   self.best_fitness_history[-20]) < 0.01:
                    # 最近20代几乎没有改进，早停
                    pass

            # 选择、交叉、变异产生新一代
            population = self._evolve(population, fitness_scores, start, goal)

        # 从最佳个体提取路径
        if best_individual is not None:
            path = self._decode_path(best_individual, start, goal)
        else:
            path = []

        runtime = time.time() - start_time

        return {
            'path': path,
            'explored': list(explored_cells),
            'explored_count': len(explored_cells),
            'path_length': self._calc_path_length(path),
            'runtime': runtime,
            'fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'generations': self.max_generations,
            'best_fitness': best_fitness
        }

    def _init_population(self, start: Tuple[int, int],
                         goal: Tuple[int, int]) -> List[List[List[int]]]:
        """
        初始化种群

        每个个体是一条从起点到终点的路径（中间点序列）
        使用随机游走生成初始路径
        """
        population = []
        max_points = max(self.rows, self.cols) * 3

        for _ in range(self.pop_size):
            path = self._random_walk(start, goal, max_points)
            # 只保留中间点（去掉起点和终点）
            if len(path) > 2:
                individual = [[p[0], p[1]] for p in path[1:-1]]
            else:
                individual = []
            population.append(individual)

        return population

    def _random_walk(self, start: Tuple[int, int], goal: Tuple[int, int],
                     max_steps: int) -> List[Tuple[int, int]]:
        """随机游走生成一条路径"""
        path = [start]
        current = start
        visited_local = {start}
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for _ in range(max_steps):
            if current == goal:
                break

            # 偏好朝目标方向移动
            np.random.shuffle(directions)
            best_dir = None
            best_dist = float('inf')

            for dr, dc in directions:
                nr, nc = current[0] + dr, current[1] + dc
                if self._is_valid(nr, nc) and (nr, nc) not in visited_local:
                    dist = abs(nr - goal[0]) + abs(nc - goal[1])
                    if dist < best_dist:
                        best_dist = dist
                        best_dir = (dr, dc)

            if best_dir is None:
                # 无路可走，随机选一个未访问的邻居
                valid_moves = [(dr, dc) for dr, dc in directions
                              if self._is_valid(current[0] + dr,
                                               current[1] + dc)]
                if not valid_moves:
                    break
                best_dir = valid_moves[np.random.randint(len(valid_moves))]

            current = (current[0] + best_dir[0], current[1] + best_dir[1])
            visited_local.add(current)
            path.append(current)

        # 如果没到终点，用直线逼近
        if path[-1] != goal:
            path.append(goal)

        return path

    def _fitness(self, individual: List[List[int]], start: Tuple[int, int],
                 goal: Tuple[int, int]) -> float:
        """
        适应度函数

        1. 路径越短越好
        2. 穿过障碍物严重惩罚
        3. 路径点之间连续性越好加分
        """
        if len(individual) == 0:
            # 空个体: 直接连接起点到终点
            dist = np.sqrt((goal[0] - start[0])**2 + (goal[1] - start[1])**2)
            return 1.0 / (dist + 1.0)

        # 构建完整路径
        full_path = [list(start)] + individual + [list(goal)]
        path_length = 0.0
        collision_penalty = 0
        segment_penalty = 0

        for i in range(1, len(full_path)):
            p1 = full_path[i-1]
            p2 = full_path[i]
            seg_len = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            path_length += seg_len

            # 碰撞检测: 使用Bresenham线检测
            if not self._is_segment_valid(p1, p2):
                collision_penalty += seg_len * 10

            # 段太长惩罚
            if seg_len > max(self.rows, self.cols) / 3:
                segment_penalty += seg_len

        # 适应度 = 1/(路径长度 + 碰撞惩罚 + 段惩罚)
        total_cost = path_length + collision_penalty * 100 + segment_penalty * 2
        return 1.0 / (total_cost + 0.01)

    def _is_segment_valid(self, p1: List[int], p2: List[int]) -> bool:
        """检查两个路径点之间的线段是否穿过障碍物"""
        r1, c1 = int(p1[0]), int(p1[1])
        r2, c2 = int(p2[0]), int(p2[1])

        # 使用Bresenham线算法检查
        dr = abs(r2 - r1)
        dc = abs(c2 - c1)
        steps = max(dr, dc)
        if steps == 0:
            return self._is_valid(r1, c1)

        for i in range(steps + 1):
            t = i / steps
            r = int(round(r1 + t * (r2 - r1)))
            c = int(round(c1 + t * (c2 - c1)))
            if not self._is_valid(r, c):
                return False
        return True

    def _evolve(self, population: List[List[List[int]]],
                fitness_scores: List[float],
                start: Tuple[int, int],
                goal: Tuple[int, int]) -> List[List[List[int]]]:
        """进化操作: 选择 + 交叉 + 变异"""
        new_population = []

        # 精英保留
        sorted_indices = np.argsort(fitness_scores)[::-1]
        for i in range(self.elite_size):
            idx = sorted_indices[i]
            new_population.append([p[:] for p in population[idx]])

        # 生成新个体
        while len(new_population) < self.pop_size:
            # 轮盘赌选择
            parent1 = self._roulette_select(population, fitness_scores)
            parent2 = self._roulette_select(population, fitness_scores)

            # 交叉
            if np.random.random() < self.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = [p[:] for p in parent1], [p[:]
                                                          for p in parent2]

            # 变异
            child1 = self._mutate(child1, start, goal)
            child2 = self._mutate(child2, start, goal)

            new_population.append(child1)
            if len(new_population) < self.pop_size:
                new_population.append(child2)

        return new_population[:self.pop_size]

    def _roulette_select(self, population: List[List[List[int]]],
                         fitness_scores: List[float]) -> List[List[int]]:
        """轮盘赌选择"""
        total_fitness = sum(fitness_scores)
        if total_fitness == 0:
            idx = np.random.randint(len(population))
            return [p[:] for p in population[idx]]

        pick = np.random.random() * total_fitness
        cumulative = 0
        for i, fitness in enumerate(fitness_scores):
            cumulative += fitness
            if cumulative >= pick:
                return [p[:] for p in population[i]]

        return [p[:] for p in population[-1]]

    def _crossover(self, parent1: List[List[int]],
                   parent2: List[List[int]]) -> Tuple[List[List[int]],
                                                      List[List[int]]]:
        """单点交叉"""
        if len(parent1) < 2 or len(parent2) < 2:
            return [p[:] for p in parent1], [p[:] for p in parent2]

        cp1 = np.random.randint(1, len(parent1))
        cp2 = np.random.randint(1, len(parent2))

        child1 = parent1[:cp1] + parent2[cp2:]
        child2 = parent2[:cp2] + parent1[cp1:]

        return child1, child2

    def _mutate(self, individual: List[List[int]],
                start: Tuple[int, int],
                goal: Tuple[int, int]) -> List[List[int]]:
        """变异操作"""
        if np.random.random() > self.mutation_rate:
            return individual

        mutated = [p[:] for p in individual]

        mutation_type = np.random.choice(['add', 'remove', 'modify', 'smooth'])

        if mutation_type == 'add' and len(mutated) < self.rows * 2:
            # 随机插入一个新路径点
            if len(mutated) > 0:
                idx = np.random.randint(len(mutated))
                base = mutated[idx]
                offset_r = np.random.randint(-3, 4)
                offset_c = np.random.randint(-3, 4)
                new_pt = [base[0] + offset_r, base[1] + offset_c]
                if self._is_valid(new_pt[0], new_pt[1]):
                    mutated.insert(idx + 1, new_pt)

        elif mutation_type == 'remove' and len(mutated) > 0:
            # 随机删除一个路径点
            idx = np.random.randint(len(mutated))
            mutated.pop(idx)

        elif mutation_type == 'modify' and len(mutated) > 0:
            # 随机修改一个路径点
            idx = np.random.randint(len(mutated))
            offset_r = np.random.randint(-2, 3)
            offset_c = np.random.randint(-2, 3)
            nr = mutated[idx][0] + offset_r
            nc = mutated[idx][1] + offset_c
            if self._is_valid(nr, nc):
                mutated[idx] = [nr, nc]

        elif mutation_type == 'smooth' and len(mutated) > 2:
            # 平滑: 尝试用直接连线替代拐点
            for i in range(len(mutated) - 2, 0, -1):
                prev_pt = start if i == 0 else mutated[i-1]
                next_pt = goal if i == len(mutated) - 1 else mutated[i+1]
                if self._is_segment_valid(list(prev_pt), list(next_pt)):
                    mutated.pop(i)
                    break

        return mutated

    def _decode_path(self, individual: List[List[int]],
                     start: Tuple[int, int],
                     goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """将个体解码为完整路径，修复穿过障碍物的段"""
        full_points = [list(start)] + individual + [list(goal)]
        path = [(start[0], start[1])]

        for i in range(1, len(full_points)):
            p1 = full_points[i-1]
            p2 = full_points[i]

            # 使用Bresenham线填充中间点
            r1, c1 = int(p1[0]), int(p1[1])
            r2, c2 = int(p2[0]), int(p2[1])

            if self._is_segment_valid(p1, p2):
                # 直线连接
                dr = abs(r2 - r1)
                dc = abs(c2 - c1)
                steps = max(dr, dc)
                if steps > 0:
                    for s in range(1, steps + 1):
                        t = s / steps
                        r = int(round(r1 + t * (r2 - r1)))
                        c = int(round(c1 + t * (c2 - c1)))
                        if (r, c) != path[-1]:
                            path.append((r, c))
                else:
                    if (r2, c2) != path[-1]:
                        path.append((r2, c2))
            else:
                # 需要绕过障碍物，使用A*局部修复
                local_path = self._local_repair(
                    (r1, c1), (r2, c2))
                if local_path:
                    for pt in local_path[1:]:
                        if pt != path[-1]:
                            path.append(pt)
                else:
                    path.append((r2, c2))

        return path

    def _local_repair(self, start: Tuple[int, int],
                      goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """使用贪心方法修复不可行段"""
        # 简化的局部修复: 贪心最近邻居
        path = [start]
        current = start
        max_steps = abs(goal[0] - start[0]) + abs(goal[1] - start[1]) + 10

        for _ in range(max_steps):
            if current == goal:
                break

            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]
            best_move = None
            best_dist = float('inf')

            for dr, dc in directions:
                nr, nc = current[0] + dr, current[1] + dc
                if self._is_valid(nr, nc):
                    dist = abs(nr - goal[0]) + abs(nc - goal[1])
                    if dist < best_dist:
                        best_dist = dist
                        best_move = (nr, nc)

            if best_move is None:
                break

            current = best_move
            path.append(current)

        return path if path[-1] == goal else None

    def _is_valid(self, r: int, c: int) -> bool:
        return (0 <= r < self.rows and 0 <= c < self.cols
                and self.grid[r, c] == 0)

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
