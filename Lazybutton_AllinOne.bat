@echo off
:: 检查是否以管理员身份运行
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 正在请求管理员权限...
    PowerShell -Command "Start-Process -FilePath '%~0' -Verb RunAs"
    EXIT /B
)

:: 以绕过执行策略的方式运行 PowerShell 脚本
PowerShell -NoProfile -ExecutionPolicy Bypass -File "D:\Git-Local-Repo\khinsider_mass_downloader_script\DepChecker.ps1"

:: 暂停以便查看输出
pause
