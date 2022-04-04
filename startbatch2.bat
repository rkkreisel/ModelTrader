@echo off
Title Check for running process . . .
mode con cols=50 lines=3
set "MyProcess=python.exe"
set delay=1000
:Main
cls
Tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe">nul && (
    echo( & Color 9A
    echo         PROCESS "Python" IS RUNNING !
)||(
    echo( & Color 4C
    echo        PROCESS "Python" IS NOT RUNNING !
	call batchstartmainlocal.bat
)
Timeout /T %delay% /nobreak>nul
Goto Main