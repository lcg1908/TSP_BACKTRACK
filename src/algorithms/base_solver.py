import time

class BaseSolver:
    """Lớp cơ sở trừu tượng cho các thuật toán giải TSP."""
    
    def __init__(self, problem):
        self.problem = problem
        self.best_path = []
        self.best_cost = float('inf')
        self.runtime = 0.0

    def solve(self):
        """Phương thức chính để chạy thuật toán (cần được ghi đè)."""
        start_time = time.time()
        # Logic giải quyết thuật toán ở đây
        # ...
        self.runtime = time.time() - start_time
        return self.best_path, self.best_cost