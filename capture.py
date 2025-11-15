# capture.py
import time
import threading
import os
from window_utils import find_window_by_name, capture_window
from share_state import state
import tkinter as tk
from tkinter import filedialog
from func import create_output_folder, get_unique_video_path

def start_capture(entry_window_name, combo_window_name, use_combo_var, entry_interval, label_status, label_count, button_start, button_pause):
    # 从 shared_state 获取状态
    state['hwnd'] = None
    if use_combo_var.get() == 1:  # 如果选择了使用下拉列表
        window_name = combo_window_name.get().strip()
    else:
        window_name = entry_window_name.get().strip()

    if not window_name or (use_combo_var.get() == 1 and window_name == "从列表选择或手动输入"):  # 检查是否有效窗口名
        label_status.config(text="请输入窗口名称")
        return
    
    try:
        interval = float(entry_interval.get().strip())
        if interval <= 0:
            raise ValueError("时间间隔必须大于0")
        state['interval'] = interval
    except ValueError as e:
        label_status.config(text=str(e))
        return
    
    try:
        hwnd = find_window_by_name(window_name)
        state['hwnd'] = hwnd
    except Exception as e:
        label_status.config(text=str(e))
        return

    if not state['first_start']:
        # 第一次启动时初始化
        output_folder = create_output_folder()
        
        # 👇 使用防重名函数
        video_path = get_unique_video_path(output_folder, "output", ".mp4")
        
        state.update({
            'output_folder': output_folder,
            'last_image': None,
            'frame_number': 0,
            'saved_count': [0],  # 用于统计写入视频的帧数
            'first_start': True,
            'video_writer': None,
            'video_path': video_path
        })
    
    state['running'] = True
    button_start.config(state=tk.DISABLED)
    button_pause.config(state=tk.NORMAL)
    label_status.config(text="开始捕获")
    
    thread = threading.Thread(target=capture_loop, args=(label_status, label_count, state['saved_count']))
    thread.start()
    

def pause_capture(label_status, button_start, button_pause):
    state['running'] = False
    button_start.config(state=tk.NORMAL)
    button_pause.config(state=tk.DISABLED)
    label_status.config(text="捕获已暂停")

def stop_capture(button_start, button_pause, label_status):
    state['running'] = False
    button_pause.config(state=tk.DISABLED)
    
    # 释放视频写入器
    video_writer = state.get('video_writer')
    if video_writer is not None:
        video_writer.release()
        state['video_writer'] = None
        saved_path = state['video_path']
        label_status.config(text=f"捕获停止，视频已保存: {saved_path}")
    else:
        label_status.config(text="捕获停止")
    
    # 👇 关键：重置 first_start，确保下次启动时生成新文件！
    state['first_start'] = False
    
    button_start.config(state=tk.NORMAL)
    
def capture_loop(label_status, label_count, saved_count):
    while state['running']:
        try:
            state['last_image'] = capture_window(
                state['hwnd'],
                state['output_folder'],
                state['frame_number'],
                state['last_image'],
                label_status,
                label_count,
                saved_count
            )
            state['frame_number'] += 1
            time.sleep(state['interval'])
        except Exception as e:
            label_status.config(text=f"错误：{e}")
            time.sleep(1)  # 出错后等待1秒重试