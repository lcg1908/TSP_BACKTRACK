# src/models/tsp_problem.py

class TSPProblem:
    """
    Lớp TSP Problem lưu trữ ma trận khoảng cách (matrix) và tính toán chi phí khi được hỏi.
    """
    def __init__(self, matrix=None):
        # Ban đầu chưa có thành phố nào (số lượng = 0)
        self.num_cities = 0
        # Ma trận khoảng cách ban đầu là rỗng
        self.dist_matrix = []
        # Nếu lúc khởi tạo có đưa ma trận vào thì thiết lập luôn
        if matrix:
            self.set_matrix(matrix)

    
    def set_matrix(self, matrix):
        """
        Hàm này dùng để nạp hoặc thay đổi dữ liệu bản đồ.
        Input: matrix là list lồng nhau (bảng 2 chiều). 
        Ví dụ: matrix[0][1] là khoảng cách từ thành phố 0 đến 1.
        """
        self.dist_matrix = matrix  
        # Nếu ma trận có dữ liệu
        if matrix:
            # Tự động đếm số lượng thành phố dựa trên độ dài ma trận
            self.num_cities = len(matrix)
        else:
            # Nếu ma trận rỗng thì reset về 0
            self.num_cities = 0

    def get_cost(self, city_from_idx, city_to_idx):
        """
        Helper: Trả lời câu hỏi "Đi từ thành phố A đến B tốn bao nhiêu?"
        """
        try:
            # Thử lấy giá trị trong ma trận tại hàng [city_from] cột [city_to]
            return self.dist_matrix[city_from_idx][city_to_idx]
        
        except IndexError:
            # Lỗi này xảy ra nếu bạn hỏi thành phố số 10 mà bản đồ chỉ có 5 thành phố
            print(f"Lỗi: Cố gắng truy cập ma trận [{city_from_idx}][{city_to_idx}] - Không tồn tại")
            return float('inf') # Trả về vô cực (coi như không đi được)
        
        except TypeError:
            # Lỗi này xảy ra nếu chưa nạp ma trận mà đã đòi lấy dữ liệu
            print("Lỗi: Ma trận chưa được thiết lập (None).")
            return float('inf')


    def get_path_cost(self, path):
        """
        Tính tổng chi phí của cả một lộ trình (Total Distance).
        Input path: Danh sách thứ tự đi, ví dụ: [0, 2, 1, 3, 0] (đi từ 0->2->1->3 rồi về 0)
        """
        # Kiểm tra an toàn: Nếu lộ trình rỗng hoặc ngắn quá (<=2 điểm) hoặc chưa có bản đồ
        if not path or len(path) <= 2 or not self.dist_matrix:
            return 0
            
        total_cost = 0 # Biến tổng chi phí ban đầu bằng 0
        
        try:
            # Duyệt qua từng chặng đường trong lộ trình
            # len(path) - 1 vì nếu có 5 điểm thì chỉ có 4 đoạn đường nối
            for i in range(len(path) - 1):
                current_city = path[i]     # Thành phố đang đứng
                next_city = path[i+1]      # Thành phố tiếp theo sẽ đến
                
                # Cộng dồn chi phí của đoạn đường này vào tổng
                # Sử dụng hàm get_cost() ở trên để lấy khoảng cách
                total_cost += self.get_cost(current_city, next_city)
                
        except Exception as e:
            print(f"Lỗi khi tính chi phí đường đi: {e}")
            return float('inf') # Nếu lỗi thì trả về vô cực
            
        return total_cost # Trả về kết quả cuối cùng
