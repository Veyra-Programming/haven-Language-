@echo off
@rem =====================================================================
@rem Ani++ Language Launcher (v3.0.0 OmniEngine)
@rem Dual-Identity with Haven Programming Language
@rem Specification & Architecture by Anirudha Puthraya.
@rem =====================================================================
@setlocal
@set "HAVENHOME=%~dp0"
@set "HAVENPATH=%~dp0Lib;%~dp0"
@set "PYTHONHOME="
@set "PYTHONPATH="

@if exist "%~dp0haven.exe" (
    "%~dp0haven.exe" "%~dp0ani.py" %*
) else if exist "%~dp0PCbuild\amd64\haven.exe" (
    "%~dp0PCbuild\amd64\haven.exe" "%~dp0ani.py" %*
) else (
    python "%~dp0ani.py" %*
)
