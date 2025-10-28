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
        # 1. Đặt cờ self.is_running = True
        # 2. Gọi self.start_timer()
        # 3. Lấy matrix và num_cities từ self.tsp_problem
        # 4. Tạo mảng visited (ví dụ: [False] * num_cities)
        # 5. Tạo current_path ban đầu (ví dụ: [0])
        # 6. Đánh dấu visited[0] = True
        # ... (Code setup ở đây) ...
        
        print("Bắt đầu chạy Backtracking...")

        # --- TODO 2: Bắt đầu đệ quy ---
        # Gọi hàm _backtrack_recursive(...) lần đầu tiên
        # (Nên bọc trong try...except để bắt lỗi)
        try:
            # Viết code gọi hàm đệ quy của bạn ở đây
            # Ví dụ:
            # self._backtrack_recursive(
            #     current_city=0,
            #     count=1,
            #     current_cost=0,
            #     current_path=..., 
            #     visited=...,
            #     matrix=...,
            #     num_cities=...,
            #     update_callback=update_callback,
            #     sleep_time=sleep_time
            # )
            pass # Xóa pass khi viết code

        except Exception as e:
            print(f"Lỗi xảy ra trong Backtracking: {e}")
        
        # --- TODO 3: Hoàn thành ---
        # (Luôn chạy sau khi đệ quy kết thúc hoặc lỗi)
        
        # 1. Gọi self.stop_timer()
        # 2. Gọi finish_callback(self.best_path, self.min_cost, self.runtime)
        
        # ... (Code cleanup ở đây) ...
        
        print(f"Backtracking hoàn thành. Chi phí: {self.min_cost}, Thời gian: {self.runtime:.4f}s")

        
    def _backtrack_recursive(self, current_city, count, current_cost, current_path, visited, matrix, num_cities, update_callback, sleep_time):
        """
        Hàm đệ quy chính thực hiện việc tìm kiếm.
        Tất cả logic cốt lõi của thuật toán nằm ở đây.
        """

        # --- TODO 1: Kiểm tra dừng (Bắt buộc) ---
        # if not self.is_running:
        #     return
        
        # --- TODO 2: (Tùy chọn) Cắt tỉa (Pruning) ---
        # (Đây là nơi để thêm các kỹ thuật cải tiến)
        # Ví dụ: if current_cost >= self.min_cost: return
        
        # --- TODO 3: Điều kiện cơ bản (Base Case) ---
        # (Khi count == num_cities - tức là đã đi hết)
        # 1. Tính chi phí quay về 0 (cost_back_to_start)
        # 2. Tính total_cost
        # 3. So sánh if total_cost < self.min_cost:
        # 4.    Cập nhật self.min_cost, self.best_path
        # 5.    Gọi update_callback(self.best_path)
        # 6. return
        
        # --- TODO 4: Bước đệ quy (Recursive Step) ---
        # Lặp for next_city in range(num_cities):
        # 1.  Kiểm tra if (not visited[next_city] and ...điều kiện khác...):
        # 2.      (Bước "Thử")
        # 3.      Đánh dấu visited[next_city] = True
        # 4.      Thêm next_city vào current_path
        # 5.      (Tùy chọn) time.sleep(sleep_time)
        # 6.      Gọi đệ quy self._backtrack_recursive(...) với các tham số mới
        # 7.      (Bước "Quay lui")
        # 8.      Xóa next_city khỏi current_path (pop)
        # 9.      Đánh dấu visited[next_city] = False
        
        pass # Xóa pass khi viết code