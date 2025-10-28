# src/algorithms/aco_solver.py
import time
import random
import math
from .base_solver import BaseSolver # Sử dụng import tương đối

class ACOSolver(BaseSolver):
    """
    Triển khai thuật toán Tối ưu bầy kiến (Ant Colony Optimization - ACO).
    
    Người lập trình sẽ điền logic thuật toán vào đây, bao gồm:
    1. Khởi tạo ma trận Pheromone.
    2. Vòng lặp chính (theo iterations).
    3. Logic cho từng con kiến xây dựng đường đi (dựa trên Pheromone).
    4. Logic cập nhật Pheromone (bay hơi và thêm mới).
    """

    def __init__(self, tsp_problem):
        """Khởi tạo, gọi lớp cha và định nghĩa các tham số của ACO."""
        super().__init__(tsp_problem)
        
        # --- TODO 1: Định nghĩa các tham số cho ACO ---
        # Đây là các tham số kinh điển của ACO
        self.num_ants = 20           # Số lượng kiến trong mỗi vòng lặp
        self.max_iterations = 100    # Số vòng lặp (thế hệ)
        
        self.alpha = 1.0  # Tầm quan trọng của Pheromone
        self.beta = 2.0   # Tầm quan trọng của Heuristic (khoảng cách)
        self.rho = 0.5    # Tốc độ bay hơi Pheromone (Evaporation rate)
        self.Q = 100      # Hằng số Pheromone (dùng khi kiến "thả" Pheromone)
        
        self.pheromone_matrix = []
        self.heuristic_matrix = [] # Ma trận heuristic (thường là 1/distance)

    def solve(self, update_callback=None, finish_callback=None, sleep_time=0.05):
        """
        Phương thức chính để chạy thuật toán.
        Quản lý vòng lặp chính của các thế hệ (iterations).
        """
        
        # --- TODO 2: Thiết lập ban đầu ---
        self.is_running = True
        self.start_timer()

        matrix = self.tsp_problem.dist_matrix
        num_cities = self.tsp_problem.num_cities

        if num_cities == 0:
            self.stop_timer()
            if finish_callback:
                finish_callback(self.best_path, self.min_cost, self.runtime)
            return

        # Khởi tạo ma trận Pheromone và Heuristic
        self._initialize_matrices(num_cities, matrix)
        
        print("Bắt đầu chạy ACO...")

        # --- TODO 3: Vòng lặp chính (Main Loop) ---
        try:
            for iteration in range(self.max_iterations):
                
                # 3.1. Kiểm tra dừng (Bắt buộc)
                if not self.is_running:
                    print("ACO bị dừng.")
                    break
                
                # 3.2. Cho tất cả kiến xây dựng đường đi
                all_ant_paths = self._construct_ant_solutions(num_cities, matrix)
                
                # 3.3. Cập nhật Pheromone (Bay hơi + Thêm mới)
                self._update_pheromones(all_ant_paths)

                # 3.4. (Tùy chọn) Cập nhật UI nếu tìm thấy kết quả tốt nhất mới
                # (Logic tìm best_path mới thường nằm trong _construct_ant_solutions
                #  hoặc _update_pheromones)
                # if new_global_best_found and update_callback:
                #    update_callback(list(self.best_path))

                # 3.5. (Tùy chọn) Làm chậm mô phỏng
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
                # print(f"Iteration {iteration}: Best Cost = {self.min_cost}")

        except Exception as e:
            print(f"Lỗi xảy ra trong ACO: {e}")
        
        # --- TODO 4: Hoàn thành ---
        self.stop_timer()
        if finish_callback:
            finish_callback(self.best_path, self.min_cost, self.runtime)
        
        print(f"ACO hoàn thành. Chi phí: {self.min_cost}, Thời gian: {self.runtime:.4f}s")

    def _initialize_matrices(self, num_cities, matrix):
        """Khởi tạo ma trận Pheromone và Heuristic."""
        # --- TODO 5: Khởi tạo Pheromone ---
        # Thường là một giá trị nhỏ, hằng số (ví dụ: 1.0) cho tất cả các cạnh
        self.pheromone_matrix = [[1.0] * num_cities for _ in range(num_cities)]
        
        # --- TODO 6: Khởi tạo Heuristic ---
        # Thường là (1 / distance). Cẩn thận với chia cho 0.
        self.heuristic_matrix = [[0.0] * num_cities for _ in range(num_cities)]
        for i in range(num_cities):
            for j in range(num_cities):
                if i != j and matrix[i][j] > 0:
                    self.heuristic_matrix[i][j] = 1.0 / matrix[i][j]
                else:
                    self.heuristic_matrix[i][j] = 0.0 # Hoặc 1 giá trị rất nhỏ

    def _construct_ant_solutions(self, num_cities, matrix):
        """Cho tất cả self.num_ants con kiến xây dựng đường đi."""
        all_ant_paths = []
        
        for ant in range(self.num_ants):
            # --- TODO 7: Logic cho 1 con kiến ---
            # 1. Chọn 1 thành phố bắt đầu ngẫu nhiên
            # 2. Xây dựng đường đi (build_path) bằng cách lặp 
            #    chọn thành phố tiếp theo dựa trên xác suất
            # 3. Hàm tính xác suất: _calculate_probabilities()
            # 4. Tính toán chi phí của đường đi
            # 5. Lưu (path, cost) vào all_ant_paths
            # 6. *Quan trọng*: Cập nhật self.min_cost và self.best_path
            #    NGAY LẬP TỨC nếu con kiến này tìm thấy đường đi tốt nhất toàn cục
            
            # (Code ví dụ)
            # path, cost = self._build_single_ant_path(num_cities, matrix)
            # all_ant_paths.append((path, cost))
            # if cost < self.min_cost:
            #     self.min_cost = cost
            #     self.best_path = path
            
            pass # Xóa pass khi viết code

        return all_ant_paths

    def _calculate_probabilities(self, current_city, visited, num_cities):
        """Tính xác suất để một con kiến di chuyển từ current_city đến các thành phố khác."""
        probabilities = [0.0] * num_cities
        total_prob = 0.0
        
        # --- TODO 8: Tính toán tử số (Pheromone^alpha * Heuristic^beta) ---
        # 1. Lặp qua tất cả các thành phố `next_city`
        # 2. Nếu `next_city` chưa thăm:
        # 3.    Tính: (pheromone[current_city][next_city] ** self.alpha) * #             (heuristic[current_city][next_city] ** self.beta)
        # 4.    Lưu vào probabilities[next_city]
        # 5.    Cộng dồn vào total_prob
        
        # --- TODO 9: Tính xác suất cuối cùng ---
        # 1. Lặp lại qua các thành phố `next_city`
        # 2. Nếu total_prob > 0:
        # 3.    probabilities[next_city] = probabilities[next_city] / total_prob
        # 4. Trả về mảng probabilities
        
        return probabilities
        
    def _build_single_ant_path(self, num_cities, matrix):
        """Logic cho 1 con kiến xây dựng 1 đường đi hoàn chỉnh."""
        # --- TODO 10: Logic xây dựng đường đi ---
        # 1. Chọn TP bắt đầu (start_city)
        # 2. Khởi tạo path = [start_city], visited = [False]*n, visited[start_city]=True
        # 3. Lặp (num_cities - 1) lần:
        # 4.    current_city = path[-1]
        # 5.    Gọi probs = self._calculate_probabilities(current_city, visited, ...)
        # 6.    Chọn `next_city` dựa trên "bánh xe roulette" (random.choices)
        # 7.    append `next_city` vào path, đánh dấu visited
        # 8. Thêm start_city vào cuối path để hoàn thành chu trình
        # 9. Tính tổng chi phí (self.tsp_problem.get_path_cost(path))
        # 10. Trả về (path, cost)
        
        path = [] # Xóa dòng này
        cost = 0  # Xóa dòng này
        return (path, cost) # Xóa dòng này

    def _update_pheromones(self, all_ant_paths):
        """Cập nhật ma trận Pheromone: Bay hơi + Thả Pheromone mới."""
        
        num_cities = self.tsp_problem.num_cities

        # --- TODO 11: Bay hơi (Evaporation) ---
        # 1. Lặp qua ma trận pheromone (i, j)
        # 2. self.pheromone_matrix[i][j] *= (1.0 - self.rho)
        
        # --- TODO 12: Thả Pheromone mới (Deposition) ---
        # 1. Lặp qua từng (path, cost) trong `all_ant_paths`
        # 2. Tính lượng pheromone_delta = self.Q / cost
        # 3. Lặp qua các cạnh (i, j) trong `path`:
        # 4.    self.pheromone_matrix[i][j] += pheromone_delta
        # 5.    (Nếu là TSP bất đối xứng, chỉ [i][j], nếu đối xứng,
        #       thì cả [i][j] và [j][i])
        
        pass # Xóa pass khi viết code