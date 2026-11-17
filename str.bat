@echo off
@rem =====================================================================
@rem Star Language CLI Launcher (str)
@rem Zero-JS Flutter UI, Universal Mobile & Desktop Engine
@rem Unified Haven & Star Ecosystem Launcher
@rem =====================================================================
@setlocal

@if exist "%LOCALAPPDATA%\Programs\Star\bin\star.exe" (
    "%LOCALAPPDATA%\Programs\Star\bin\star.exe" %*
    exit /b %ERRORLEVEL%
)

@if exist "%LOCALAPPDATA%\Programs\Star\bin\star.bat" (
    "%LOCALAPPDATA%\Programs\Star\bin\star.bat" %*
    exit /b %ERRORLEVEL%
)

@set "HAVENHOME=%~dp0"
@set "HAVENPATH=%~dp0Lib;%~dp0"
@set "PYTHONHOME=%~dp0"
@set "PYTHONPATH=%~dp0Lib;%~dp0"
@"%~dp0PCbuild\amd64\haven.exe" -c "import str, sys; sys.exit(str.StarVM.run_file(sys.argv[1]) if len(sys.argv) > 1 else 0)" %*
