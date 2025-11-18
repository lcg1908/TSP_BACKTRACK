# src/algorithms/backtrack_solver_improved.py
import time
from .base_solver import BaseSolver

class BacktrackSolverImproved(BaseSolver):
    """
    Backtracking cải tiến dùng:
      - LCV (Least Cost Value) - Sắp xếp thứ tự duyệt
      - Branch & Bound (Cắt tỉa theo giới hạn dưới)
    """

    def __init__(self, tsp_problem):
        super().__init__(tsp_problem)
        self.min_edge = []

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
        print("Bắt đầu chạy Backtrack cải tiến...")
        visited = [False] * num_cities
        current_path = [0]
        visited[0] = True

        # --- TÍNH TOÁN TRƯỚC CHO BOUND ---
        # Tìm cạnh nhỏ nhất đi ra từ mỗi thành phố (bỏ qua 0 và inf)
        self.min_edge = []
        for row in matrix:
            valid_costs = [c for c in row if c > 0 and c != float('inf')]
            self.min_edge.append(min(valid_costs) if valid_costs else 0)

        try:
            self._backtrack_recursive_improved(
                current_city=0,
                count=1,
                current_cost=0,
                current_path=current_path,
                visited=visited,
                matrix=matrix,
                num_cities=num_cities,
                update_callback=update_callback,
                sleep_time=sleep_time
            )
        except Exception as e:
            print(f"Lỗi trong quá trình chạy Improved: {e}")

        self.stop_timer()
        if finish_callback:
            finish_callback(self.best_path, self.min_cost, self.runtime)

        print(f"Backtrack cải tiến hoàn thành. Chi phí: {self.min_cost}, Thời gian: {self.runtime:.4f}s")

    def _backtrack_recursive_improved(self, current_city, count, current_cost, current_path,
                                   visited, matrix, num_cities, update_callback, sleep_time):

        if not self.is_running:
            return

        # --- CẮT TỈA 1: So sánh trực tiếp ---
        if current_cost >= self.min_cost:
            return

        # --- CẮT TỈA 2: Tính giới hạn dưới (Lower Bound) ---
        # Bound = Chi phí đã đi + (Tổng các cạnh nhỏ nhất của các đỉnh CHƯA đi)
        # Điều này ước lượng kịch bản "lạc quan nhất"
        lower_bound = current_cost + sum(self.min_edge[i] for i in range(num_cities) if not visited[i])
        
        if lower_bound >= self.min_cost:
            return

        # --- BASE CASE: Đã đi hết ---
        if count == num_cities:
            cost_back = matrix[current_city][0]
            # Kiểm tra đường về
            if cost_back == float('inf'):
                return

            total_cost = current_cost + cost_back
            if total_cost < self.min_cost:
                self.min_cost = total_cost
                self.best_path = current_path + [0]
                if update_callback:
                    update_callback(self.best_path)
            return

        # --- LCV HEURISTIC: Sắp xếp thứ tự duyệt ---
        # Ưu tiên đi sang thành phố có chi phí thấp trước
        # Điều này giúp tìm ra một lời giải tốt (Good Solution) sớm hơn -> Cắt tỉa hiệu quả hơn
        next_cities = self._get_sorted_next_cities(current_city, visited, matrix, num_cities)

        for next_city in next_cities:
            cost_move = matrix[current_city][next_city]
            
            # Bỏ qua nếu không có đường đi
            if cost_move == float('inf'):
                continue

            visited[next_city] = True
            current_path.append(next_city)
            new_cost = current_cost + cost_move

            if sleep_time > 0:
                time.sleep(sleep_time)

            self._backtrack_recursive_improved(
                current_city=next_city,
                count=count + 1,
                current_cost=new_cost,
                current_path=current_path,
                visited=visited,
                matrix=matrix,
                num_cities=num_cities,
                update_callback=update_callback,
                sleep_time=sleep_time
            )

            # Backtrack
            current_path.pop()
            visited[next_city] = False

    def _get_sorted_next_cities(self, current_city, visited, matrix, num_cities):
        """
        Trả về danh sách các thành phố tiếp theo chưa thăm, 
        được sắp xếp tăng dần theo chi phí đi từ current_city.
        """
        candidates = []
        for i in range(num_cities):
            if not visited[i]:
                cost = matrix[current_city][i]
                if cost != float('inf'): # Chỉ thêm nếu có đường đi
                    candidates.append((i, cost))
        
        # Sắp xếp theo chi phí (thành phần thứ 2 của tuple)
        candidates.sort(key=lambda x: x[1])
        
        # Trả về danh sách chỉ số thành phố
        return [c[0] for c in candidates]
