import os
import launch
import platform
import subprocess

def is_aria2_installed():
    """返回 True 如果 aria2c 命令在 PATH 中可用"""
    try:
        subprocess.run("aria2c", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

system = platform.system()

if system == "Linux":
    if not is_aria2_installed():
        try:
            release_info = platform.freedesktop_os_release()
        except Exception:
            release_info = {}

        dist_id = release_info.get("ID", "")
        id_like = release_info.get("ID_LIKE", "")

        # 检测是否为 Arch 系发行版
        arch_ids = {"arch", "endeavouros", "manjaro", "artix"}
        is_arch = (dist_id in arch_ids) or ("arch" in id_like)

        if is_arch:
            launch.run("sudo pacman -S aria2", "Installing requirements for Model Downloader")
        else:
            # 默认尝试 apt，但提示可能不适用
            print("Attempting to install aria2 via apt (Debian/Ubuntu)...")
            launch.run("apt update && apt -y install -qq aria2", "Installing requirements for Model Downloader")
    # 如果已安装，什么都不做

elif system == "Darwin":          # macOS
    if not is_aria2_installed():
        launch.run("brew install aria2", "Installing requirements for Model Downloader")

elif system == "Windows":
    if not is_aria2_installed():
        print("Model Downloader requires aria2c for the 'aria2' download method.")
        print("See setup tutorial: https://www.youtube.com/watch?v=JnWQST4ay_E")
        print("Alternatively, you can choose the 'requests' downloader in the UI without installing aria2.")