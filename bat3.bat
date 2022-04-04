@echo off
Title Check for running process . . .
mode con cols=50 lines=3
set "MyProcess=python"
set delay=5
:Main
cls
tasklist /nh /fi "imagename eq python.exe" | findstr /i "python.exe" >nul && (echo Python is running)|| (Echo Python is not running)
Timeout /T %delay% /nobreak>nul
Goto Main