# src/algorithms/backtrack_solver.py
import time
from .base_solver import BaseSolver

class BacktrackSolver(BaseSolver):
    """
    Triển khai thuật toán Backtracking (Quay lui)
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
        print("Bắt đầu chạy Backtrack cơ bản...")
        visited = [False] * num_cities
        current_path = [0] 
        visited[0] = True 
        
        try:
            self._backtrack_recursive(
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
            print(f"Lỗi: {e}")
        
        self.stop_timer()
        if finish_callback:
            finish_callback(self.best_path, self.min_cost, self.runtime)
        print(f"Backtrack cơ bản hoàn thành. Chi phí: {self.min_cost}, Thời gian: {self.runtime:.4f}s")

    def _backtrack_recursive(self, current_city, count, current_cost, current_path, visited, matrix, num_cities, update_callback, sleep_time):
        if not self.is_running:
            return
        
        # Vì đây là bản "Cơ bản" (Basic), NÊN BỎ đoạn cắt tỉa này 
        # để nó chạy chậm hơn bản Cải tiến, từ đó thấy rõ sự khác biệt trên biểu đồ.
        # if current_cost >= self.min_cost:
        #    return
        
        # Base Case: Đã đi hết các thành phố
        if count == num_cities:
            cost_back_to_start = matrix[current_city][0]
            
            # Kiểm tra nếu không có đường về (Vô cực) thì bỏ qua
            if cost_back_to_start == float('inf'):
                return

            total_cost = current_cost + cost_back_to_start
            
            if total_cost < self.min_cost:
                self.min_cost = total_cost
                self.best_path = current_path + [0]
                if update_callback:
                    update_callback(self.best_path)
            return
        
        # Recursive Step
        for next_city in range(num_cities):
            if not visited[next_city]:
                # Kiểm tra chi phí trước khi đi
                cost_to_next = matrix[current_city][next_city]
                
                # Nếu không có đường đi (inf), bỏ qua ngay (Không đệ quy vào nhánh này)
                if cost_to_next == float('inf'):
                    continue

                visited[next_city] = True
                current_path.append(next_city)
                
                new_cost = current_cost + cost_to_next
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                self._backtrack_recursive(
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
