# main.py
import tkinter as tk  # Thư viện để làm giao diện 
from src.gui.app import TSPApp  # Import lớp TSPApp

# Đảm bảo code chỉ chạy khi mở trực tiếp file này 
# (không chạy nếu file này được import bởi file khác)
if __name__ == "__main__":
    try:
        # 1. Tạo khung cửa sổ gốc (Root Window)
        # Khung vỏ trắng tinh chưa có nội dung 
        root = tk.Tk()
        # 2. Khởi tạo ứng dụng TSPApp
        # Nạp toàn bộ nút bấm, bản đồ, logic vào trong root ở trên
        app = TSPApp(root)
        # 3. Bắt đầu vòng lặp sự kiện (Event Loop)
        # Giữ cho cửa sổ luôn hiển thị và lắng nghe thao tác chuột/bàn phím của người dùng.
        # Nếu không có dòng này, cửa sổ hiện lên rồi tắt ngay lập tức.
        root.mainloop()
    except Exception as e:
        # In ra lỗi nếu chương trình không khởi động được (tránh crash đột ngột)
        print(f"Đã xảy ra lỗi: {e}")
