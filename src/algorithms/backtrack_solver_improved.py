# src/algorithms/backtrack_solver_improved.py
import time
from .base_solver import BaseSolver

class BacktrackSolverImproved(BaseSolver):
    """
    Backtracking cải tiến dùng:
      - LCV (Least Cost Value)
      - Branch & Bound (cắt tỉa theo giới hạn dưới)
    """

    def __init__(self, tsp_problem):
        super().__init__(tsp_problem)

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

        visited = [False] * num_cities
        current_path = [0]
        visited[0] = True

        print("Bắt đầu Backtracking cải tiến ...")

        # Khởi tạo chi phí trung bình tối thiểu của mỗi hàng — dùng cho bound
        self.min_edge = [min([d for d in row if d > 0], default=0) for row in matrix]

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
            print(f"Lỗi trong quá trình chạy: {e}")

        self.stop_timer()
        if finish_callback:
            finish_callback(self.best_path, self.min_cost, self.runtime)

        print(f"Hoàn tất! Chi phí tối thiểu: {self.min_cost}, Thời gian: {self.runtime:.4f}s")

    
    def _backtrack_recursive_improved(self, current_city, count, current_cost, current_path,
                   visited, matrix, num_cities, update_callback, sleep_time):

        if not self.is_running:
            return

        # Cắt tỉa 1: Nếu cost hiện tại đã >= best → dừng
        if current_cost >= self.min_cost:
            return

        # Cắt tỉa 2: Tính giới hạn dưới (Bound)
        lower_bound = self._estimate_lower_bound(current_cost, visited)
        if lower_bound >= self.min_cost:
            return

        # Nếu đã đi hết các thành phố
        if count == num_cities:
            total_cost = current_cost + matrix[current_city][0]
            if total_cost < self.min_cost:
                self.min_cost = total_cost
                self.best_path = current_path + [0]
                if update_callback:
                    update_callback(self.best_path)
            return

        # Sắp xếp theo LCV — thành phố có cạnh chi phí nhỏ hơn đi trước
        next_cities = self._sort_next_cities_lcv(current_city, visited, matrix, num_cities)

        for next_city in next_cities:
            if visited[next_city] or matrix[current_city][next_city] <= 0:
                continue

            visited[next_city] = True
            current_path.append(next_city)
            new_cost = current_cost + matrix[current_city][next_city]

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

            current_path.pop()
            visited[next_city] = False

    def _estimate_lower_bound(self, current_cost, visited):
        """
        Tính giới hạn dưới: cost hiện tại + tổng chi phí cạnh thấp nhất của các thành phố chưa thăm.
        """
        remaining_min_cost = sum(self.min_edge[i] for i, v in enumerate(visited) if not v)
        return current_cost + remaining_min_cost

    def _sort_next_cities_lcv(self, current_city, visited, matrix, num_cities):
        """
        LCV: Ưu tiên thành phố có chi phí đi thấp hơn trước.
        """
        unvisited = [i for i in range(num_cities) if not visited[i] and matrix[current_city][i] > 0]
        sorted_cities = sorted(unvisited, key=lambda c: matrix[current_city][c])
        return sorted_cities

     
