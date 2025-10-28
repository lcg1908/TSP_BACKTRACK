# src/models/tsp_problem.py
# import math # KHÔNG CẦN NỮA

class TSPProblem:
    """
    Lớp lưu trữ dữ liệu của bài toán TSP.
    Chỉ làm việc với ma trận chi phí (dist_matrix).
    """
    def __init__(self, matrix=None):
        self.num_cities = 0
        self.dist_matrix = []
        
        if matrix:
            self.set_matrix(matrix)

    
    def set_matrix(self, matrix):
        """
        Thiết lập ma trận chi phí cho bài toán.
        matrix: list của list, ví dụ [[0, 5, 3], [2, 0, 7], [8, 4, 0]]
        """
        self.dist_matrix = matrix
        if matrix:
            self.num_cities = len(matrix)
        else:
            self.num_cities = 0

    def get_cost(self, city_from_idx, city_to_idx):
        """
        Helper: Lấy chi phí đi từ thành phố A đến B.
        """
        try:
            return self.dist_matrix[city_from_idx][city_to_idx]
        except IndexError:
            print(f"Lỗi: Cố gắng truy cập ma trận [{city_from_idx}][{city_to_idx}]")
            return float('inf') # Trả về vô cực nếu lỗi
        except TypeError:
            print("Lỗi: Ma trận chưa được thiết lập (None).")
            return float('inf')


    def get_path_cost(self, path):
        """
        Tính tổng chi phí của một đường đi (chu trình).
        path: list các chỉ số (ví dụ: [0, 2, 1, 3, 0])
        """
        if not path or len(path) < 2 or not self.dist_matrix:
            return 0
            
        cost = 0
        try:
            for i in range(len(path) - 1):
                # Sử dụng hàm get_cost() mới để an toàn
                cost += self.get_cost(path[i], path[i+1])
        except Exception as e:
            print(f"Lỗi khi tính chi phí đường đi: {e}")
            return float('inf')
        return cost