# khinsider_mass_downloader_script
This is a scrip that can download flac and mp3 format music from famous game soundtrack website khinsider

To use this script correctly, you need to follow the following steps:
    1, Download the file named DownSoundTrack.py in repo.
    2, Install python and add it to your system path so that you can call "python" in cmd directly. (If you already installed python, skip)
    3, Install requests and beautifulsoup4 lib from Pypi (Simply just run pip install requests beautifulsoup4), or if you are using windows, you can download the DepCheker.bat to install it automatically.  (If you already have the deps, skip)
    4, Run cmd (the Command Prompt) by using key win + r then type in "cmd", using command 'cd' to navigate to the directory you put the script, the script will put those download music under this directory later.
    5, Run 'python DownSoundTrack.py' , then, a small windows will pop up, asking for album url. You need to open your browser and then find the album's album page url. Taking the galgame HENTAI PRISON(ヘンタイ・プリズン) as an example, you wan to download its OST (original Sound Track), then search for it and find out the page url as "https://downloads.khinsider.com/game-soundtracks/album/hentai-prison-original-soundtrack-2022" (Check img below), then copy it, paste it to the small windows, click ok. 
    ![屏幕截图 2024-12-05 153741](https://github.com/user-attachments/assets/b63e9179-e46f-4c89-8184-ba749bb264b8)
    6, Then, another window will pop up, it will ask you which format of music you want, mp3 or flac. Notice that some of album only provide mp3 fromat, so it will raise error if you try to donwload flac at this situation.
    7, Congratulations! Download Process has been started! If you still get any error that you can't figure out, file an issue.
