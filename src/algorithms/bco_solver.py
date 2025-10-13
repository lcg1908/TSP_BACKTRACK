from .base_solver import BaseSolver
import random
import time
from itertools import permutations

class BCOSolver(BaseSolver):
    """Triển khai Bees Colony Optimization (BCO) cho TSP."""

    def __init__(self, problem, colony_size=10, max_iterations=5, max_trials=3):
        super().__init__(problem)
        self.colony_size = colony_size  # Số lượng Food Sources/Employed Bees
        self.max_iterations = max_iterations
        self.max_trials = max_trials    # Ngưỡng bỏ qua vị trí (Scout Bee trigger)

        # Danh sách các vị trí thức ăn (tour) và chất lượng (cost)
        self.food_sources = []
        self.source_costs = []
        self.trial_counts = [] # Số lần thử không cải thiện
        
        # Hàm phụ trợ để đảm bảo hoán vị hợp lệ (tương tự như trong PSO)
        self.generator = self._create_neighbor_swap

    def _initialize_colony(self):
        """Khởi tạo quần thể vị trí thức ăn ban đầu."""
        N = self.problem.N
        cities = list(range(N))

        self.best_cost = float('inf')
        self.food_sources = []
        self.source_costs = []
        self.trial_counts = [0] * self.colony_size

        for _ in range(self.colony_size):
            path = random.sample(cities, N)
            cost = self.problem.calculate_cost(path)
            
            self.food_sources.append(path)
            self.source_costs.append(cost)
            
            if cost < self.best_cost:
                self.best_cost = cost
                self.best_path = path.copy()

    def _create_neighbor_swap(self, path):
        """Tạo vị trí thức ăn lân cận bằng cách hoán đổi 2 thành phố ngẫu nhiên (2-opt swap đơn giản)."""
        new_path = list(path)
        N = self.problem.N
        idx1, idx2 = random.sample(range(N), 2)
        new_path[idx1], new_path[idx2] = new_path[idx2], new_path[idx1]
        return new_path

    def _employed_bee_phase(self):
        """Pha Ong Tìm kiếm (Employed Bees): Khám phá các vị trí lân cận."""
        for i in range(self.colony_size):
            current_path = self.food_sources[i]
            
            # Tạo một giải pháp lân cận mới (neighbor food source)
            new_path = self.generator(current_path)
            new_cost = self.problem.calculate_cost(new_path)
            
            # Áp dụng chiến lược tham lam: Nếu tốt hơn, chấp nhận nó
            if new_cost < self.source_costs[i]:
                self.food_sources[i] = new_path
                self.source_costs[i] = new_cost
                self.trial_counts[i] = 0 # Reset số lần thử
                
                # Cập nhật GBest
                if new_cost < self.best_cost:
                    self.best_cost = new_cost
                    self.best_path = new_path.copy()
            else:
                self.trial_counts[i] += 1

    def _onlooker_bee_phase(self):
        """Pha Ong Theo dõi (Onlooker Bees): Chọn vị trí dựa trên xác suất."""
        
        # 1. Tính toán xác suất chọn (Fitness / Tổng Fitness)
        # Vì ta đang tìm MIN (chi phí), ta dùng nghịch đảo chi phí (hoặc Chi phí tối đa - Chi phí)
        # Sử dụng phương pháp đơn giản: (Max_Cost + 1) - Current_Cost
        
        max_cost = max(self.source_costs)
        fitnesses = [(max_cost + 1) - cost for cost in self.source_costs]
        total_fitness = sum(fitnesses)
        
        if total_fitness == 0: return # Tránh chia cho 0
        
        probabilities = [f / total_fitness for f in fitnesses]

        # 2. Onlooker Bees chọn và khám phá
        for _ in range(self.colony_size):
            # Chọn một vị trí dựa trên xác suất (Roulette Wheel Selection)
            r = random.random()
            selected_index = -1
            cumulative_prob = 0
            
            for i in range(self.colony_size):
                cumulative_prob += probabilities[i]
                if r <= cumulative_prob:
                    selected_index = i
                    break
            
            if selected_index == -1: continue

            # Vị trí được chọn
            i = selected_index
            current_path = self.food_sources[i]
            new_path = self.generator(current_path)
            new_cost = self.problem.calculate_cost(new_path)

            # Áp dụng chiến lược tham lam: Nếu tốt hơn, chấp nhận nó
            if new_cost < self.source_costs[i]:
                self.food_sources[i] = new_path
                self.source_costs[i] = new_cost
                self.trial_counts[i] = 0
                
                if new_cost < self.best_cost:
                    self.best_cost = new_cost
                    self.best_path = new_path.copy()
            else:
                self.trial_counts[i] += 1

    def _scout_bee_phase(self):
        """Pha Ong Trinh sát (Scout Bees): Thay thế vị trí thức ăn đã cạn."""
        for i in range(self.colony_size):
            if self.trial_counts[i] >= self.max_trials:
                # Tạo vị trí thức ăn ngẫu nhiên mới
                N = self.problem.N
                new_path = random.sample(range(N), N)
                new_cost = self.problem.calculate_cost(new_path)
                
                self.food_sources[i] = new_path
                self.source_costs[i] = new_cost
                self.trial_counts[i] = 0 # Reset
                
                if new_cost < self.best_cost:
                    self.best_cost = new_cost
                    self.best_path = new_path.copy()

    def solve(self):
        """Chạy toàn bộ thuật toán BCO."""
        self.best_path = []
        self.best_cost = float('inf')
        
        start_time = time.time()
        self._initialize_colony()
        
        for iteration in range(self.max_iterations):
            self._employed_bee_phase()
            self._onlooker_bee_phase()
            self._scout_bee_phase()
            
            # print(f"Iter {iteration}: Cost={self.best_cost}") # Để debug

        self.runtime = time.time() - start_time
        return self.best_path, self.best_cost