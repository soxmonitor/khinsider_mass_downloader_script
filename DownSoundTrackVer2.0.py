import os
import re
import time
import tkinter as tk
from tkinter import simpledialog, Checkbutton, IntVar
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib.parse import unquote
from urllib3.util.retry import Retry

# 下载并保存文件，支持断点续传和重试机制

def download_and_save(download_link):
    try:
        # 获取解码后的文件名
        file_name = unquote(download_link.split('/')[-1])

        # 检查文件是否已存在
        if os.path.exists(file_name):
            print(f"File {file_name} already exists. Skipping download.")
            return

        # 下载文件
        download_response = requests.get(download_link)
        extension = download_link.split('.')[-1]

        # 清理文件名，去除不合法字符
        safe_file_name = re.sub(r'[<>:"/\\|?*]', '', file_name)
        safe_file_name = re.sub(r'[^\w\s.-]', '', safe_file_name)

        # 确保文件名的扩展名正确
        if not safe_file_name.endswith(f'.{extension}'):
            safe_file_name = f'{safe_file_name[:95]}.{extension}'

        # 保存文件
        with open(safe_file_name, 'wb') as f:
            f.write(download_response.content)
        print(f'Downloaded {safe_file_name}')

    except Exception as e:
        print(f"Failed to download {download_link}. Error: {e}")


# 下载音轨

def download_tracks(album_url, download_flac, download_wav, download_mp3):
    track_links = get_track_links(album_url)
    for link in track_links:
        track_page = requests.get(link)
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
            download_and_save(flac_link)
        elif download_wav and wav_link:
            download_and_save(wav_link)
        elif download_mp3 and mp3_link:
            download_and_save(mp3_link)
        else:
            print(f'No download link found for {link}')

# 获取音轨链接
def get_track_links(album_url):
    response = requests.get(album_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    track_links = set()
    base_url = 'https://downloads.khinsider.com'

    for link in soup.find_all('a'):
        if 'href' in link.attrs:
            href = link['href']
            full_link = href if href.startswith('http') else base_url + href
            if full_link.endswith(('.mp3', '.flac', '.wav')):
                track_links.add(full_link)  
    return track_links

# 界面交互
def ask_user_for_album_link(root):
    root.withdraw()
    flac_var = IntVar()
    wav_var = IntVar()
    mp3_var = IntVar()
    album_url = simpledialog.askstring("Input", "Please enter the album URL:", parent=root)

    if album_url:
        checkbox_window = tk.Toplevel(root)
        flac_check = Checkbutton(checkbox_window, text="Download FLAC", variable=flac_var)
        wav_check = Checkbutton(checkbox_window, text="Download WAV", variable=wav_var)
        mp3_check = Checkbutton(checkbox_window, text="Download MP3", variable=mp3_var)
        flac_check.pack()
        wav_check.pack()
        mp3_check.pack()
        proceed_button = tk.Button(checkbox_window, text="Download", command=lambda: proceed(album_url, flac_var.get(), wav_var.get(), mp3_var.get(), checkbox_window, root))
        proceed_button.pack()
        checkbox_window.mainloop()

# 开始下载
def proceed(url, flac, wav, mp3, window, root):
    window.destroy()
    download_tracks(url, flac, wav, mp3)
    root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    ask_user_for_album_link(root)
