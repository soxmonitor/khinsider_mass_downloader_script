@echo off
setlocal enabledelayedexpansion

:: Prompt the user to choose the audio format
echo Please choose the audio format:
echo 1. FLAC
echo 2. WAV
echo 3. MP3
set /p audio_choice="Enter a number (1-3): "

:: Set the audio format based on user choice
if "%audio_choice%"=="1" (
    set "audio_format=flac"
) else if "%audio_choice%"=="2" (
    set "audio_format=wav"
) else if "%audio_choice%"=="3" (
    set "audio_format=mp3"
) else (
    echo Invalid input, exiting program.
    exit /b
)

:: Get all the specified format audio files in the current directory
for %%f in (*.%audio_format%) do (
    echo Playing file: %%f
    :: Use ffplay directly to play the audio file (with -autoexit to auto-close after playback)
    ffplay -autoexit -nodisp "%%f"
    timeout /t 1 > nul
)

echo Playback finished
endlocal

