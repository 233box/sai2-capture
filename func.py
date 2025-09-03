import time
import os
from share_state import state
import tkinter as tk
from PIL import ImageTk, Image
import win32gui
import window_utils

def update_cut_window(event,combo_zoom):
    selected_value = combo_zoom.get()
    cut_window_ = 0
    if selected_value == "100%":
        cut_window = 55
    elif selected_value == "125%":
        cut_window = 70
    elif selected_value == "150%":
        cut_window = 85
    elif selected_value == "200%":
        cut_window = 110
    state["cut_window"] = cut_window

def toggle_topmost(root,button_toggle_topmost):
    is_topmost = state.get("is_topmost",False)
    is_topmost = not is_topmost
    root.attributes('-topmost', is_topmost)
    if is_topmost:
        button_toggle_topmost.config(text="取消置顶")
    else:
        button_toggle_topmost.config(text="置顶")
    state["is_topmost"] = is_topmost

def create_output_folder():
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    # folder_name = f"output_{timestamp}"
    folder_name = ""
    output_folder = os.path.join("output_frames", folder_name)
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

def start_preview(entry_window_name, combo_window_name, use_combo_var, combo_zoom, master):
    if use_combo_var.get() == 1:  # 如果选择了使用下拉列表
        window_name = combo_window_name.get().strip()
    else:
        window_name = entry_window_name.get().strip()
    if not window_name:
        print("未选择窗口名称")
        return

    # 创建预览窗口
    preview_window = tk.Toplevel(master)
    preview_window.title("预览窗口")
    canvas = tk.Canvas(preview_window)
    canvas.pack()

    def update_preview():
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd == 0:
            print("找不到指定窗口")
            preview_window.after(1000, update_preview)
            return
        
        image = window_utils.capture_window_content(hwnd)  # 假设这个方法返回PIL.Image对象
        if image:
            w, h = image.size

        
            # 检查是否需要调整大小
            if w > 800 or h > 800:
                ratio = min(800/w, 800/h)
                w = int(w * ratio)
                h = int(h * ratio)
                image = image.resize((w, h), Image.Resampling.LANCZOS)
    
            tk_image = ImageTk.PhotoImage(image)
            canvas.image = tk_image  # 防止被垃圾回收
            canvas.config(width=image.width, height=image.height)
            canvas.create_image(0, 0, anchor='nw', image=tk_image)

        preview_window.after(500, update_preview)  # 每0.5秒更新一次

    update_preview()