# src/gui/app.py
import tkinter as tk
from sklearn.manifold import MDS
import numpy as np
from tkinter import ttk, messagebox
import threading
import random
import math
from src.models.tsp_problem import TSPProblem
from src.algorithms.backtrack_solver import BacktrackSolver
from src.algorithms.backtrack_solver_improved import BacktrackSolverImproved
from src.algorithms.aco_solver import ACOSolver
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# IMPORT CỬA SỔ CON
from .benchmark_window import BenchmarkWindow

# --- DỮ LIỆU MẪU ---
DEFAULT_MATRIX_2D = [
    [0, 10, 20, 30, 25], [10, 0, 15, 35, 20], [20, 15, 0, 22, 18],
    [30, 35, 22, 0, 12], [25, 20, 18, 12, 0]
]
DEFAULT_MATRIX_CLUSTER = [
    [0, 5, 50, 60, 70], [5, 0, 55, 65, 75], [50, 55, 0, 8, 10],
    [60, 65, 8, 0, 7], [70, 75, 10, 7, 0]
]
DEFAULT_MATRIX_1D = [
    [0, 10, 8, 9, 7], [15, 0, 10, 5, 6], [12, 13, 0, 8, 9],
    [11, 7, 18, 0, 6], [14, 6, 11, 4, 0]
]


SOLVER_CLASSES = {
    "Backtracking (Cơ bản)": BacktrackSolver, 
    "Backtracking (Cải tiến)": BacktrackSolverImproved,
    "ACO (Metaheuristic)": ACOSolver
}

ALL_SOLVER_NAMES = [
    "Backtracking (Cơ bản)", "Backtracking (Cải tiến)", "ACO (Metaheuristic)"
]


class TSPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mô phỏng TSP")
        try:
            self.root.state('zoomed')
        except Exception:
            pass

        # Khởi tạo biến trước khi tạo UI
        self.num_cities_var = tk.IntVar(value=5)
        self.vis_nodes = []
        self.tsp_problem = TSPProblem()
        self.solver = None
        self.solver_thread = None
        self.is_inputting = False

        self.city_treeview = None
        self.comparison_results = {}

        self._setup_ui()

        self.num_cities_var.trace_add("write", self._on_num_cities_change)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        #Buộc Tkinter cập nhật và vẽ cửa sổ để lấy kích thước thật
        self.root.update()

        #Bây giờ canvas đã có kích thước thật, ta mới gọi _reset()
        self._reset()
        self.benchmark_win = None # Biến để kiểm tra cửa sổ con đã mở chưa


    def open_benchmark_window(self):
            """Mở cửa sổ thử nghiệm"""
            # Kiểm tra xem cửa sổ đã mở chưa, nếu rồi thì "focus" nó
            if self.benchmark_win and self.benchmark_win.winfo_exists():
                self.benchmark_win.focus()
            else:
                # Nếu chưa, tạo một cửa sổ Toplevel mới
                # self.root là cửa sổ cha
                self.benchmark_win = BenchmarkWindow(self.root)
                self.benchmark_win.title("Thử nghiệm thuật toán")

    #Được gọi khi người dùng bấm nút [X]. Nó dừng luồng thuật toán (solver_thread.join) trước khi tắt hẳn ứng dụng để tránh lỗi "treo" tiến trình ngầm
    def _on_close(self):
        if self.solver:
            try:
                self.solver.is_running = False
            except Exception:
                pass
        if self.solver_thread and self.solver_thread.is_alive():
            try:
                self.solver_thread.join(timeout=0.2)
            except Exception:
                pass
        self.root.destroy()

    # Tạo ra ma trận khoảng cách dựa trên kịch bản người dùng chọn (Đối xứng, Phân cụm, hoặc 1 chiều).
    def _create_random_symmetric_matrix(self, n):
        matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                cost = random.randint(10, 200)
                matrix[i][j] = matrix[j][i] = cost
        return matrix

    def _create_random_cluster_matrix(self, n):
        if n < 4:
            return self._create_random_symmetric_matrix(n)
        matrix = [[0] * n for _ in range(n)]
        mid_point = n // 2
        for i in range(n):
            for j in range(i + 1, n):
                same = (i < mid_point) == (j < mid_point)
                cost = random.randint(5, 20) if same else random.randint(50, 100)
                matrix[i][j] = matrix[j][i] = cost
        return matrix

    def _create_random_asymmetric_matrix(self, n):
        matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 0
                else:
                    # Xác suất 20% không có đường đi (Inf)
                    if random.random() < 0.2:
                        matrix[i][j] = float('inf')
                    else:
                        matrix[i][j] = random.randint(10, 100)
        return matrix
    #Biến ma trận số liệu thành tọa độ (x, y) để vẽ lên màn hình.
    def _generate_positions_from_distances(self, dist_matrix):
        n = len(dist_matrix)
        if n == 0:
            return []
        # Chuyển thành numpy array
        D = np.array(dist_matrix)
        # Nếu có 0 trên đường chéo thì ok, nếu không thì ép về 0
        np.fill_diagonal(D, 0)
        # Dùng MDS để tìm tọa độ 2D
        mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
        coords = mds.fit_transform(D)
        # Scale và chuyển sang tọa độ canvas
        coords_min, coords_max = coords.min(axis=0), coords.max(axis=0)
        coords_norm = (coords - coords_min) / (coords_max - coords_min + 1e-9)
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 600
        margin = 50
        coords_scaled = [
            {
                'name': str(i),
                'coords': (
                    int(margin + coords_norm[i, 0] * (width - 2 * margin)),
                    int(margin + coords_norm[i, 1] * (height - 2 * margin))
                )
            }
            for i in range(n)
        ]
        return coords_scaled

    #Phương án dự phòng (Fallback): Nếu thuật toán MDS bị lỗi (hoặc dữ liệu quá ít), hàm này sẽ xếp các thành phố thành một vòng tròn đơn giản để đảm bảo chương trình không bị crash.
    def _generate_vis_nodes(self, n):
        self.vis_nodes = []
        if n == 0:
            return
        try:
            self.canvas.update_idletasks()
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            center_x, center_y = width / 2, height / 2
            radius = min(width, height) / 2 - 40
            if radius <= 0:
                radius = 100
            for i in range(n):
                angle = (2 * math.pi / n) * i - (math.pi / 2)
                x_tk = center_x + radius * math.cos(angle)
                y_tk = center_y + radius * math.sin(angle)
                self.vis_nodes.append({'name': str(i), 'coords': (round(x_tk), round(y_tk))})
        except Exception:
            for i in range(n):
                self.vis_nodes.append({'name': str(i), 'coords': (100 + i * 50, 100)})

    # --- UI setup ---
    def _setup_ui(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_label = ttk.Label(header_frame, text="ĐỒ ÁN MÔ PHỎNG THUẬT TOÁN TSP",
                                 font=("Arial", 16, "bold"), anchor=tk.CENTER)
        header_label.pack(fill=tk.X, pady=5)
        ttk.Separator(header_frame).pack(fill=tk.X, pady=5)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        control_frame = ttk.Frame(main_frame, width=350, padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)

        # --- THÊM NÚT BENCHMARK WINDOW ---
        self.benchmark_button = ttk.Button(
            control_frame, 
            text="Chạy Thử Nghiệm (Benchmark)", 
            command=self.open_benchmark_window
        )
        self.benchmark_button.pack(fill="x", padx=10, pady=(0, 5)) # Gói trực tiếp vào sidebar
        # -----------------------------------------------------------

        # Chọn chế độ
        self.mode_frame = ttk.LabelFrame(control_frame, text="Chế độ")
        self.mode_frame.pack(fill=tk.X, pady=2)
        self.mode_var = tk.StringVar(value="default")
        ttk.Radiobutton(self.mode_frame, text="Đồ thị mặc định", variable=self.mode_var,
                        value="default", command=self._on_mode_change).pack(anchor=tk.W)
        ttk.Radiobutton(self.mode_frame, text="Đồ thị ngẫu nhiên", variable=self.mode_var,
                        value="input", command=self._on_mode_change).pack(anchor=tk.W)

        self.input_options_frame = ttk.Frame(self.mode_frame)
        self.input_options_frame.pack(anchor=tk.W, pady=(5, 10), padx=20)
        spinbox_frame = ttk.Frame(self.input_options_frame)
        spinbox_frame.pack(fill=tk.X)
        ttk.Label(spinbox_frame, text="Số thành phố:").pack(side=tk.LEFT, padx=(0, 3))

        #giới hạn 3-100 node
        self.num_cities_spinbox = ttk.Spinbox(spinbox_frame, from_=3, to=100,
                                              textvariable=self.num_cities_var, width=3)
        self.num_cities_spinbox.pack(side=tk.LEFT)
        self.random_btn = ttk.Button(spinbox_frame, text="Tạo ngẫu nhiên",
                                     command=self._generate_random_data)
        self.random_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Điều khiển
        action_frame = ttk.LabelFrame(control_frame, text="Điều khiển")
        action_frame.pack(fill=tk.X, pady=3)

        ttk.Label(action_frame, text="Chọn tình huống (Kịch bản):").pack(anchor=tk.W, padx=5)
        self.scenario_var = tk.StringVar()
        self.scenario_combo = ttk.Combobox(action_frame, textvariable=self.scenario_var,
                                           values=["2D (Đối xứng)", "Cluster (Phân cụm)", "1D (Không đối xứng)"],
                                           state="readonly")
        self.scenario_combo.pack(fill=tk.X, pady=3, padx=3)
        self.scenario_combo.current(0)
        self.scenario_combo.bind("<<ComboboxSelected>>", self._on_scenario_change)

        ttk.Label(action_frame, text="Chọn thuật toán:").pack(anchor=tk.W, padx=3)
        self.solver_var = tk.StringVar()
        self.solver_combo = ttk.Combobox(action_frame, textvariable=self.solver_var,
                                         values=ALL_SOLVER_NAMES, state="readonly")
        self.solver_combo.pack(fill=tk.X, pady=3, padx=3)
        self.solver_combo.current(0)

        self.run_btn = ttk.Button(action_frame, text="Chạy Thuật Toán", command=self._run_solver)
        self.run_btn.pack(fill=tk.X, ipady=2, pady=3, padx=5)
        self.reset_btn = ttk.Button(action_frame, text="Reset", command=self._reset)
        self.reset_btn.pack(fill=tk.X, ipady=2, pady=3, padx=5)


        # Status
        status_frame = ttk.LabelFrame(control_frame, text="Trạng thái")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=2)
        self.status_label = ttk.Label(status_frame, text="Sẵn sàng.", wraplength=330)
        self.status_label.pack(anchor=tk.NW, pady=5, padx=5)
        self.cost_label = ttk.Label(status_frame, text="Chi phí tốt nhất: N/A", font=("Arial", 12, "bold"))
        self.cost_label.pack(anchor=tk.NW, pady=5, padx=5)
        self.best_path_label = ttk.Label(status_frame, text="", font=("Arial", 9), wraplength=330)
        self.best_path_label.pack(anchor=tk.NW, pady=5, padx=5)

        # Treeview ma trận
        list_frame = ttk.LabelFrame(control_frame, text="Ma trận chi phí (Khoảng cách gốc)")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        list_scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        list_scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        self.city_treeview = ttk.Treeview(list_frame, yscrollcommand=list_scrollbar_y.set,
                                          xscrollcommand=list_scrollbar_x.set, height=5)
        list_scrollbar_y.config(command=self.city_treeview.yview)
        list_scrollbar_x.config(command=self.city_treeview.xview)
        list_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        list_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.city_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right display (canvas + charts)
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        center_frame = ttk.Frame(display_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.canvas = tk.Canvas(center_frame, bg="white", highlightthickness=1, highlightbackground="#ccc")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        right_frame = ttk.Frame(display_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)
        chart_top = ttk.Frame(right_frame, height=300)
        chart_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))
        chart_top.pack_propagate(False)
        chart_bottom = ttk.Frame(right_frame, height=300)
        chart_bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        chart_bottom.pack_propagate(False)

        # Runtime Chart
        self.fig_runtime = Figure(figsize=(4, 2), dpi=100)
        self.ax_runtime = self.fig_runtime.add_subplot(111)
        self.runtime_canvas = FigureCanvasTkAgg(self.fig_runtime, master=chart_top)
        self.runtime_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # Cost Chart
        self.fig_cost = Figure(figsize=(4, 2), dpi=100)
        self.ax_cost = self.fig_cost.add_subplot(111)
        self.cost_canvas = FigureCanvasTkAgg(self.fig_cost, master=chart_bottom)
        self.cost_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # --- Event handlers ---
    def _on_mode_change(self, event=None):
        self._reset()

    def _on_scenario_change(self, event=None):
        self._reset()

    def _on_num_cities_change(self, *args):
        if self.mode_var.get() == "input":
            self._reset()
    #Chạy khi bấm nút "Tạo ngẫu nhiên". Gọi các hàm tạo ma trận ở trên, sau đó gọi MDS để tính tọa độ, rồi vẽ lên Canvas.
    def _generate_random_data(self):
        """Tạo ngẫu nhiên ma trận khoảng cách và toạ độ hiển thị."""
        if self.mode_var.get() != "input":
            messagebox.showwarning("Thông báo", "Vui lòng chọn 'Đồ thị ngẫu nhiên' để tạo.")
            return

        n = int(self.num_cities_var.get())
        scenario = (self.scenario_var.get() or "").strip()
        self._reset()
        self.is_inputting = True

        # --- Sinh ma trận khoảng cách ---
        if "2D" in scenario:
            new_matrix = self._create_random_symmetric_matrix(n)
        elif "Cluster" in scenario:
            new_matrix = self._create_random_cluster_matrix(n)
        elif "1D" in scenario or "Không đối xứng" in scenario:
            new_matrix = self._create_random_asymmetric_matrix(n)
        else:
            new_matrix = self._create_random_symmetric_matrix(n)

        # --- Gán ma trận cho TSPProblem ---
        self.tsp_problem.set_matrix(new_matrix)
        self.status_label.config(text=f"Đã tạo ma trận {scenario} {n}x{n}.")

        # --- Sinh vị trí hiển thị (ưu tiên MDS nếu có) ---
        try:
            self.vis_nodes = self._generate_positions_from_distances(new_matrix)
        except Exception as e:
            print(f"[Cảnh báo] Không dùng được MDS, fallback: {e}")
            self._generate_vis_nodes(n)

        # --- Cập nhật UI ---
        self._update_city_treeview()
        self._redraw_canvas()
        self._lock_controls(False)
    #Chạy khi bấm nút "Chạy Thuật Toán". Tạo một Luồng riêng (Thread) để chạy thuật toán (target=self.solver.solve), giúp giao diện không bị đơ.
    def _run_solver(self):
        if self.tsp_problem.num_cities == 0:
            messagebox.showwarning("Lỗi", "Chưa có dữ liệu. Vui lòng tạo ma trận.")
            return
        if self.solver_thread and self.solver_thread.is_alive():
            messagebox.showwarning("Thông báo", "Thuật toán đang chạy...")
            return
        solver_name = self.solver_var.get()
        if not solver_name:
            messagebox.showerror("Lỗi", "Vui lòng chọn một thuật toán.")
            return
        SolverClass = SOLVER_CLASSES.get(solver_name)
        if SolverClass is None:
            messagebox.showinfo("Thông báo", f"Thuật toán '{solver_name}' chưa được cài đặt.")
            return
        self._lock_controls(True)
        self.status_label.config(text=f"Đang chạy {solver_name}...")
        self.cost_label.config(text="Chi phí tốt nhất: Đang tìm...")
        self.best_path_label.config(text="")
        self.solver = SolverClass(self.tsp_problem)
        sleep_time = 0.0
        self.solver_thread = threading.Thread(target=self.solver.solve,
                                              args=(self._update_path_visual, self._on_solver_finish, sleep_time))
        self.solver_thread.daemon = True
        self.solver_thread.start()
    #Đưa ứng dụng về trạng thái ban đầu: Dừng thuật toán, xóa dữ liệu cũ, xóa biểu đồ.
    def _reset(self, *args):
        if self.solver:
            try:
                self.solver.is_running = False
            except Exception:
                pass
        self.vis_nodes = []
        self.is_inputting = False
        self.tsp_problem = TSPProblem()
        self.comparison_results = {}
        mode = self.mode_var.get()
        scenario = self.scenario_var.get()

        if mode == "default":
            self.is_inputting = False
            if scenario == "2D (Đối xứng)":
                matrix_to_load = DEFAULT_MATRIX_2D
            elif scenario == "Cluster (Phân cụm)":
                matrix_to_load = DEFAULT_MATRIX_CLUSTER
            else:
                matrix_to_load = DEFAULT_MATRIX_1D
            self.tsp_problem.set_matrix(matrix_to_load)
            self.num_cities_var.set(self.tsp_problem.num_cities)
            self.status_label.config(text=f"Đã tải ma trận mặc định {scenario}.")
        else:
            self.is_inputting = True
            n = int(self.num_cities_var.get())
            self.status_label.config(text=f"Hãy nhấn 'Tạo ngẫu nhiên' để tạo ma trận {n}x{n}.")

        self.cost_label.config(text="Chi phí tốt nhất: N/A")
        self.best_path_label.config(text="")

        n_cities = self.tsp_problem.num_cities
        current_matrix = self.tsp_problem.dist_matrix
        if n_cities > 0 and current_matrix:
            try:
                # Thử dùng MDS để tạo vị trí từ ma trận khoảng cách
                self.vis_nodes = self._generate_positions_from_distances(current_matrix)
            except Exception as e:
                # Nếu thất bại (ví dụ: ma trận không đối xứng, MDS lỗi),
                # thì quay về cách vẽ vòng tròn
                self._generate_vis_nodes(n_cities)
        else:
            # Nếu không có ma trận (chế độ input chưa nhấn tạo)
            self._generate_vis_nodes(n_cities)


        self._update_city_treeview()
        self._lock_controls(False)
        self._redraw_canvas()
        self._clear_comparison_charts()

    def _update_city_treeview(self):
        if not self.city_treeview:
            return
        for item in self.city_treeview.get_children():
            self.city_treeview.delete(item)
        matrix = self.tsp_problem.dist_matrix
        n = self.tsp_problem.num_cities
        if n == 0 or not matrix:
            self.city_treeview['columns'] = ()
            self.city_treeview.heading("#0", text="Chưa có dữ liệu")
            return

        col_names = [str(i) for i in range(n)]
        self.city_treeview['columns'] = col_names
        self.city_treeview.heading("#0", text="TP")
        self.city_treeview.column("#0", width=40, anchor=tk.W, stretch=False)
        for i in range(n):
            col_name = str(i)
            self.city_treeview.heading(col_name, text=col_name)
            self.city_treeview.column(col_name, width=50, anchor=tk.E, stretch=True)

        for i in range(n):
            row_values = [f"{matrix[i][j]:.0f}" if matrix[i][j] != float('inf') else "Inf" for j in range(n)]
            self.city_treeview.insert("", tk.END, text=f"{i}", values=row_values)


    '''Hàm "quản lý trạng thái" của giao diện. 
    Nhiệm vụ: bật (enable) hoặc tắt (disable) các nút bấm, ô chọn, và thanh trượt, dựa trên việc thuật toán có đang chạy hay không.
    Hàm này nhận một tham số: is_running (là True nếu thuật toán đang chạy, False nếu không).'''
    def _lock_controls(self, is_running):
        run_state = tk.DISABLED if is_running else tk.NORMAL
        #Nút reset bật bất cứ lúc nào
        reset_state = tk.NORMAL
        self.run_btn.config(state=run_state)
        self.reset_btn.config(state=reset_state)
        other_state = tk.DISABLED if is_running else tk.NORMAL
        self.solver_combo.config(state=other_state)

        try:
            if other_state == tk.DISABLED:
                self.city_treeview.state(['disabled'])
            else:
                self.city_treeview.state(['!disabled'])
        except Exception:
            pass
        self.scenario_combo.config(state=other_state)
        for child in self.mode_frame.winfo_children():
            if isinstance(child, ttk.Radiobutton):
                child.config(state=other_state)
        is_input_mode = (self.mode_var.get() == "input")
        input_state = tk.NORMAL if (is_input_mode and not is_running) else tk.DISABLED
        try:
            self.num_cities_spinbox.config(state=input_state)
        except Exception:

            try:
                if input_state == tk.DISABLED:
                    self.num_cities_spinbox.state(['disabled'])
                else:
                    self.num_cities_spinbox.state(['!disabled'])
            except Exception:
                pass
        self.random_btn.config(state=input_state)
        if self.tsp_problem.num_cities > 0 and not is_running:
            self.run_btn.config(state=tk.NORMAL)
        else:
            self.run_btn.config(state=tk.DISABLED)

    # Drawing callbacks
    def _update_path_visual(self, path):
        if self.root:
            self.root.after(0, self._draw_path_on_main, path, "green", 2)

    def _on_solver_finish(self, best_path, min_cost, runtime):
        if self.root:
            solver_name = self.solver_var.get()
            self.root.after(0, self._handle_finish_on_main, solver_name, best_path, min_cost, runtime)


    def _draw_path_on_main(self, path, color, width):
        self._redraw_canvas()
        self._draw_path(path, color, width)

    def _handle_finish_on_main(self, solver_name, best_path, min_cost, runtime):
        if not self.root or not hasattr(self, 'status_label') or not self.status_label.winfo_exists():
            return
        self.status_label.config(text=f"Hoàn thành {solver_name}! (Sau {runtime:.2f} giây)")
        self.cost_label.config(text=f"Chi phí tốt nhất: {min_cost:.2f}")
        self.comparison_results[solver_name] = {"time": runtime, "cost": min_cost}
        self._draw_path_on_main(best_path, "green", 4)
        try:
            path_names = [str(i) for i in best_path]
            path_str = ' -> '.join(path_names)
            self.best_path_label.config(text=f"Lộ trình: {path_str}")
        except Exception as e:
            print(f"Lỗi khi hiển thị lộ trình: {e}")
            self.best_path_label.config(text="Không thể hiển thị lộ trình.")
        self._lock_controls(False)
        runnable_solvers = [name for name, cls in SOLVER_CLASSES.items() if cls is not None]
        if all(name in self.comparison_results for name in runnable_solvers):
            self._update_comparison_charts()
    #Xóa sạch màn hình và vẽ lại các chấm tròn (thành phố) dựa trên tọa độ đã tính.
    def _redraw_canvas(self):
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            return
        for node_data in self.vis_nodes:
            x_tk, y_tk = node_data['coords']
            city_name = node_data['name']
            fill_color = "#007bff"
            self.canvas.create_oval(x_tk - 5, y_tk - 5, x_tk + 5, y_tk + 5,
                                    fill=fill_color, outline="black", width=1)
            self.canvas.create_text(x_tk, y_tk - 10, text=city_name,
                                    anchor=tk.S, font=("Arial", 10, "bold"))

    #Vẽ các đường nối (Line) giữa các thành phố. Vẽ thêm mũi tên (nếu là đồ thị 1 chiều) và hiển thị con số chi phí ở giữa đoạn đường.
    def _draw_path(self, path_indices, color, width):
        if not path_indices or len(path_indices) < 2 or not self.vis_nodes:
            return
        is_asymmetric = (self.scenario_var.get() == "1D (Không đối xứng)")
        try:
            path_coords = [self.vis_nodes[idx]['coords'] for idx in path_indices]
            for i in range(len(path_coords) - 1):
                idx1, idx2 = path_indices[i], path_indices[i + 1]
                x1, y1 = path_coords[i]
                x2, y2 = path_coords[i + 1]
                arrow = tk.LAST if is_asymmetric else tk.NONE
                line_id = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, arrow=arrow)

                cost = self.tsp_problem.get_cost(idx1, idx2)
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                angle_rad = math.atan2(y2 - y1, x2 - x1)
                angle_deg = math.degrees(angle_rad)
                if 90 < angle_deg <= 180:
                    angle_deg -= 180
                elif -180 <= angle_deg < -90:
                    angle_deg += 180

                text_id = self.canvas.create_text(
                    mid_x, mid_y, text=f"{cost:.0f}",
                    fill="red", font=("Arial", 8, "bold")
                )
                bbox = self.canvas.bbox(text_id)
                if bbox:
                    padding = 1
                    rect_id = self.canvas.create_rectangle(
                        bbox[0] - padding, bbox[1] - padding,
                        bbox[2] + padding, bbox[3] + padding,
                        fill="white", outline=""
                    )
                    # Đưa khung xuống dưới chữ
                    self.canvas.tag_lower(rect_id, text_id)

        except IndexError:
            print("Lỗi Index khi vẽ đường đi (vis_nodes).")
        except Exception as e:
            print(f"Lỗi không xác định khi vẽ đường đi: {e}")

    # Hàm vẽ Charts
    def _clear_comparison_charts(self):
        self.comparison_results = {}
        if hasattr(self, 'ax_runtime') and hasattr(self, 'ax_cost'):
            self.ax_runtime.clear()
            self.ax_cost.clear()
            self.ax_runtime.set_title("Thời gian chạy", fontsize=10)
            self.ax_cost.set_title("Chi phí tốt nhất", fontsize=10)
            self.ax_runtime.text(0.5, 0.5, "Chạy các thuật toán\nđể so sánh", ha='center', va='center', transform=self.ax_runtime.transAxes)
            self.ax_cost.text(0.5, 0.5, "Chạy các thuật toán\nđể so sánh", ha='center', va='center', transform=self.ax_cost.transAxes)
            self.ax_runtime.tick_params(axis='both', which='major', labelsize=8)
            self.ax_cost.tick_params(axis='both', which='major', labelsize=8)
            try:
                self.fig_runtime.tight_layout(pad=1.5)
                self.fig_cost.tight_layout(pad=1.5)
            except Exception:
                pass
            if hasattr(self, 'runtime_canvas'):
                self.runtime_canvas.draw_idle()
            if hasattr(self, 'cost_canvas'):
                self.cost_canvas.draw_idle()

    def _update_comparison_charts(self):
        if not hasattr(self, 'ax_runtime') or not hasattr(self, 'ax_cost') or not self.comparison_results:
            self._clear_comparison_charts()
            return
        labels = list(self.comparison_results.keys())
        times = [result['time'] for result in self.comparison_results.values()]
        costs = [result['cost'] for result in self.comparison_results.values()]
        try:
            sorted_data = sorted(zip(labels, times, costs))
            labels = [item[0] for item in sorted_data]
            times = [item[1] for item in sorted_data]
            costs = [item[2] for item in sorted_data]
        except Exception:
            print("Lỗi sắp xếp dữ liệu biểu đồ")
            return

        x_pos = range(len(labels))
        colors = ['#007bff', '#dc3545', '#28a745', '#ffc107', '#6f42c1']
        bar_colors = colors[:len(labels)]

        self.ax_runtime.clear()
        bars_runtime = self.ax_runtime.bar(x_pos, times, color=bar_colors)
        self.ax_runtime.set_ylabel("Thời gian (s)", fontsize=9)
        self.ax_runtime.set_title("So sánh Thời gian chạy", fontsize=10)
        self.ax_runtime.set_xticks(list(x_pos))
        self.ax_runtime.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
        self.ax_runtime.tick_params(axis='y', labelsize=8)
        try:
            self.ax_runtime.bar_label(bars_runtime, fmt='%.2f', fontsize=8, padding=-12, color='white', weight='bold')
        except Exception:
            pass

        self.ax_cost.clear()
        bars_cost = self.ax_cost.bar(x_pos, costs, color=bar_colors)
        self.ax_cost.set_ylabel("Chi phí", fontsize=9)
        self.ax_cost.set_title("So sánh Chi phí tốt nhất", fontsize=10)
        self.ax_cost.set_xticks(list(x_pos))
        self.ax_cost.set_xticklabels(labels, rotation=30, ha='right', fontsize=8)
        self.ax_cost.tick_params(axis='y', labelsize=8)
        try:
            self.ax_cost.bar_label(bars_cost, fmt='%.2f', fontsize=8, padding=-12, color='white', weight='bold')
        except Exception:
            pass

        if costs:
            min_c, max_c = min(costs) * 0.9, max(costs) * 1.1
            self.ax_cost.set_ylim(bottom=min_c if min_c > 0 else 0, top=max_c)
        try:
            self.fig_runtime.tight_layout(pad=2.0)
            self.fig_cost.tight_layout(pad=2.0)
        except Exception:
            pass
        self.runtime_canvas.draw_idle()
        self.cost_canvas.draw_idle()

