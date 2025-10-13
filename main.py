import sys
import tkinter as tk
import os

# Thêm đường dẫn thư mục 'src' vào sys.path để import các module
# Điều này giúp cho việc import hoạt động đúng trong VS Code
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, 'src'))

from src.gui.app import TSPApp

def main():
    """Khởi chạy ứng dụng Tkinter."""
    root = tk.Tk()
    
    # KÍCH HOẠT CHẾ ĐỘ TOÀN MÀN HÌNH
    root.attributes('-fullscreen', True) 

    # BẮT SỰ KIỆN PHÍM ESCAPE ĐỂ THOÁT
    # Khi nhấn phím ESC, thoát khỏi chế độ toàn màn hình (và đóng ứng dụng).
    root.bind('<Escape>', lambda event: root.attributes('-fullscreen', False))
    
    app = TSPApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
