@echo off
rem ============================================================================
rem Haven IDE Desktop Launcher v1.0.0
rem Standards Architect: Anirudha Puthraya
rem ============================================================================
setlocal

set "HAVEN_ROOT=%~dp0"
set "PYTHONPATH=%HAVEN_ROOT%Lib;%HAVEN_ROOT%"
set "PATH=%HAVEN_ROOT%PCbuild\amd64;%PATH%"

if exist "%HAVEN_ROOT%PCbuild\amd64\havenw.exe" (
    start "" "%HAVEN_ROOT%PCbuild\amd64\havenw.exe" -m idlelib %*
) else if exist "%HAVEN_ROOT%PCbuild\amd64\haven.exe" (
    start "" "%HAVEN_ROOT%PCbuild\amd64\haven.exe" -m idlelib %*
) else if exist "%HAVEN_ROOT%PCbuild\amd64\havenw_d.exe" (
    start "" "%HAVEN_ROOT%PCbuild\amd64\havenw_d.exe" -m idlelib %*
) else if exist "%HAVEN_ROOT%PCbuild\amd64\haven_d.exe" (
    start "" "%HAVEN_ROOT%PCbuild\amd64\haven_d.exe" -m idlelib %*
) else (
    echo [ERROR] Haven 1.0.0 runtime binary not found in PCbuild\amd64\
    echo Please run build.bat -c Release -p x64 first.
    pause
    exit /b 1
)
