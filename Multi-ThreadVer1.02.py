import os
import re
import tkinter as tk
from tkinter import Label, Entry, Button, Checkbutton, IntVar, BooleanVar, messagebox, filedialog, OptionMenu, Toplevel, Frame, Canvas, Scrollbar
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageTk
import io

# Constants for default URL and the file to store the last URL
DEFAULT_URL = 'https://downloads.khinsider.com/game-soundtracks/album/battlefield-2042-ps4-ps5-windows-xbox-one-xbox-series-xs-gamerip-2021'
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
LAST_URL_FILENAME = 'last_url.txt'
THREAD_OPTIONS = [1, 2, 4, 8, 16, 32]
DEFAULT_THREADS = 32
BASE_URL = 'https://downloads.khinsider.com'

# Global list to keep references to PhotoImage objects
image_references = []

# 下载并保存文件，支持断点续传和重试机制
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/58.0.3029.110 Safari/537.3'
        }
        download_response = requests.get(download_link, stream=True, headers=headers)
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
    if max_threads > total_tracks:
        max_threads = total_tracks if total_tracks > 0 else 1
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

        if download_wav and file_name.endswith('.wav'):
            if not os.path.exists(file_path):
                print(f"Missing WAV file: {safe_file_name}. Retrying download...")
                download_and_save(link, download_dir)

        if download_mp3 and file_name.endswith('.mp3'):
            if not os.path.exists(file_path):
                print(f"Missing MP3 file: {safe_file_name}. Retrying download...")
                download_and_save(link, download_dir)
    print("Verified, Successfully fully downloaded!")

# 下载每个线程负责的任务
def download_tracks_for_thread(track_links, download_flac, download_wav, download_mp3, download_dir):
    for link in track_links:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
                Chrome/58.0.3029.110 Safari/537.3'
            }
            track_page = requests.get(link, headers=headers)
            track_page.raise_for_status()
            track_soup = BeautifulSoup(track_page.text, 'html.parser')
            flac_link = mp3_link = wav_link = None

            for a in track_soup.find_all('a'):
                if 'Click here to download as FLAC' in a.text:
                    flac_link = urljoin(BASE_URL, a['href'])
                if 'Click here to download as WAV' in a.text:
                    wav_link = urljoin(BASE_URL, a['href'])
                if 'Click here to download as MP3' in a.text:
                    mp3_link = urljoin(BASE_URL, a['href'])

            # 根据选择下载格式
            if download_flac and flac_link:
                download_and_save(flac_link, download_dir)
            if download_wav and wav_link:
                download_and_save(wav_link, download_dir)
            if download_mp3 and mp3_link:
                download_and_save(mp3_link, download_dir)
        except Exception as e:
            print(f"Error processing {link}: {e}")

# 获取音轨链接
def get_track_links(album_url):
    response = requests.get(album_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    track_links = set()

    # 假设所有下载链接都在class为albumListDiv的div内
    album_list_div = soup.find('div', class_='albumListDiv')
    if not album_list_div:
        print("No album list div found.")
        return list(track_links)

    album_table = album_list_div.find('table', class_='albumList')
    if not album_table:
        print("No album table found.")
        return list(track_links)

    for tr in album_table.find_all('tr')[1:]:  # 跳过表头
        tds = tr.find_all('td')
        if len(tds) < 2:
            print("Not enough td elements in tr. Skipping.")
            continue

        album_icon_td = tds[0]
        album_name_td = tds[1]

        album_a = album_icon_td.find('a', href=True)
        album_img = album_icon_td.find('img', src=True)
        if not album_a or not album_img:
            print("Album link or image not found. Skipping.")
            continue

        album_link = urljoin(BASE_URL, album_a['href'])
        album_img_url = album_img['src']

        # 从第二个td中提取专辑名称
        album_name_a = album_name_td.find('a', href=True)
        if album_name_a:
            album_name = album_name_a.text.strip()
        else:
            album_name = "Unknown Album"

        print(f"Found album: {album_name}")
        print(f"Album link: {album_link}")
        print(f"Image URL: {album_img_url}")

        # 可以选择将专辑名称和链接存储起来，供下载时使用
        # 这里仅返回链接列表
        track_links.add(album_link)

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
    dialog = Toplevel(root)
    dialog.title("Album URL and Download Directory Input")

    # 主框架
    main_frame = Frame(dialog)
    main_frame.pack(padx=10, pady=10)

    # URL标签
    url_label = Label(main_frame, text="Please enter the album URL:")
    url_label.grid(row=0, column=0, sticky='w')

    # 获取上次的URL或使用默认
    last_url = read_last_url(DEFAULT_DOWNLOAD_DIR)
    url_var = tk.StringVar(value=last_url)

    # URL输入框
    url_entry = Entry(main_frame, textvariable=url_var, width=60)
    url_entry.grid(row=1, column=0, padx=(0,5), pady=5, sticky='w')

    # Search按钮
    search_button = Button(main_frame, text="Search...", command=lambda: open_search_window(dialog, url_var))
    search_button.grid(row=1, column=1, padx=(5,0), pady=5)

    # 记住URL的复选框
    remember_var = BooleanVar()
    # 如果存在上次的URL且不是默认，则默认选中
    remember_var.set(os.path.exists(os.path.join(DEFAULT_DOWNLOAD_DIR, LAST_URL_FILENAME)))

    remember_check = Checkbutton(main_frame, text="Remember this URL", variable=remember_var)
    remember_check.grid(row=2, column=0, columnspan=2, sticky='w', pady=(5,10))

    # 下载目录选择
    download_dir_label = Label(main_frame, text="Select download directory:")
    download_dir_label.grid(row=3, column=0, sticky='w')

    download_dir_var = tk.StringVar(value=DEFAULT_DOWNLOAD_DIR)

    download_dir_entry = Entry(main_frame, textvariable=download_dir_var, width=60)
    download_dir_entry.grid(row=4, column=0, padx=(0,5), pady=5, sticky='w')

    browse_button = Button(main_frame, text="Browse...", command=lambda: browse_directory(download_dir_var))
    browse_button.grid(row=4, column=1, padx=(5,0), pady=5)

    # 线程数选择
    threads_label = Label(main_frame, text="Select number of threads:")
    threads_label.grid(row=5, column=0, sticky='w', pady=(10,0))

    thread_var = tk.IntVar(value=DEFAULT_THREADS)
    thread_option = OptionMenu(main_frame, thread_var, *THREAD_OPTIONS)
    thread_option.config(width=10)
    thread_option.grid(row=6, column=0, sticky='w', pady=5)

    # 下载按钮
    proceed_button = Button(main_frame, text="Download", command=lambda: proceed(url_var.get(), download_dir_var.get(), thread_var.get(), remember_var.get(), dialog, root))
    proceed_button.grid(row=7, column=0, columnspan=2, pady=(10,0))

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

# 打开搜索窗口
def open_search_window(parent_window, url_var):
    search_window = Toplevel(parent_window)
    search_window.title("Search Albums")
    search_window.geometry("800x600")  # 增加窗口尺寸以适应内容

    # 搜索框
    search_label = Label(search_window, text="Enter search keyword:")
    search_label.pack(padx=10, pady=(10, 0))

    search_keyword_var = tk.StringVar()
    search_entry = Entry(search_window, textvariable=search_keyword_var, width=50)
    search_entry.pack(padx=10, pady=5)

    # 搜索按钮
    search_button = Button(search_window, text="Search", command=lambda: perform_search(search_keyword_var.get(), search_window, url_var))
    search_button.pack(padx=10, pady=5)

    # 结果显示框架
    result_frame = Frame(search_window)
    result_frame.pack(padx=10, pady=10, fill='both', expand=True)

    # 滚动条
    canvas = Canvas(result_frame)
    scrollbar = Scrollbar(result_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 存储搜索结果
    search_window.scrollable_frame = scrollable_frame

# 执行搜索
def perform_search(keyword, search_window, url_var):
    if not keyword.strip():
        messagebox.showerror("Input Error", "Search keyword cannot be empty.")
        return

    search_url = f"{BASE_URL}/search?search={keyword}"
    print(f"Searching for keyword: {keyword}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        messagebox.showerror("Search Error", f"Failed to perform search. Error: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    album_list_div = soup.find('div', class_='albumListDiv')
    if not album_list_div:
        messagebox.showinfo("No Results", "No albums found for the given keyword.")
        return

    album_table = album_list_div.find('table', class_='albumList')
    if not album_table:
        messagebox.showinfo("No Results", "No albums found for the given keyword.")
        return

    # 清空之前的搜索结果
    for widget in search_window.scrollable_frame.winfo_children():
        widget.destroy()

    albums_found = False
    for tr in album_table.find_all('tr')[1:]:  # 跳过表头
        tds = tr.find_all('td')
        if len(tds) < 2:
            print("Not enough td elements in tr. Skipping.")
            continue

        album_icon_td = tds[0]
        album_name_td = tds[1]

        album_a = album_icon_td.find('a', href=True)
        album_img = album_icon_td.find('img', src=True)
        if not album_a or not album_img:
            print("Album link or image not found. Skipping.")
            continue

        album_link = urljoin(BASE_URL, album_a['href'])
        album_img_url = album_img['src']

        # 从第二个td中提取专辑名称
        album_name_a = album_name_td.find('a', href=True)
        if album_name_a:
            album_name = album_name_a.text.strip()
        else:
            album_name = "Unknown Album"

        print(f"Found album: {album_name}")
        print(f"Album link: {album_link}")
        print(f"Image URL: {album_img_url}")

        # 下载图片
        try:
            img_response = requests.get(album_img_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
                Chrome/58.0.3029.110 Safari/537.3'
            })
            img_response.raise_for_status()
            image = Image.open(io.BytesIO(img_response.content))
            image = image.resize((50, 50), Image.Resampling.LANCZOS)  # 使用新的缩放方法
            photo = ImageTk.PhotoImage(image)
            image_references.append(photo)  # 保持引用
            print(f"Successfully downloaded image for album: {album_name}")
        except Exception as e:
            print(f"Failed to download or open image for album '{album_name}'. Error: {e}")
            photo = None

        # 创建显示专辑的框架
        album_frame = Frame(search_window.scrollable_frame, borderwidth=1, relief='solid', padx=5, pady=5)
        album_frame.pack(fill='x', pady=2)

        # 图像标签
        if photo:
            img_label = Label(album_frame, image=photo)
            img_label.pack(side='left', padx=(0,10))
        else:
            img_label = Label(album_frame, text="No Image", width=10, height=5)
            img_label.pack(side='left', padx=(0,10))

        # 专辑名称标签
        name_label = Label(album_frame, text=album_name, font=("Arial", 12, "bold"))
        name_label.pack(side='top', anchor='w')

        # 专辑链接按钮
        album_button = Button(album_frame, text="Open Album", fg="blue", cursor="hand2", anchor='w', justify='left', command=lambda link=album_link: select_album(link, url_var, search_window))
        album_button.pack(side='left', fill='x', expand=True)

        albums_found = True

    if not albums_found:
        messagebox.showinfo("No Results", "No albums found for the given keyword.")

# 选择专辑
def select_album(album_link, url_var, search_window):
    url_var.set(album_link)
    search_window.destroy()

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
    # Proceed to ask for download formats
    ask_user_for_download_options(url, download_dir, thread_count, root)

# 界面交互，允许用户选择下载格式
def ask_user_for_download_options(album_url, download_dir, thread_count, root):
    # 创建新的顶级窗口
    checkbox_window = Toplevel(root)
    checkbox_window.title("Select Download Formats")

    # 主框架
    main_frame = Frame(checkbox_window)
    main_frame.pack(padx=10, pady=10)

    # 选择下载格式的变量
    flac_var = IntVar()
    wav_var = IntVar()
    mp3_var = IntVar()

    # 复选框
    flac_check = Checkbutton(main_frame, text="Download FLAC", variable=flac_var)
    wav_check = Checkbutton(main_frame, text="Download WAV", variable=wav_var)
    mp3_check = Checkbutton(main_frame, text="Download MP3", variable=mp3_var)

    flac_check.pack(anchor='w', padx=20, pady=2)
    wav_check.pack(anchor='w', padx=20, pady=2)
    mp3_check.pack(anchor='w', padx=20, pady=2)

    # 下载按钮
    proceed_button = Button(main_frame, text="Start Download", command=lambda: start_download(album_url, download_dir, thread_count, flac_var.get(), wav_var.get(), mp3_var.get(), checkbox_window, root))
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
    root.geometry("600x400")
    ask_user_for_album_link(root)
