# settings_handler.py
import os
import pickle
from share_state import state
import tkinter as tk
from tkinter import filedialog

SETTINGS_FILE = "settings.pkl"

def save_settings(entry_window_name, combo_window_name, use_combo_var, entry_interval, combo_zoom, entry_video_duration):
    """
    保存当前设置到文件。
    """
    settings = {
        "window_name": entry_window_name.get(),
        "combo_window_name": combo_window_name.get(),
        "use_combo": use_combo_var.get(),
        "interval": entry_interval.get(),
        "zoom": combo_zoom.get(),
        "video_duration": entry_video_duration.get()
    }
    try:
        with open(SETTINGS_FILE, 'wb') as f:
            pickle.dump(settings, f)
        print("设置已保存")
    except Exception as e:
        print(f"保存设置失败: {e}")

def load_settings(entry_window_name, combo_window_name, use_combo_var, entry_interval, combo_zoom, entry_video_duration):
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "rb") as f:
            settings = pickle.load(f)
            window_name = settings.get("window_name", "导航器")
            entry_window_name.delete(0, tk.END)
            entry_window_name.insert(0, window_name)
            combo_window_name.set(window_name)  # 同时设置 combo_window_name
            combo_zoom.set(settings.get("zoom", "125%"))
            entry_video_duration.delete(0, tk.END)
            entry_video_duration.insert(0, str(settings.get("video_duration", 10)))
            use_combo = settings.get("use_combo", 1)  # 获取是否使用下拉列表的设置，默认为1（使用）
            use_combo_var.set(use_combo)
            interval = settings.get("interval", 1.0)
            entry_interval.delete(0, tk.END)
            entry_interval.insert(0, str(interval))
            # 更新 shared_state 中的相关状态（如果需要）
            state.update({
                "cut_window": get_cut_window_from_zoom(combo_zoom.get()),
                "interval": float(interval)
            })

def get_cut_window_from_zoom(zoom_str):
    zoom_map = {
        "100%": 55,
        "125%": 70,
        "150%": 85,
        "200%": 110
    }
    return zoom_map.get(zoom_str, 70)  # 默认返回125%对应的值