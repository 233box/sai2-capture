# window_utils.py
import ctypes
from PIL import Image, ImageChops
import win32gui
import os
from share_state import state

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', ctypes.c_ulong),
        ('biWidth', ctypes.c_long),
        ('biHeight', ctypes.c_long),
        ('biPlanes', ctypes.c_ushort),
        ('biBitCount', ctypes.c_ushort),
        ('biCompression', ctypes.c_ulong),
        ('biSizeImage', ctypes.c_ulong),
        ('biXPelsPerMeter', ctypes.c_long),
        ('biYPelsPerMeter', ctypes.c_long),
        ('biClrUsed', ctypes.c_ulong),
        ('biClrImportant', ctypes.c_ulong)
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', ctypes.c_ulong * 3)
    ]

def enum_window_titles():
    """
    枚举所有可见窗口的标题，并返回去重后的列表。
    """
    titles = set()

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                titles.add(title)

    win32gui.EnumWindows(callback, None)
    return sorted(titles)

def get_window_rect(hwnd):
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)

def find_window_by_name(window_name):
    hwnd = user32.FindWindowW(None, window_name)
    if hwnd:
        return hwnd
    else:
        raise Exception(f"无法找到名为 {window_name} 的窗口")

def capture_window_content(hwnd):
    x, y, width, height = get_window_rect(hwnd)
    
    # 扩大窗口大小
    width = int(width * 1.5)
    height = int(height * 1.5)
    height -= state["cut_window"]
    
    hdcScreen = user32.GetDC(0)
    hdcMem = gdi32.CreateCompatibleDC(hdcScreen)
    hbmScreen = gdi32.CreateCompatibleBitmap(hdcScreen, width, height)
    gdi32.SelectObject(hdcMem, hbmScreen)
    user32.PrintWindow(hwnd, hdcMem, 0)
    
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = 0
    
    buffer_size = abs(width * height) * 4
    buffer = (ctypes.c_ubyte * buffer_size)()
    
    gdi32.GetDIBits(hdcScreen, hbmScreen, 0, height, buffer, ctypes.byref(bmi), DIB_RGB_COLORS)
    
    image = Image.frombuffer('RGBA', (abs(width), abs(height)), buffer, 'raw', 'BGRA', 0, 1).convert('RGB')
    
    # 清理资源
    gdi32.DeleteObject(hbmScreen)
    gdi32.DeleteDC(hdcMem)
    user32.ReleaseDC(0, hdcScreen)
    
    return image

def save_if_modified(image, last_image, output_folder, frame_number, label_status, label_count, saved_count):
    if last_image is None or ImageChops.difference(image, last_image).getbbox() is not None:
        filename = os.path.join(output_folder, f"frame_{frame_number}.png")
        image.save(filename)
        label_status.config(text=f"帧 {frame_number} 已保存")
        saved_count[0] += 1
        label_count.config(text=f"已保存图像: {saved_count[0]}")
    else:
        label_status.config(text=f"帧 {frame_number} 没有变化")
    
    return image

# 在主程序或其他地方调用
def capture_window(hwnd, output_folder, frame_number, last_image, label_status, label_count, saved_count):
    image = capture_window_content(hwnd)
    return save_if_modified(image, last_image, output_folder, frame_number, label_status, label_count, saved_count)