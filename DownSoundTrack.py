import re
import tkinter as tk
from tkinter import simpledialog, messagebox, Checkbutton, IntVar
import requests
from bs4 import BeautifulSoup

def download_tracks(album_url, download_flac, download_mp3):
    track_links = get_track_links(album_url)
    for link in track_links:
        track_page = requests.get(link)
        track_soup = BeautifulSoup(track_page.text, 'html.parser')
        flac_link = mp3_link = None

        for a in track_soup.find_all('a'):
            if 'Click here to download as FLAC' in a.text:
                flac_link = a['href']
            if 'Click here to download as MP3' in a.text:
                mp3_link = a['href']

        if download_flac and flac_link:
            download_and_save(flac_link)
        elif download_mp3 and mp3_link:
            download_and_save(mp3_link)
        else:
            print(f'No download link found for {link}')

def download_and_save(download_link):
    try:
        download_response = requests.get(download_link)
        # Extract the file extension
        extension = download_link.split('.')[-1]

        # Create a safe file name by removing unsafe characters
        safe_file_name = re.sub(r'[<>:"/\\|?*]', '', download_link.split('/')[-1])
        safe_file_name = re.sub(r'[^\w\s.-]', '', safe_file_name)

        # Ensure the file name includes the correct extension
        if not safe_file_name.endswith(f'.{extension}'):
            safe_file_name = f'{safe_file_name[:95]}.{extension}'  # Trim the file name to keep the extension within limits

        with open(safe_file_name, 'wb') as f:
            f.write(download_response.content)
        print(f'Downloaded {safe_file_name}')
    except Exception as e:
        print(f"Failed to download {download_link}. Error: {e}")


def get_track_links(album_url):
    response = requests.get(album_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    track_links = []
    base_url = 'https://downloads.khinsider.com'  # 假设基础URL是这个，根据实际情况调整

    for link in soup.find_all('a'):
        if 'href' in link.attrs:
            href = link['href']
            # 检查链接是否是完整的URL
            if href.startswith('http'):
                full_link = href
            else:
                # 补全相对URL
                full_link = base_url + href if href.startswith('/') else base_url + '/' + href
            if full_link.endswith(".mp3") or full_link.endswith(".flac"):
                track_links.append(full_link)
    return track_links

def ask_user_for_album_link(root):
    root.withdraw()
    flac_var = IntVar()
    mp3_var = IntVar()
    album_url = simpledialog.askstring("Input", "Please enter the album URL:", parent=root)

    if album_url:
        checkbox_window = tk.Toplevel(root)
        flac_check = Checkbutton(checkbox_window, text="Download FLAC", variable=flac_var)
        mp3_check = Checkbutton(checkbox_window, text="Download MP3", variable=mp3_var)
        flac_check.pack()
        mp3_check.pack()
        proceed_button = tk.Button(checkbox_window, text="Download", command=lambda: proceed(album_url, flac_var.get(), mp3_var.get(), checkbox_window, root))
        proceed_button.pack()
        checkbox_window.mainloop()

def proceed(url, flac, mp3, window, root):
    window.destroy()
    download_tracks(url, flac, mp3)
    root.quit()  # 正确退出mainloop

if __name__ == "__main__":
    root = tk.Tk()
    ask_user_for_album_link(root)
