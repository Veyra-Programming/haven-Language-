@echo off
@rem ============================================================================
@rem Haven Programming Language Launcher (v1.0.0 Production Core)
@rem Open Digital Continuity Standard (ODCS) by Anirudha Puthraya
@rem ============================================================================
@setlocal
@set "HAVENHOME=%~dp0"
@set "HAVENPATH=%~dp0Lib;%~dp0"
@set "HAVEN_HOME=%~dp0"
@set "HAVEN_PATH=%~dp0Lib;%~dp0"
@set "PYTHONHOME=%~dp0"
@set "PYTHONPATH=%~dp0Lib;%~dp0"
@"%~dp0PCbuild\amd64\haven.exe" "%~dp0haven.py" %*
