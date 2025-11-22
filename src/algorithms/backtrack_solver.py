# src/algorithms/backtrack_solver.py

import time
from .base_solver import BaseSolver


class BacktrackSolver(BaseSolver):
    """
    Triển khai thuật toán Backtracking (Quay lui) để giải bài toán TSP.
    Đây là phiên bản CƠ BẢN (không cắt tỉa), dùng để so sánh tốc độ
    với phiên bản Backtracking cải tiến.
    """

    def __init__(self, tsp_problem):
        # Gọi hàm khởi tạo lớp cha (BaseSolver)
        super().__init__(tsp_problem)

    def solve(self, update_callback=None, finish_callback=None, sleep_time=0):
        """
        Hàm chính để chạy thuật toán Backtracking.

        - update_callback: callback cập nhật đường đi tạm thời tốt nhất (để GUI hiển thị)
        - finish_callback: callback khi chạy xong (trả kết quả cho GUI)
        - sleep_time: thời gian nghỉ giữa các bước (dùng để làm chậm cho GUI quan sát)
        """
        self.is_running = True
        self.start_timer()  # Bắt đầu đo thời gian

        matrix = self.tsp_problem.dist_matrix
        num_cities = self.tsp_problem.num_cities

        # Nếu không có thành phố nào → dừng luôn
        if num_cities == 0:
            self.stop_timer()
            if finish_callback:
                finish_callback(self.best_path, self.min_cost, self.runtime)
            return

        print("Bắt đầu chạy Backtrack cơ bản...")

        # Mảng đánh dấu các thành phố đã đi
        visited = [False] * num_cities

        # Bắt đầu từ thành phố 0
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

        # Khi chạy xong → dừng timer
        self.stop_timer()

        # Trả kết quả cho GUI
        if finish_callback:
            finish_callback(self.best_path, self.min_cost, self.runtime)

        print(f"Backtrack cơ bản hoàn thành. Chi phí: {self.min_cost}, Thời gian: {self.runtime:.4f}s")

    def _backtrack_recursive(self, current_city, count, current_cost,
                             current_path, visited, matrix, num_cities,
                             update_callback, sleep_time):
        """
        Hàm đệ quy chính của thuật toán Backtracking.

        - current_city: thành phố hiện tại
        - count: số lượng thành phố đã đi được
        - current_cost: tổng chi phí đến hiện tại
        - current_path: đường đi hiện tại
        - visited: danh dấu thành phố đã đến
        """

        # Nếu người dùng bấm STOP → dừng đệ quy
        if not self.is_running:
            return

        # (Bản cơ bản KHÔNG cắt tỉa nhánh)
        # Vì để chứng minh tốc độ chậm hơn bản cải tiến.
        # if current_cost >= self.min_cost:
        #     return

        # ======== BASE CASE ========
        # Khi đã đi qua hết tất cả thành phố
        if count == num_cities:

            # Chi phí quay về thành phố xuất phát
            cost_back_to_start = matrix[current_city][0]

            # Nếu không có đường về (inf) → bỏ
            if cost_back_to_start == float('inf'):
                return

            total_cost = current_cost + cost_back_to_start

            # Nếu tìm được hành trình tốt hơn → update
            if total_cost < self.min_cost:
                self.min_cost = total_cost
                self.best_path = current_path + [0]

                # Callback để GUI update đường đi tốt nhất
                if update_callback:
                    update_callback(self.best_path)

            return  # Kết thúc nhánh đệ quy

        # ======== RECURSION STEP ========
        # Thử đi qua từng thành phố tiếp theo
        for next_city in range(num_cities):

            # Chỉ xem thành phố chưa đi
            if not visited[next_city]:

                cost_to_next = matrix[current_city][next_city]

                # Nếu giữa 2 thành phố không có đường (inf) → bỏ qua
                if cost_to_next == float('inf'):
                    continue

                # Đánh dấu đã đi
                visited[next_city] = True
                current_path.append(next_city)

                new_cost = current_cost + cost_to_next

                # Làm chậm tốc độ để GUI thấy rõ
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # Gọi đệ quy
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

                # ======== BACKTRACK ========
                # Quay lui: Bỏ chọn thành phố này để thử nhánh khác
                current_path.pop()
                visited[next_city] = False
