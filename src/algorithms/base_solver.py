# src/algorithms/base_solver.py
from abc import ABC, abstractmethod 
import time

class BaseSolver(ABC):
    """
    Lớp cơ sở trừu tượng (Abstract Base Class) định nghĩa Interface chung cho các thuật toán giải TSP.
    Mục tiêu:
    1. Đảm bảo tính thống nhất (Consistency): Tất cả thuật toán đều có cấu trúc input/output giống nhau.
    2. Giao diện (GUI) có thể gọi phương thức .solve() mà không cần quan tâm cụ thể đó là thuật toán nào
    """
    
    def __init__(self, tsp_problem):
        """
        Khởi tạo các thuộc tính chung (Common Attributes) cho mọi bộ giải.
        Args:
            tsp_problem: Đối tượng chứa dữ liệu bài toán (Distance Matrix, số lượng thành phố).
        """
        # Đưa dữ liệu bài toán vào thuật toán
        self.tsp_problem = tsp_problem 
        
        # Các biến lưu trữ trạng thái và kết quả tối ưu
        self.best_path = []            # Lưu trữ lộ trình tối ưu tìm được
        self.min_cost = float('inf')   # Chi phí tối ưu (Khởi tạo là dương vô cùng)
        self.runtime = 0               # Thời gian thực thi
        self.is_running = False        # Cờ kiểm soát luồng (Control Flag) để xử lý dừng/chạy
        self._start_time = 0           # Biến nội bộ để tính toán thời gian

    @abstractmethod
    def solve(self, update_callback=None, finish_callback=None, sleep_time=0.05):
        """
        Phương thức trừu tượng (Abstract Method) - Định nghĩa "Contract" (Hợp đồng).
        - Đây là phương thức thuần ảo, không có cài đặt cụ thể ở lớp cha.
        - BẮT BUỘC: Các lớp con (Subclasses) kế thừa phải Override (ghi đè) phương thức này 
          để triển khai logic thuật toán cụ thể.
        
        Args:
            update_callback (func): Hàm callback để cập nhật UI thời gian thực (Visualization).
            finish_callback (func): Hàm callback trả về kết quả cuối cùng khi thuật toán kết thúc.
            sleep_time (float): Thời gian delay giữa các bước lặp (để tạo hiệu ứng animation).
        """
        pass
        
    # Các phương thức tiện ích dùng chung ---
    def start_timer(self):
        """Bắt đầu bộ đếm thời gian thực thi (Profiling)."""
        self._start_time = time.time()
        
    def stop_timer(self):
        """
        Kết thúc bộ đếm và tính toán tổng thời gian thực thi (Runtime).
        Kết quả được lưu vào thuộc tính self.runtime.
        """
        self.runtime = time.time() - self._start_time
