@echo off
rem ============================================================================
rem Haven Graphical IDE Desktop Launcher v2.1.1 GA
rem Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
rem Standards Architect: Anirudha Puthraya
rem ============================================================================
setlocal

set "HAVEN_ROOT=%~dp0"
set "HAVENHOME=%HAVEN_ROOT%"
set "HAVENPATH=%HAVEN_ROOT%Lib;%HAVEN_ROOT%"
set "PYTHONHOME="
set "PYTHONPATH="
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
    echo [ERROR] Haven 2.1.1 GA runtime binary not found in PCbuild\amd64\
    pause
    exit /b 1
)
