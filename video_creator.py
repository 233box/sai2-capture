import os
from tkinter import filedialog
import threading
import imageio.v2 as imageio
from share_state import state

def select_folder_and_create_video(label_status, root, entry_video_duration):
    """
    打启文件对话框让用户选择包含图片的文件夹，并调用create_video_from_images生成视频。
    """
    initial_dir = os.path.dirname(state["output_folder"]) if state["output_folder"] else os.getcwd()
    folder_selected = filedialog.askdirectory(initialdir=initial_dir)
    if folder_selected:
        # 通过GUI更新状态显示
        print(f"Selected folder: {folder_selected}")
        create_video_from_images(folder_selected,label_status,root,entry_video_duration)

def generate_video_thread(image_paths, video_path, fps, label_status, total_images, root):
    try:
        with imageio.get_writer(video_path, format='FFMPEG', mode='I', fps=fps) as writer:
            for i, image_path in enumerate(image_paths):
                image = imageio.imread(image_path)
                writer.append_data(image)
                progress = (i + 1) / total_images * 100
                # 使用 after 安全更新 GUI
                root.after(0, label_status.config, {'text': f"生成视频: {progress:.2f}%"})
        
        root.after(0, label_status.config, {'text': f"视频已保存到 {video_path}"})
    except Exception as e:
        root.after(0, label_status.config, {'text': f"生成视频失败: {str(e)}"})

def create_video_from_images(folder_path,label_status, root, entry_video_duration):
    images = sorted([f for f in os.listdir(folder_path) if f.endswith('.png')], key=lambda x: int(x.split('_')[1].split('.')[0]))
    image_paths = [os.path.join(folder_path, img) for img in images]
    if not image_paths:
        label_status.config(text="没有找到图片文件")
        return

    try:
        video_duration = float(entry_video_duration.get().strip())
        if video_duration <= 0:
            raise ValueError("视频时长必须大于0")
    except ValueError as e:
        label_status.config(text=str(e))
        return

    total_images = len(image_paths)
    fps = total_images / video_duration
    video_path = os.path.join(folder_path, "output.mp4")

    # 启动后台线程执行耗时任务
    thread = threading.Thread(
        target=generate_video_thread,
        args=(image_paths, video_path, fps, label_status, total_images, root)
    )
    thread.start()