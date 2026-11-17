@echo off
@rem =====================================================================
@rem Haven Language Launcher (v2.1.1 GA)
@rem Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
@rem Architecture & Design by Anirudha Puthraya.
@rem =====================================================================
@setlocal
@set "HAVENHOME=%~dp0"
@set "HAVENPATH=%~dp0Lib;%~dp0"
@set "PYTHONHOME="
@set "PYTHONPATH="
@"%~dp0PCbuild\amd64\haven.exe" "%~dp0haven.py" %*
