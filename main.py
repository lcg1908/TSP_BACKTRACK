# main.py
import tkinter as tk
from src.gui.app import TSPApp

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = TSPApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
