import tkinter as tk
from tkinter import messagebox, scrolledtext
import time

from ..models.tsp_problem import TSPProblem
from ..algorithms.backtrack_solver import BacktrackSolver
from ..algorithms.bco_solver import BCOSolver 

class TSPApp:
    def __init__(self, master):
        self.master = master
        master.title("TSP Solver (N=3 Mini Demo)")
        
        self.N = 3 
        self.problem = TSPProblem(self.N) 
        self.setup_ui()

    def setup_ui(self):
        # 0. CẤU HÌNH CỘT VÀ HÀNG CỦA CỬA SỔ CHÍNH ĐỂ CHO PHÉP CO GIÃN
        self.master.grid_columnconfigure(0, weight=1)  # Cột bên trái (Ma trận, Menu, Nút)
        self.master.grid_columnconfigure(1, weight=3)  # Cột bên phải (Kết quả) - Chiếm 3/4 không gian
        self.master.grid_rowconfigure(0, weight=1)     # Cho phép hàng chính co giãn

        # 1. Khung chứa Ma trận (Giữ nguyên)
        matrix_frame = tk.LabelFrame(self.master, text=f"Ma trận chi phí (N={self.N})", padx=5, pady=5)
        matrix_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        
        # ... (Phần code tạo ma trận labels giữ nguyên)
        tk.Label(matrix_frame, text="Từ \\ Đến", borderwidth=1, relief="solid").grid(row=0, column=0, padx=2, pady=2)
        for i in range(self.N):
             tk.Label(matrix_frame, text=f"{i}", width=4, borderwidth=1, relief="solid").grid(row=0, column=i+1, padx=2, pady=2)
             tk.Label(matrix_frame, text=f"{i}", width=4, borderwidth=1, relief="solid").grid(row=i+1, column=0, padx=2, pady=2)

        for i in range(self.N):
            for j in range(self.N):
                val = self.problem.cost_matrix[i][j]
                label = tk.Label(matrix_frame, text=f"{val}", width=4, borderwidth=1, relief="solid")
                label.grid(row=i+1, column=j+1, padx=2, pady=2)
            
        # 2. Khung chọn thuật toán 
        option_frame = tk.LabelFrame(self.master, text="Chọn Thuật toán", padx=5, pady=5)
        option_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew") # <-- Sticky EW để co giãn chiều rộng
        
        self.algorithm_options = {
            "1. Backtrack (Chính xác)": BacktrackSolver,
            "2. BCO (Tối ưu Bầy ong)": BCOSolver,
            "3. Backtrack Cải tiến (Branch&Bound)": None 
        }
        self.algo_var = tk.StringVar(self.master)
        self.algo_var.set(list(self.algorithm_options.keys())[0])
        
        algo_menu = tk.OptionMenu(option_frame, self.algo_var, *self.algorithm_options.keys())
        algo_menu.config(width=25)
        algo_menu.pack(pady=5, fill="x", expand=True) # <-- Pack fill X để menu co giãn

        # 3. Nút Run 
        run_button = tk.Button(self.master, text="Chạy Thuật toán", command=self.run_algorithm, bg="#e0ffff")
        run_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # 4. Khu vực kết quả 
        result_frame = tk.LabelFrame(self.master, text="Kết quả", padx=5, pady=5)
        # Sử dụng sticky="NESW" để khung kết quả chiếm hết ô grid (row 0, column 1)
        # và mở rộng theo chiều rộng/cao của cửa sổ.
        result_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=5, sticky="nesw") 
        
        # CẤU HÌNH KHUNG KẾT QUẢ ĐỂ NỘI DUNG CO GIÃN
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1) 
        
        # Textbox hiển thị kết quả
        self.result_text = scrolledtext.ScrolledText(result_frame, width=50, height=15, wrap=tk.WORD)
        # Sử dụng grid với sticky="NESW" để Textbox chiếm hết khung result_frame
        self.result_text.grid(row=0, column=0, sticky="nesw") 
        
        self.display_initial_info()


    def display_initial_info(self):
            """Hiển thị thông tin ban đầu về ma trận mẫu."""
            self.result_text.insert(tk.END, "Chào mừng đến với TSP Mini Solver (N=3)\n")
            self.result_text.insert(tk.END, "--- Cấu hình ma trận ---\n")
            self.result_text.insert(tk.END, "Thành phố 0 <-> 1: 5\n")
            self.result_text.insert(tk.END, "Thành phố 0 <-> 2: 8\n")
            self.result_text.insert(tk.END, "Thành phố 1 <-> 2: 4\n")
            self.result_text.insert(tk.END, "Dự kiến kết quả tối ưu: 17\n")
            self.result_text.insert(tk.END, "-------------------------\n\n")

    def run_algorithm(self):
            """Thực thi thuật toán đã chọn và hiển thị kết quả."""
            selected_algo_name = self.algo_var.get()
            SolverClass = self.algorithm_options.get(selected_algo_name)
            
            if SolverClass is None:
                messagebox.showerror("Lỗi", "Vui lòng chọn thuật toán hợp lệ.")
                return

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"--- BẮT ĐẦU: {selected_algo_name} ---\n")
            
            try:
                solver = SolverClass(self.problem) 
                start_time = time.time() # Thêm đo thời gian
                best_path, best_cost = solver.solve()
                end_time = time.time()
                runtime = end_time - start_time
                
                path_str = self.problem.get_path_string(best_path)
                
                # Hiển thị kết quả cuối cùng
                self.result_text.insert(tk.END, "--- KẾT QUẢ CUỐI CÙNG ---\n")
                self.result_text.insert(tk.END, f"Hành trình tốt nhất: {path_str}\n")
                self.result_text.insert(tk.END, f"Chi phí nhỏ nhất: {best_cost}\n")
                self.result_text.insert(tk.END, f"Thời gian chạy: {runtime:.6f} giây\n")
                
                # --- KIỂM TRA VÀ HIỂN THỊ THÔNG SỐ METAHEURISTICS ---
                if isinstance(solver, BCOSolver):
                    self.result_text.insert(tk.END, f" (BCO: {solver.colony_size} vị trí, {solver.max_iterations} lần lặp, Max Trials: {solver.max_trials})\n")
                    
            except Exception as e:
                messagebox.showerror("Lỗi khi chạy thuật toán", str(e))
                self.result_text.insert(tk.END, f"\nLỖI CHƯƠNG TRÌNH: {e}\n")