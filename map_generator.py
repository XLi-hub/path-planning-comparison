"""
地图生成模块 - 生成多种栅格地图用于路径规划测试
支持: 随机散点障碍、迷宫式障碍、窄通道场景
"""

import numpy as np
import random


class MapGenerator:
    """栅格地图生成器"""

    def __init__(self, rows: int = 30, cols: int = 30):
        """
        初始化地图生成器

        Args:
            rows: 地图行数
            cols: 地图列数
        """
        self.rows = rows
        self.cols = cols
        self.grid = np.zeros((rows, cols), dtype=int)
        self.start = (0, 0)
        self.goal = (rows - 1, cols - 1)

    def generate_random_obstacles(self, obstacle_ratio: float = 0.2,
                                  seed: int = None) -> np.ndarray:
        """
        生成随机散点障碍物地图

        Args:
            obstacle_ratio: 障碍物覆盖率
            seed: 随机种子

        Returns:
            栅格地图 (0=空地, 1=障碍物)
        """
        if seed is not None:
            np.random.seed(seed)

        self.grid = np.zeros((self.rows, self.cols), dtype=int)
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) != self.start and (i, j) != self.goal:
                    if np.random.random() < obstacle_ratio:
                        self.grid[i, j] = 1
        return self.grid

    def generate_maze(self, seed: int = None) -> np.ndarray:
        """
        生成迷宫式障碍物地图（使用递归分割法）

        Args:
            seed: 随机种子

        Returns:
            栅格地图
        """
        if seed is not None:
            random.seed(seed)

        self.grid = np.zeros((self.rows, self.cols), dtype=int)

        # 添加边界墙
        for i in range(self.rows):
            for j in range(self.cols):
                if i == 0 or i == self.rows - 1 or j == 0 or j == self.cols - 1:
                    self.grid[i, j] = 1

        # 递归分割法生成迷宫墙
        self._divide_maze(1, 1, self.rows - 2, self.cols - 2)

        # 确保起点和终点是空地
        self.grid[self.start] = 0
        self.grid[self.goal] = 0
        # 也确保起点和终点旁边的格子是空地，方便通行
        if self.start[0] + 1 < self.rows:
            self.grid[self.start[0] + 1, self.start[1]] = 0
        if self.start[1] + 1 < self.cols:
            self.grid[self.start[0], self.start[1] + 1] = 0
        if self.goal[0] - 1 >= 0:
            self.grid[self.goal[0] - 1, self.goal[1]] = 0
        if self.goal[1] - 1 >= 0:
            self.grid[self.goal[0], self.goal[1] - 1] = 0

        return self.grid

    def _divide_maze(self, r1: int, c1: int, r2: int, c2: int):
        """递归分割迷宫区域"""
        if r2 - r1 < 2 or c2 - c1 < 2:
            return

        # 随机选择横向或纵向分割
        if r2 - r1 > c2 - c1:
            # 横向分割
            wall_row = random.randint(r1 + 1, r2 - 1)
            opening = random.randint(c1, c2)
            for c in range(c1, c2 + 1):
                if c != opening:
                    self.grid[wall_row, c] = 1
            self._divide_maze(r1, c1, wall_row - 1, c2)
            self._divide_maze(wall_row + 1, c1, r2, c2)
        else:
            # 纵向分割
            wall_col = random.randint(c1 + 1, c2 - 1)
            opening = random.randint(r1, r2)
            for r in range(r1, r2 + 1):
                if r != opening:
                    self.grid[r, wall_col] = 1
            self._divide_maze(r1, c1, r2, wall_col - 1)
            self._divide_maze(r1, wall_col + 1, r2, c2)

    def generate_narrow_passage(self, seed: int = None) -> np.ndarray:
        """
        生成窄通道场景（考验算法搜索能力）

        Returns:
            栅格地图
        """
        if seed is not None:
            np.random.seed(seed)

        self.grid = np.zeros((self.rows, self.cols), dtype=int)

        # 用横向墙壁制造窄通道，留出几个缺口
        for i in range(4, self.rows - 4, 5):
            # 随机留 1-2 个通道口
            num_openings = np.random.randint(1, 3)
            openings = np.random.choice(range(1, self.cols - 1),
                                        size=num_openings, replace=False)
            for j in range(1, self.cols - 1):
                if j not in openings:
                    self.grid[i, j] = 1

        # 添加一些纵向墙增加难度
        for j in range(4, self.cols - 4, 6):
            num_openings = np.random.randint(1, 3)
            openings = np.random.choice(range(1, self.rows - 1),
                                        size=num_openings, replace=False)
            for i in range(1, self.rows - 1):
                if i not in openings:
                    self.grid[i, j] = 1

        # 确保起点和终点是空地
        self.grid[self.start] = 0
        self.grid[self.goal] = 0

        return self.grid

    def generate_all_scenes(self) -> dict:
        """
        生成所有测试场景

        Returns:
            dict: {场景名称: (grid, start, goal)}
        """
        scenes = {}

        # 场景1: 低密度随机障碍 (10%)
        self.generate_random_obstacles(obstacle_ratio=0.10, seed=42)
        scenes['随机散点-低密度(10%)'] = (
            self.grid.copy(), self.start, self.goal
        )

        # 场景2: 中密度随机障碍 (20%)
        self.generate_random_obstacles(obstacle_ratio=0.20, seed=42)
        scenes['随机散点-中密度(20%)'] = (
            self.grid.copy(), self.start, self.goal
        )

        # 场景3: 高密度随机障碍 (30%)
        self.generate_random_obstacles(obstacle_ratio=0.30, seed=42)
        scenes['随机散点-高密度(30%)'] = (
            self.grid.copy(), self.start, self.goal
        )

        # 场景4: 迷宫式
        self.generate_maze(seed=123)
        scenes['迷宫式障碍'] = (self.grid.copy(), self.start, self.goal)

        # 场景5: 窄通道
        self.generate_narrow_passage(seed=456)
        scenes['窄通道场景'] = (self.grid.copy(), self.start, self.goal)

        return scenes


if __name__ == '__main__':
    gen = MapGenerator(30, 30)
    scenes = gen.generate_all_scenes()
    for name, (grid, s, g) in scenes.items():
        obstacle_count = np.sum(grid)
        total = grid.shape[0] * grid.shape[1]
        print(f'{name}: 障碍物 {obstacle_count}/{total} '
              f'({obstacle_count/total*100:.1f}%), 起点{s}, 终点{g}')
