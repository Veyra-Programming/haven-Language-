# ============================================================================
# Haven Programming Language PowerShell Entry Point (v1.0.0 Production Core)
# Open Digital Continuity Standard (ODCS) by Anirudha Puthraya
# ============================================================================
$env:HAVENHOME = "$PSScriptRoot"
$env:HAVENPATH = "$PSScriptRoot\Lib;$PSScriptRoot"
$env:HAVEN_HOME = "$PSScriptRoot"
$env:HAVEN_PATH = "$PSScriptRoot\Lib;$PSScriptRoot"
$env:PYTHONHOME = "$PSScriptRoot"
$env:PYTHONPATH = "$PSScriptRoot\Lib;$PSScriptRoot"
& "$PSScriptRoot\PCbuild\amd64\haven.exe" "$PSScriptRoot\haven.py" @args
