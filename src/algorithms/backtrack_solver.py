from .base_solver import BaseSolver
from itertools import permutations
import time

class BacktrackSolver(BaseSolver):
    """Sử dụng Backtracking để tìm lời giải chính xác."""

    def solve(self):
        # Đặt lại best_cost và runtime
        self.best_path = []
        self.best_cost = float('inf')
        
        start_time = time.time()
        N = self.problem.N
        
        # Cố định điểm đầu là 0, vét cạn các hoán vị còn lại
        start_city = 0
        other_cities = list(range(1, N))
        
        # Duyệt qua tất cả các thứ tự đi qua các thành phố còn lại (N-1)!
        for path_suffix in permutations(other_cities):
            current_path = [start_city] + list(path_suffix)
            cost = self.problem.calculate_cost(current_path)
            
            if cost < self.best_cost:
                self.best_cost = cost
                self.best_path = current_path
        
        self.runtime = time.time() - start_time
        return self.best_path, self.best_cost