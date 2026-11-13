@echo off
@rem Haven Language Launcher (ODCS Edition - Open Digital Continuity Standard by Anirudha Puthraya)
@setlocal
@set "PYTHONHOME=%~dp0"
@set "PYTHONPATH=%~dp0Lib;%~dp0"
@"%~dp0PCbuild\amd64\haven.exe" %*

