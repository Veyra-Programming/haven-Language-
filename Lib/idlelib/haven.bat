@echo off
rem Start Haven IDE using the Haven interpreter (ODCS Native Edition)
set CURRDIR=%~dp0
if exist "%CURRDIR%..\..\PCbuild\amd64\havenw_d.exe" (
    start "Haven IDE" "%CURRDIR%..\..\PCbuild\amd64\havenw_d.exe" "%CURRDIR%idle.pyw" %*
) else if exist "%CURRDIR%..\..\PCbuild\amd64\haven_d.exe" (
    start "Haven IDE" "%CURRDIR%..\..\PCbuild\amd64\haven_d.exe" "%CURRDIR%idle.pyw" %*
) else (
    start "Haven IDE" "%CURRDIR%..\..\haven.bat" -m idle %*
)
