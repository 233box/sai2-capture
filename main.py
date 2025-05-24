import tkinter as tk
from tkinter import ttk, filedialog
import capture  # 假设已创建的capture模块
import video_creator  # 假设已创建的video_creator模块
import settings_handler  # 假设已创建的settings_handler模块
import window_utils
import func

def main():
    global root
    root = tk.Tk()
    root.title("Sai2 捕获工具")
    root.geometry("800x350")

    titles = window_utils.enum_window_titles()  # 获取所有窗口名称
    combo_window_name = ttk.Combobox(root, values=titles)
    combo_window_name.set("从列表选择或手动输入")  # 默认提示信息
    combo_window_name.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    use_combo_var = tk.IntVar(value=1)  # 默认选中使用下拉列表
    check_use_combo = ttk.Checkbutton(root, text="使用下拉列表中的窗口", variable=use_combo_var)
    check_use_combo.grid(row=0, column=3, padx=10, pady=5, sticky="w")

    label_window_name = ttk.Label(root, text="窗口名称:")
    label_window_name.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_window_name = ttk.Entry(root, width=20)
    entry_window_name.insert(0, "导航器")  # 默认值
    entry_window_name.grid(row=0, column=2, padx=10, pady=5, sticky="w")

    label_interval = ttk.Label(root, text="捕获时间间隔 (秒):")
    label_interval.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry_interval = ttk.Entry(root, width=20)
    entry_interval.insert(0, "0.1")  # 默认值
    entry_interval.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    label_zoom = ttk.Label(root, text="缩放大小:")
    label_zoom.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    combo_zoom = ttk.Combobox(root, values=["100%", "125%", "150%", "200%"])
    combo_zoom.set("125%")  # 默认值
    combo_zoom.bind("<<ComboboxSelected>>", lambda event: func.update_cut_window(event,combo_zoom))
    combo_zoom.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    label_video_duration = ttk.Label(root, text="视频时长 (秒):")
    label_video_duration.grid(row=3, column=0, padx=10, pady=5, sticky="w")
    entry_video_duration = ttk.Entry(root, width=20)
    entry_video_duration.insert(0, "10")  # 默认值
    entry_video_duration.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    label_status = ttk.Label(root, text="状态: 未开始")
    label_status.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")
    label_count = ttk.Label(root, text="已保存图像: 0")
    label_count.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="w")

    button_width = 15
    button_start = ttk.Button(root, text="开始/继续", command=lambda: capture.start_capture(entry_window_name, combo_window_name, use_combo_var, entry_interval, label_status, label_count, button_start, button_pause), width=button_width)
    button_start.grid(row=6, column=0, padx=10, pady=5, sticky="w")
    button_pause = ttk.Button(root, text="暂停", command=lambda: capture.pause_capture(label_status, button_start, button_pause), state=tk.DISABLED, width=button_width)
    button_pause.grid(row=6, column=1, padx=10, pady=5, sticky="w")
    button_toggle_topmost = ttk.Button(root, text="置顶", command=lambda: func.toggle_topmost(root,button_toggle_topmost), width=button_width)
    button_toggle_topmost.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="w")
    button_create_video = ttk.Button(root, text="生成视频", command=lambda: video_creator.select_folder_and_create_video(label_status, root, entry_video_duration), width=button_width)
    button_create_video.grid(row=7, column=1, columnspan=2, padx=10, pady=5, sticky="w")
    # 新增预览按钮
    button_preview = ttk.Button(root, text="预览窗口", command=lambda: func.start_preview(entry_window_name, combo_window_name, use_combo_var, combo_zoom, root), width=button_width)
    button_preview.grid(row=8, column=0, padx=10, pady=5, sticky="w")

    settings_handler.load_settings(entry_window_name, combo_window_name, use_combo_var, entry_interval, combo_zoom, entry_video_duration)

    root.protocol("WM_DELETE_WINDOW", lambda: (settings_handler.save_settings(entry_window_name, combo_window_name, use_combo_var, entry_interval, combo_zoom, entry_video_duration), root.destroy()))


    root.mainloop()

if __name__ == "__main__":
    main()