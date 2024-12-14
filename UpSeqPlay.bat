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

:: Ask user if they want to enable asking logic for each song
set /p ask_logic="Do you want to enable asking logic for each song? [Y/N]: "
if /i "%ask_logic%"=="N" (
    echo Asking logic disabled.
    for %%f in (*.%audio_format%) do (
        echo Playing file: %%f
        ffplay -autoexit -nodisp "%%f"
        timeout /t 1 > nul
    )
) else (
    echo Asking logic enabled.
    for %%f in (*.%audio_format%) do (
        :start_playback
        echo Playing file: %%f
        ffplay -autoexit -nodisp "%%f"
        timeout /t 1 > nul

        :: Use choice command to wait for user input with a 60-second timeout
        choice /C NR /N /T 10 /D N /M "Do you want to play the next file (N) or replay this one (R)? You get 10 secs to choose. [N/R]: "
        if errorlevel 2 (
            goto start_playback
        )
    )
)

echo Playback finished
endlocal


