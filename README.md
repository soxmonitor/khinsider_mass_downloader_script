# khinsider_mass_downloader_script / Khinsider 游戏内原声带下载脚本

This is a script that can download FLAC , WAV and MP3 format music from the famous game soundtrack website **khinsider**.

## My Goal is always to create a user friendly script ## 
##                   傻瓜式教程(Windows only)      ##
1，Git pull 整个仓库（或者你也可以直接下载 Multi-ThreadVer1.01.py, DepCehcker.ps1, Lazybutton_AllinOne.bat这三个文件，将这些文件放在一个文件夹下） 

2，直接双击Lazybutton_AllinOne.bat

3, 在弹出的窗口中点search按钮，并输入关键词，脚本会为你自动找到匹配专辑，然后，点击Open Album，网址会自动填入url栏。其余config请自行探索。
效果演示：![屏幕截图 2024-12-30 032603](https://github.com/user-attachments/assets/20ab3c26-f803-4ba1-86ae-f8a50fcd5d8e)


### To use this script correctly, you need to follow the following steps: (Only for non-Windows users)

1. Download the file named `DownSoundTrack.py` from the repo.
2. Install Python and add it to your system path so that you can call `python` in the cmd directly. (If you already installed Python, skip)
3. Install `requests` and `beautifulsoup4` libraries from PyPI. Simply run `pip install requests beautifulsoup4`, or if you are using Windows, you can download the `DepCheker.bat` to install them automatically. (If you already have the dependencies, skip)
4. Run the cmd (Command Prompt) by pressing `Win + R`, then typing `cmd`. Use the command `cd` to navigate to the directory where you put the script. The script will download the music to this directory later.
5. Run `python DownSoundTrack.py`, and a small window will pop up asking for the album URL. You need to open your browser and find the album's page URL. Taking the galgame **HENTAI PRISON** (ヘンタイ・プリズン) as an example, if you want to download its OST (Original Sound Track), search for it and find the page URL as `https://downloads.khinsider.com/game-soundtracks/album/hentai-prison-original-soundtrack-2022` (check the image below), then copy it, paste it into the small window, and click OK.
   
   ![Screenshot](https://github.com/user-attachments/assets/b63e9179-e46f-4c89-8184-ba749bb264b8)

6. Then, another window will pop up asking which format of music you want: MP3 or FLAC or WAV. Note that some albums only provide MP3 format, so it will raise an error if you try to download FLAC or WAV in this situation.
7. Congratulations! The download process has started! If you encounter any errors that you can't figure out, file an issue.


