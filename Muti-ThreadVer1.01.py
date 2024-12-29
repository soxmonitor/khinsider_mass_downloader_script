import os
import re
import time
import tkinter as tk
from tkinter import simpledialog, Checkbutton, IntVar, Label, Entry, Button, BooleanVar, messagebox, filedialog, OptionMenu
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor

# 一些常量，用户你可以自行修改
DEFAULT_URL = 'https://downloads.khinsider.com/game-soundtracks/album/battlefield-2042-ps4-ps5-windows-xbox-one-xbox-series-xs-gamerip-2021'
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
LAST_URL_FILENAME = 'last_url.txt'
THREAD_OPTIONS = [1, 2, 4, 8, 16, 32]
DEFAULT_THREADS = 32

# 下载并保存文件，加入重试机制
def download_and_save(download_link, download_dir):
    try:
        # 获取解码后的文件名
        file_name = unquote(download_link.split('/')[-1])

        # 清理文件名，去除不合法字符
        safe_file_name = re.sub(r'[<>:"/\\|?*]', '', file_name)
        safe_file_name = re.sub(r'[^\w\s.-]', '', safe_file_name)

        # 确保文件名的扩展名正确
        extension = download_link.split('.')[-1]
        if not safe_file_name.endswith(f'.{extension}'):
            safe_file_name = f'{safe_file_name[:95]}.{extension}'

        # 完整的文件路径
        file_path = os.path.join(download_dir, safe_file_name)

        # 检查文件是否已存在
        if os.path.exists(file_path):
            print(f"File {safe_file_name} already exists. Skipping download.")
            return

        # 下载文件
        download_response = requests.get(download_link, stream=True)
        download_response.raise_for_status()

        # 保存文件
        with open(file_path, 'wb') as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f'Downloaded {safe_file_name}')

    except Exception as e:
        print(f"Failed to download {download_link}. Error: {e}")

# 下载音轨
def download_tracks(album_url, download_flac, download_wav, download_mp3, download_dir, max_threads=32):
    track_links = get_track_links(album_url)
    total_tracks = len(track_links)
    print(f"Total tracks to download: {total_tracks}")

    # 计算每个线程应该下载的任务范围
    chunk_size = total_tracks // max_threads
    remainder = total_tracks % max_threads

    # 使用ThreadPoolExecutor来进行多线程下载
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []

        # 将任务分配到不同的线程
        for i in range(max_threads):
            # 计算每个线程的起始位置和结束位置
            start_index = i * chunk_size
            end_index = start_index + chunk_size
            if i == max_threads - 1:  # 最后一个线程负责处理剩余任务
                end_index += remainder

            futures.append(executor.submit(download_tracks_for_thread, track_links[start_index:end_index], download_flac, download_wav, download_mp3, download_dir))

        # 等待所有线程完成
        for future in futures:
            future.result()

    # 检查是否有遗漏
    print("Download complete. Verifying missing files...")
    for link in track_links:    # 最后检查是否有无遗漏
        file_name = unquote(link.split('/')[-1])
        safe_file_name = re.sub(r'[<>:"/\\|?*]', '', file_name)
        safe_file_name = re.sub(r'[^\w\s.-]', '', safe_file_name)
        file_path = os.path.join(download_dir, safe_file_name)

        # 根据用户的选择，确定需要检查下载的文件格式
        if download_flac and file_name.endswith('.flac'):
            if not os.path.exists(file_path):
                print(f"Missing FLAC file: {safe_file_name}. Retrying download...")
                download_and_save(link, download_dir)

        elif download_wav and file_name.endswith('.wav'):
            if not os.path.exists(file_path):
                print(f"Missing WAV file: {safe_file_name}. Retrying download...")
                download_and_save(link, download_dir)

        elif download_mp3 and file_name.endswith('.mp3'):
            if not os.path.exists(file_path):
                print(f"Missing MP3 file: {safe_file_name}. Retrying download...")
                download_and_save(link, download_dir)
    print("Verified, Successfully fully downloaded!")

# 下载每个线程负责的任务
def download_tracks_for_thread(track_links, download_flac, download_wav, download_mp3, download_dir):
    for link in track_links:
        try:
            track_page = requests.get(link)
            track_page.raise_for_status()
            track_soup = BeautifulSoup(track_page.text, 'html.parser')
            flac_link = mp3_link = wav_link = None

            for a in track_soup.find_all('a'):
                if 'Click here to download as FLAC' in a.text:
                    flac_link = a['href']
                if 'Click here to download as WAV' in a.text:
                    wav_link = a['href']
                if 'Click here to download as MP3' in a.text:
                    mp3_link = a['href']

            # 根据选择下载格式
            if download_flac and flac_link:
                download_and_save(flac_link, download_dir)
            elif download_wav and wav_link:
                download_and_save(wav_link, download_dir)
            elif download_mp3 and mp3_link:
                download_and_save(mp3_link, download_dir)
            else:
                print(f'No download link found for {link}')
        except Exception as e:
            print(f"Error processing {link}: {e}")

# 获取音轨链接
def get_track_links(album_url):
    response = requests.get(album_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    track_links = set()
    base_url = 'https://downloads.khinsider.com'

    # 过滤有效的下载链接
    for link in soup.find_all('a'):
        if 'href' in link.attrs:
            href = link['href']
            full_link = href if href.startswith('http') else base_url + href

            # 确保链接是合法且是音频格式
            if full_link.endswith(('.mp3', '.flac', '.wav')):
                track_links.add(full_link)

    print(f"Total unique track links found: {len(track_links)}")
    return list(track_links)

# 读取最后的URL，如果不存在则返回默认URL
def read_last_url(download_dir):
    last_url_path = os.path.join(download_dir, LAST_URL_FILENAME)
    if os.path.exists(last_url_path):
        with open(last_url_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        return DEFAULT_URL

# 保存最后的URL
def save_last_url(url, download_dir):
    last_url_path = os.path.join(download_dir, LAST_URL_FILENAME)
    with open(last_url_path, 'w', encoding='utf-8') as f:
        f.write(url)

# 界面交互，允许用户输入自定义URL或使用记住的URL，并选择下载目录和线程数
def ask_user_for_album_link(root):
    root.withdraw()

    # 创建新的顶级窗口
    dialog = tk.Toplevel(root)
    dialog.title("Album URL and Download Directory Input")

    # 标签
    url_label = Label(dialog, text="Please enter the album URL:")
    url_label.pack(pady=(10, 0))

    # 获取上次的URL或使用默认
    last_url = read_last_url(DEFAULT_DOWNLOAD_DIR)
    url_var = tk.StringVar(value=last_url)

    # 输入框
    url_entry = Entry(dialog, textvariable=url_var, width=80)
    url_entry.pack(padx=10, pady=5)

    # 记住URL的复选框
    remember_var = BooleanVar()
    # 如果存在上次的URL且不是默认，则默认选中
    remember_var.set(os.path.exists(os.path.join(DEFAULT_DOWNLOAD_DIR, LAST_URL_FILENAME)))

    # 记住URL的复选框
    remember_check = Checkbutton(dialog, text="Remember this URL", variable=remember_var)
    remember_check.pack(pady=(5, 10))  # 增加适当的间距

    # 下载目录选择
    download_dir_label = Label(dialog, text="Select download directory:")
    download_dir_label.pack(pady=(10, 0))

    download_dir_var = tk.StringVar(value=DEFAULT_DOWNLOAD_DIR)

    download_dir_entry = Entry(dialog, textvariable=download_dir_var, width=80)
    download_dir_entry.pack(padx=10, pady=5)

    browse_button = Button(dialog, text="Browse...", command=lambda: browse_directory(download_dir_var))
    browse_button.pack(pady=(0, 10))

    # 线程数选择
    threads_label = Label(dialog, text="Select number of download threads:")
    threads_label.pack(pady=(10, 0))

    thread_var = tk.IntVar(value=DEFAULT_THREADS)
    thread_option = OptionMenu(dialog, thread_var, *THREAD_OPTIONS)
    thread_option.pack(padx=10, pady=5)

    # 下载按钮
    proceed_button = Button(dialog, text="Download", command=lambda: proceed(url_var.get(), download_dir_var.get(), thread_var.get(), remember_var.get(), dialog, root))
    proceed_button.pack(pady=(0, 10))

    # 使窗口居中
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")

    dialog.protocol("WM_DELETE_WINDOW", root.quit)  # 处理窗口关闭
    dialog.mainloop()

# 浏览目录选择
def browse_directory(directory_var):
    selected_dir = filedialog.askdirectory(initialdir=DEFAULT_DOWNLOAD_DIR, title="Select Download Directory")
    if selected_dir:
        directory_var.set(selected_dir)

# 开始下载并保存URL
def proceed(url, download_dir, thread_count, remember, window, root):
    if not url:
        messagebox.showerror("Input Error", "The album URL cannot be empty.")
        return

    if not os.path.isdir(download_dir):
        try:
            os.makedirs(download_dir, exist_ok=True)
            print(f"Created download directory at {download_dir}.")
        except Exception as e:
            messagebox.showerror("Directory Error", f"Failed to create directory {download_dir}. Error: {e}")
            return

    if remember:
        try:
            save_last_url(url, download_dir)
            print(f"Saved last URL to {download_dir}.")
        except Exception as e:
            print(f"Failed to save the URL. Error: {e}")

    window.destroy()
    # 链接到问用户下载什么格式音频框
    ask_user_for_download_options(url, download_dir, thread_count, root)

# 界面交互，允许用户选择下载格式
def ask_user_for_download_options(album_url, download_dir, thread_count, root):
    # 创建新的顶级窗口
    checkbox_window = tk.Toplevel(root)
    checkbox_window.title("Select Download Formats")

    # 选择下载格式的变量
    flac_var = IntVar()
    wav_var = IntVar()
    mp3_var = IntVar()

    # 复选框
    flac_check = Checkbutton(checkbox_window, text="Download FLAC", variable=flac_var)
    wav_check = Checkbutton(checkbox_window, text="Download WAV", variable=wav_var)
    mp3_check = Checkbutton(checkbox_window, text="Download MP3", variable=mp3_var)

    flac_check.pack(anchor='w', padx=20, pady=2)
    wav_check.pack(anchor='w', padx=20, pady=2)
    mp3_check.pack(anchor='w', padx=20, pady=2)

    # 下载按钮
    proceed_button = Button(checkbox_window, text="Start Download", command=lambda: start_download(album_url, download_dir, thread_count, flac_var.get(), wav_var.get(), mp3_var.get(), checkbox_window, root))
    proceed_button.pack(pady=10)

    # 使窗口居中
    checkbox_window.update_idletasks()
    width = checkbox_window.winfo_width()
    height = checkbox_window.winfo_height()
    x = (checkbox_window.winfo_screenwidth() // 2) - (width // 2)
    y = (checkbox_window.winfo_screenheight() // 2) - (height // 2)
    checkbox_window.geometry(f"{width}x{height}+{x}+{y}")

    checkbox_window.protocol("WM_DELETE_WINDOW", root.quit)  # 处理窗口关闭
    checkbox_window.mainloop()

# 启动下载过程
def start_download(album_url, download_dir, thread_count, flac, wav, mp3, window, root):
    if not (flac or wav or mp3):
        messagebox.showwarning("No Format Selected", "Please select at least one download format.")
        return

    window.destroy()
    download_tracks(album_url, flac, wav, mp3, download_dir, max_threads=thread_count)
    root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Album Downloader")
    root.geometry("500x400")
    ask_user_for_album_link(root)
