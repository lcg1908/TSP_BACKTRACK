# src/algorithms/backtrack_solver.py
import time
from .base_solver import BaseSolver

class BacktrackSolver(BaseSolver):
    """
    Triển khai thuật toán Backtracking (Quay lui).
    
    Sinh viên sẽ điền logic thuật toán của mình vào các hàm
    solve() và _backtrack_recursive()
    """

    def __init__(self, tsp_problem):
        """Khởi tạo, chỉ cần gọi lớp cha."""
        super().__init__(tsp_problem)
        
        # --- (Có thể thêm các biến riêng của Backtrack ở đây nếu cần) ---
        # ví dụ: self.some_variable = ...


    def solve(self, update_callback=None, finish_callback=None, sleep_time=0.05):
        """
        Phương thức chính để chạy thuật toán.
        Đây là nơi "setup" và "cleanup" cho hàm đệ quy.
        """
        
        # --- TODO 1: Thiết lập ban đầu ---
        self.is_running = True
        self.start_timer()
        
        matrix = self.tsp_problem.dist_matrix
        num_cities = self.tsp_problem.num_cities
        
        # Kiểm tra nếu không có dữ liệu
        if num_cities == 0:
            self.stop_timer()
            if finish_callback:
                finish_callback(self.best_path, self.min_cost, self.runtime)
            return
        
        # Tạo mảng visited và current_path ban đầu
        visited = [False] * num_cities
        current_path = [0]  # Bắt đầu từ thành phố 0
        visited[0] = True  # Đánh dấu thành phố 0 đã thăm
        
        print("Bắt đầu chạy Backtracking...")

        # --- TODO 2: Bắt đầu đệ quy ---
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
            print(f"Lỗi xảy ra trong Backtracking: {e}")
        
        # --- TODO 3: Hoàn thành ---
        self.stop_timer()
        if finish_callback:
            finish_callback(self.best_path, self.min_cost, self.runtime)
        
        print(f"Backtracking hoàn thành. Chi phí: {self.min_cost}, Thời gian: {self.runtime:.4f}s")

        
    def _backtrack_recursive(self, current_city, count, current_cost, current_path, visited, matrix, num_cities, update_callback, sleep_time):
        """
        Hàm đệ quy chính thực hiện việc tìm kiếm.
        Tất cả logic cốt lõi của thuật toán nằm ở đây.
        """

        # --- TODO 1: Kiểm tra dừng (Bắt buộc) ---
        if not self.is_running:
            return
        
        # --- TODO 2: (Tùy chọn) Cắt tỉa (Pruning) ---
        # Nếu chi phí hiện tại đã lớn hơn hoặc bằng chi phí tốt nhất, không cần tiếp tục
        if current_cost >= self.min_cost:
            return
        
        # --- TODO 3: Điều kiện cơ bản (Base Case) ---
        # Khi đã đi hết tất cả các thành phố (count == num_cities)
        if count == num_cities:
            # Tính chi phí quay về thành phố 0 (điểm xuất phát)
            cost_back_to_start = matrix[current_city][0]
            total_cost = current_cost + cost_back_to_start
            
            # So sánh và cập nhật nếu tốt hơn
            if total_cost < self.min_cost:
                self.min_cost = total_cost
                # Tạo đường đi hoàn chỉnh (thêm thành phố 0 ở cuối để tạo chu trình)
                self.best_path = current_path + [0]
                
                # Gọi callback để cập nhật giao diện
                if update_callback:
                    update_callback(self.best_path)
            return
        
        # --- TODO 4: Bước đệ quy (Recursive Step) ---
        # Thử từng thành phố tiếp theo
        for next_city in range(num_cities):
            # Chỉ thử các thành phố chưa thăm
            if not visited[next_city]:
                # Bước "Thử": Thêm thành phố vào đường đi
                visited[next_city] = True
                current_path.append(next_city)
                
                # Tính chi phí đi từ thành phố hiện tại đến thành phố tiếp theo
                cost_to_next = matrix[current_city][next_city]
                new_cost = current_cost + cost_to_next
                
                # (Tùy chọn) Sleep để làm chậm quá trình (cho việc visualization)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                # Gọi đệ quy với trạng thái mới
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
                
                # Bước "Quay lui": Xóa thành phố khỏi đường đi và đánh dấu chưa thăm
                current_path.pop()  # Xóa thành phố cuối cùng
                visited[next_city] = False