import math
import random

class TSPProblem:
    """Định nghĩa cấu trúc dữ liệu cho bài toán TSP."""
    def __init__(self, n=3, matrix=None):
        self.N = n
        # Ma trận cố định cho N=3 (0=A, 1=B, 2=C)
        if matrix is None:
            # Chi phí: A->B=5, A->C=8, B->C=4
            self.cost_matrix = [
                [0, 5, 8],
                [5, 0, 4],
                [8, 4, 0]
            ]
        else:
            self.cost_matrix = matrix
            
        self.city_names = {i: str(i) for i in range(self.N)}

    def calculate_cost(self, path):
        """Tính tổng chi phí của một chu trình (quay về điểm xuất phát)."""
        if len(path) != self.N:
            return float('inf')

        total_cost = 0
        
        # Chi phí đi qua các thành phố (i -> i+1)
        for i in range(self.N - 1):
            city_from = path[i]
            city_to = path[i+1]
            total_cost += self.cost_matrix[city_from][city_to]
            
        # Chi phí quay về thành phố xuất phát (cuối -> đầu)
        city_last = path[-1]
        city_first = path[0]
        total_cost += self.cost_matrix[city_last][city_first]
        
        return total_cost

    def get_path_string(self, path):
        """Chuyển đổi chu trình số sang chuỗi tên (ví dụ: 0->1->2->0)."""
        if not path:
            return "[]"
        # Thêm lại thành phố đầu tiên để tạo thành chu trình
        full_path = path + [path[0]]
        return " -> ".join([self.city_names[i] for i in full_path])