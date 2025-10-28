# src/algorithms/base_solver.py
from abc import ABC, abstractmethod
import time

class BaseSolver(ABC):
    """Lớp cơ sở trừu tượng cho các bộ giải TSP."""
    def __init__(self, tsp_problem):
        self.tsp_problem = tsp_problem
        self.best_path = []
        self.min_cost = float('inf')
        self.runtime = 0
        self.is_running = False # Cờ để dừng thuật toán từ bên ngoài

    @abstractmethod
    def solve(self, update_callback=None, finish_callback=None, sleep_time=0.05):
        """
        Phương thức chính để chạy thuật toán.
        - update_callback(path): Gọi khi có đường đi tạm thời mới để vẽ.
        - finish_callback(path, cost, time): Gọi khi thuật toán hoàn tất.
        """
        pass
        
    def start_timer(self):
        self._start_time = time.time()
        
    def stop_timer(self):
        self.runtime = time.time() - self._start_time