# src/gui/benchmark_window.py
import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os
from src.algorithms.backtrack_solver import BacktrackSolver
from src.algorithms.backtrack_solver_improved import BacktrackSolverImproved
from src.algorithms.aco_solver import ACOSolver
from src.models.tsp_problem import TSPProblem

# Định nghĩa các kịch bản
SCENARIOS = [
    "2D (Đối xứng)",
    "Cluster (Phân cụm)",
    "1D (Không đối xứng)"
]

class BenchmarkWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Thử nghiệm thuật toán với ba kịch bản")
        self.geometry("1000x700") # Mở rộng kích thước mặc định
        # Dictionary để lưu trữ tham chiếu đến các biểu đồ (Axes) của từng kịch bản
        # Cấu trúc: { "Tên kịch bản": (ax_time, ax_cost, canvas, figure) }
        self.chart_refs = {} 
        self._setup_ui()

    def _setup_ui(self):
        # --- 1. PHẦN ĐIỀU KHIỂN (TOP) ---
        control_frame = ttk.LabelFrame(self, text="Cấu hình thử nghiệm")
        control_frame.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        ttk.Label(control_frame, text="N tối đa:").pack(side=tk.LEFT, padx=(10, 5))
        self.n_max_spinbox = ttk.Spinbox(control_frame, from_=3, to=30, width=5)
        self.n_max_spinbox.set(10) # Mặc định 10 cho an toàn
        self.n_max_spinbox.pack(side=tk.LEFT, padx=5)

        self.start_btn = ttk.Button(control_frame, text="Bắt đầu Chạy", command=self.start_benchmark)
        self.start_btn.pack(side=tk.LEFT, padx=15)

        self.progress_bar = ttk.Progressbar(control_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side=tk.LEFT, fill="x", expand=True, padx=10, pady=5)
        
        self.status_lbl = ttk.Label(control_frame, text="Sẵn sàng")
        self.status_lbl.pack(side=tk.LEFT, padx=10)

        # --- 2. PHẦN CUỘN (SCROLLABLE AREA) CHO CÁC BIỂU ĐỒ ---
        # Tạo Canvas và Scrollbar
        self.main_canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- 3. TẠO 3 DÒNG BIỂU ĐỒ (LOOP QUA SCENARIOS) ---
        for scenario_name in SCENARIOS:
            self._create_scenario_row(scenario_name)

    def _create_scenario_row(self, scenario_name):
        """Tạo giao diện cho một dòng kịch bản (Label + 2 Biểu đồ)"""
        row_frame = ttk.LabelFrame(self.scrollable_frame, text=scenario_name, padding=10)
        row_frame.pack(fill="x", expand=True, padx=10, pady=10)

        # Tạo Figure của Matplotlib: 1 dòng, 2 cột
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.5), dpi=100)
        
        # Cấu hình style cơ bản
        fig.patch.set_facecolor('#f0f0f0') # Màu nền nhẹ
        
        # Tiêu đề tạm
        ax1.set_title("Đang chờ dữ liệu...", fontsize=9)
        ax2.set_title("Đang chờ dữ liệu...", fontsize=9)
        ax1.grid(True, linestyle='--', alpha=0.6)
        ax2.grid(True, linestyle='--', alpha=0.6)

        # Nhúng vào Tkinter
        canvas = FigureCanvasTkAgg(fig, master=row_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Lưu tham chiếu để sau này update
        self.chart_refs[scenario_name] = {
            "ax_time": ax1,
            "ax_cost": ax2,
            "canvas": canvas,
            "figure": fig
        }

    # --- LOGIC CHẠY BENCHMARK ---

    def start_benchmark(self):
        """Bắt đầu luồng chạy"""
        try:
            n_max = int(self.n_max_spinbox.get())
        except ValueError:
            return

        self.start_btn.config(state="disabled")
        self.status_lbl.config(text="Đang khởi tạo...")
        self.progress_bar["value"] = 0
        
        # Tính tổng số bước để hiển thị progress bar (3 kịch bản * (n_max - 3 + 1) bước)
        # Bắt đầu từ 3 để tránh lỗi logic TSP
        n_start = 3
        total_steps = 3 * (n_max - n_start + 1)
        self.progress_bar["maximum"] = total_steps

        threading.Thread(target=self.run_benchmark_task, args=(n_start, n_max), daemon=True).start()

    def run_benchmark_task(self, n_min, n_max):
        """Hàm worker: Chạy vòng lặp đo lường có giới hạn N cho thuật toán chậm"""
        
        all_results = {}
        step_count = 0

        for scenario in SCENARIOS:
            scenario_data = {
                "n": [],
                "time_bt": [], "time_bti": [], "time_aco": [],
                "cost_bt": [], "cost_bti": [], "cost_aco": [] 
            }
            
            self.master.after(0, lambda s=scenario: self.status_lbl.config(text=f"Đang chạy kịch bản: {s}..."))

            for n in range(n_min, n_max + 1):
                # 1. Tạo dữ liệu
                matrix = self._generate_matrix_for_scenario(scenario, n)
                problem = TSPProblem()
                problem.set_matrix(matrix)
                scenario_data["n"].append(n)

                # --- HÀM PHỤ ĐỂ CHẠY VÀ ĐO THỜI GIAN ---
                def run_and_measure(SolverClass):
                    solver = SolverClass(problem)
                    start_time = time.perf_counter()
                    try:
                        solver.solve(lambda x: None, lambda p, c, t: None, 0) 
                    except TypeError:
                        solver.solve()
                    
                    end_time = time.perf_counter()
                    duration = end_time - start_time
                    
                    cost = getattr(solver, 'min_cost', 0)
                    if cost == float('inf') or cost is None: cost = 0
                    
                    return cost, duration

                # 2. Chạy Backtrack Cơ bản (Giới hạn N <= 12)
                if n > 12:
                    # Quá tải -> Gán 0 để ngắt biểu đồ
                    scenario_data["cost_bt"].append(0)
                    scenario_data["time_bt"].append(0)
                else:
                    c_bt, t_bt = run_and_measure(BacktrackSolver)
                    scenario_data["cost_bt"].append(c_bt)
                    scenario_data["time_bt"].append(t_bt)

                # 3. Chạy Backtrack Cải tiến (Giới hạn N < 16)
                if n > 12:
                    # Quá tải -> Gán 0 để ngắt biểu đồ
                    scenario_data["cost_bti"].append(0)
                    scenario_data["time_bti"].append(0)
                else:
                    c_bti, t_bti = run_and_measure(BacktrackSolverImproved)
                    scenario_data["cost_bti"].append(c_bti)
                    scenario_data["time_bti"].append(t_bti)

                # 4. Chạy ACO (Luôn chạy)
                c_aco, t_aco = run_and_measure(ACOSolver)
                scenario_data["cost_aco"].append(c_aco)
                scenario_data["time_aco"].append(t_aco)

                # Update Progress Bar
                step_count += 1
                self.master.after(0, lambda v=step_count: self.progress_bar.configure(value=v))
            
            all_results[scenario] = scenario_data

        self.master.after(0, self.finish_benchmark, all_results)

    def finish_benchmark(self, all_results):
        """Cập nhật UI sau khi xong"""
        self.status_lbl.config(text="Hoàn tất! Đang vẽ biểu đồ...")
        self.start_btn.config(state="normal")
        self.update_all_plots(all_results)
        self.status_lbl.config(text="Đã xong.")

    def update_all_plots(self, all_results):
        """Vẽ dữ liệu lên từng biểu đồ tương ứng (Có đánh dấu sai số ACO)"""
        
        for scenario, data in all_results.items():
            refs = self.chart_refs.get(scenario)
            if not refs: continue

            ax_time = refs["ax_time"]
            ax_cost = refs["ax_cost"]
            canvas = refs["canvas"]
            
            n_vals = data["n"]

            # --- BIỂU ĐỒ 1: THỜI GIAN (GIỮ NGUYÊN) ---
            ax_time.clear()
            ax_time.plot(n_vals, data["time_bt"], label="Backtrack", marker='o', markersize=4, color='#1f77b4')
            ax_time.plot(n_vals, data["time_bti"], label="BT Cải tiến", marker='s', markersize=4, color='#ff7f0e')
            ax_time.plot(n_vals, data["time_aco"], label="ACO", marker='^', markersize=4, color='#2ca02c')
            
            ax_time.set_title("Thời gian chạy (Log Scale)", fontsize=10, fontweight='bold')
            ax_time.set_yscale('log') 
            ax_time.set_ylabel("Giây")
            ax_time.legend(fontsize=8)
            ax_time.grid(True, linestyle='--', alpha=0.5)

            # --- BIỂU ĐỒ 2: CHI PHÍ (CÓ ĐÁNH DẤU SAI SỐ) ---
            ax_cost.clear()
            
            # 1. Vẽ đường chuẩn (Backtrack) - Làm nền
            ax_cost.plot(n_vals, data["cost_bt"], label="Tối ưu (Backtrack)", 
                         color='#1f77b4', linewidth=2, alpha=0.6)
            
            # 2. Vẽ đường ACO
            ax_cost.plot(n_vals, data["cost_aco"], label="ACO", 
                         color='#2ca02c', marker='^', markersize=4)

            # --- LOGIC ĐÁNH DẤU SỰ KHÁC BIỆT ---
            diff_x = []
            diff_y = []
            
            for i, n in enumerate(n_vals):
                cost_opt = data["cost_bt"][i] # Chi phí tối ưu
                cost_aco = data["cost_aco"][i] # Chi phí ACO
                
                # Chỉ so sánh khi Backtrack chạy thành công (> 0)
                # Và ACO cũng có kết quả (> 0)
                if cost_opt > 0 and cost_aco > 0:
                    # Nếu chênh lệch lớn hơn 0.5 
                    if abs(cost_aco - cost_opt) > 0.5:
                        diff_x.append(n)
                        diff_y.append(cost_aco) # Đánh dấu tại vị trí của ACO
                        print(f"[N={n}] ACO chưa tối ưu! ACO: {cost_aco}, Backtrack: {cost_opt}")

            # Vẽ dấu X màu đỏ tại những chỗ ACO tìm ra kết quả kém hơn
            if diff_x:
                ax_cost.scatter(diff_x, diff_y, color='red', marker='x', s=60, 
                                zorder=10, label="ACO Lệch (Chưa tối ưu)")
            


            ax_cost.set_title("Chất lượng lời giải (Chi phí)", fontsize=10, fontweight='bold')
            ax_cost.set_ylabel("Chi phí")
            ax_cost.legend(fontsize=8)
            ax_cost.grid(True, linestyle='--', alpha=0.5)

            canvas.draw()

    # --- HELPER FUNCTIONS TẠO DỮ LIỆU (COPY TỪ APP.PY LOGIC) ---
    def _generate_matrix_for_scenario(self, scenario, n):
        if "2D" in scenario:
            return self._create_symmetric(n)
        elif "Cluster" in scenario:
            return self._create_cluster(n)
        elif "1D" in scenario:
            return self._create_asymmetric(n)
        return self._create_symmetric(n)

    def _create_symmetric(self, n):
        matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                cost = random.randint(10, 200)
                matrix[i][j] = matrix[j][i] = cost
        return matrix

    def _create_cluster(self, n):
        if n < 4: return self._create_symmetric(n)
        matrix = [[0] * n for _ in range(n)]
        mid = n // 2
        for i in range(n):
            for j in range(i + 1, n):
                same_cluster = (i < mid) == (j < mid)
                cost = random.randint(5, 20) if same_cluster else random.randint(50, 100)
                matrix[i][j] = matrix[j][i] = cost
        return matrix

    def _create_asymmetric(self, n):
        matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j: continue
                # 20% đường đi vô cực
                matrix[i][j] = float('inf') if random.random() < 0.2 else random.randint(10, 100)
        return matrix

