# src/algorithms/aco_solver.py
import time
import random
import math
from .base_solver import BaseSolver 

class ACOSolver(BaseSolver):

    def __init__(self, tsp_problem):
        super().__init__(tsp_problem)

        self.num_ants = 20
        self.max_iterations = 100
    
        self.alpha = 1.0  
        self.beta = 2.0   
        self.rho = 0.5    
        self.Q = 100      
        
        self.pheromone_matrix = []
        self.heuristic_matrix = [] 

    def solve(self, update_callback=None, finish_callback=None, sleep_time=0):
        self.is_running = True
        self.start_timer()

        matrix = self.tsp_problem.dist_matrix
        num_cities = self.tsp_problem.num_cities

        if num_cities == 0:
            self.stop_timer()
            if finish_callback:
                finish_callback(self.best_path, self.min_cost, self.runtime)
            return

        self._initialize_matrices(num_cities, matrix)
        
        print("Bắt đầu chạy ACO...")

        try:
            for iteration in range(self.max_iterations):

                if not self.is_running:
                    print("ACO bị dừng.")
                    break
                
                # Xây dựng giải pháp cho đàn kiến
                all_ant_paths = self._construct_ant_solutions(num_cities, matrix)

                # Cập nhật mùi dựa trên các giải pháp HỢP LỆ
                if all_ant_paths:
                    self._update_pheromones(all_ant_paths, num_cities)

                # Cập nhật giao diện (Callback) với lộ trình tốt nhất tìm thấy đến giờ
                # (Tùy chọn: chỉ gọi callback mỗi 5-10 vòng để đỡ lag GUI)
                if update_callback and self.best_path:
                   update_callback(self.best_path)

                if sleep_time > 0:
                    time.sleep(sleep_time)

        except Exception as e:
            print(f"Lỗi xảy ra trong ACO: {e}")
        
        self.stop_timer()
        if finish_callback:
            finish_callback(self.best_path, self.min_cost, self.runtime)
        print(f"ACO hoàn thành. Chi phí: {self.min_cost}, Thời gian: {self.runtime:.4f}s")

    def _initialize_matrices(self, num_cities, matrix):
        # Khởi tạo pheromone ban đầu
        self.pheromone_matrix = [[1.0] * num_cities for _ in range(num_cities)]
        # Khởi tạo heuristic (Visibility = 1 / distance)
        self.heuristic_matrix = [[0.0] * num_cities for _ in range(num_cities)]
        for i in range(num_cities):
            for j in range(num_cities):
                if i != j:
                    dist = matrix[i][j]
                    # [SỬA] Chỉ tính heuristic nếu có đường đi và > 0
                    if dist != float('inf') and dist > 0:
                        self.heuristic_matrix[i][j] = 1.0 / dist
                    else:
                        self.heuristic_matrix[i][j] = 0.0

    def _construct_ant_solutions(self, num_cities, matrix):
        all_ant_paths = []
        
        for _ in range(self.num_ants):
            if not self.is_running:
                break

            path, cost = self._build_single_ant_path(num_cities, matrix)
            
            # [SỬA] Chỉ chấp nhận kiến về đích thành công (cost != inf)
            if path is not None and cost != float('inf'):
                all_ant_paths.append((path, cost))

                # Cập nhật Global Best
                if cost < self.min_cost:
                    self.min_cost = cost
                    self.best_path = path

        return all_ant_paths

    def _calculate_probabilities(self, current_city, visited, num_cities):
        probabilities = [0.0] * num_cities
        total_prob = 0.0
        
        for next_city in range(num_cities):
            # Chỉ xét các thành phố chưa thăm VÀ có đường đi (heuristic > 0)
            if not visited[next_city] and self.heuristic_matrix[current_city][next_city] > 0:
                pher = self.pheromone_matrix[current_city][next_city] ** self.alpha
                heu = self.heuristic_matrix[current_city][next_city] ** self.beta
                
                prob = pher * heu
                probabilities[next_city] = prob
                total_prob += prob

        # [QUAN TRỌNG] Nếu tổng xác suất = 0 (Kiến bị kẹt, không còn đường đi), trả về None
        if total_prob == 0:
            return None

        # Chuẩn hóa
        for city in range(num_cities):
            probabilities[city] /= total_prob

        return probabilities
        
    def _build_single_ant_path(self, num_cities, matrix):
        start_city = 0
        path = [start_city]
        visited = [False] * num_cities
        visited[start_city] = True

        current_cost = 0.0

        for _ in range(num_cities - 1):
            if not self.is_running:
                return None, float('inf')

            current = path[-1]
            probs = self._calculate_probabilities(current, visited, num_cities)

            # [SỬA] Nếu probs là None nghĩa là kiến bị kẹt -> Hủy lộ trình này
            if probs is None:
                return None, float('inf')

            next_city = self._roulette_select(probs)
            
            # Cộng chi phí
            cost_move = matrix[current][next_city]
            current_cost += cost_move

            path.append(next_city)
            visited[next_city] = True

        # [SỬA] Kiểm tra đường quay về điểm xuất phát
        last_city = path[-1]
        cost_back = matrix[last_city][start_city]
        
        if cost_back == float('inf'):
            return None, float('inf') # Không về được đích -> Hủy

        path.append(start_city)
        current_cost += cost_back

        return (path, current_cost)

    def _roulette_select(self, probabilities):
        r = random.random()
        cumulative = 0.0
        for city, prob in enumerate(probabilities):
            cumulative += prob
            if r <= cumulative:
                return city
        
        # Fallback an toàn
        for i in range(len(probabilities) - 1, -1, -1):
            if probabilities[i] > 0: return i
        return 0

    def _update_pheromones(self, all_ant_paths, num_cities):
        # 1. Bay hơi (Evaporation)
        for i in range(num_cities):
            for j in range(num_cities):
                self.pheromone_matrix[i][j] *= (1.0 - self.rho)
                # Giữ mức tối thiểu để tránh lỗi chia cho 0 hoặc kẹt cục bộ
                if self.pheromone_matrix[i][j] < 1e-10:
                     self.pheromone_matrix[i][j] = 1e-10

        # 2. Tăng cường mùi (Deposition)
        for path, cost in all_ant_paths:
            if cost <= 0: continue 
            
            pheromone_delta = self.Q / cost

            for k in range(len(path) - 1):
                i = path[k]
                j = path[k+1]
                
                # [SỬA] Chỉ cập nhật chiều thuận i -> j
                self.pheromone_matrix[i][j] += pheromone_delta
                
                # [QUAN TRỌNG] BỎ dòng cập nhật j -> i để hỗ trợ Asymmetric TSP
                # self.pheromone_matrix[j][i] += pheromone_delta  <-- XÓA DÒNG NÀY
