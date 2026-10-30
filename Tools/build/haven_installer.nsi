; ==============================================================================
; Haven Programming Language v1.0.0 (ODCS Native Edition) - NSIS Installer
; Standards Architect: Anirudha Puthraya
; Target Platform: Windows x64
; ==============================================================================

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinMessages.nsh"

; ------------------------------------------------------------------------------
; General Definitions
; ------------------------------------------------------------------------------
Name "Haven 1.0.0"
!define PRODUCT_NAME "Haven Programming Language"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "Anirudha Puthraya"
!define PRODUCT_WEB_SITE "https://github.com/haven-lang"
!define PRODUCT_DIR_REGKEY "Software\HavenLanguage\Haven"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\Haven"
!define PRODUCT_UNINST_ROOT_KEY HKCU

; Output Installer
OutFile "..\..\dist\Haven-1.0.0-win64-Setup.exe"

; Default Installation Directory (Per-User, No UAC prompt required)
InstallDir "$LOCALAPPDATA\Programs\Haven"
InstallDirRegKey HKCU "${PRODUCT_DIR_REGKEY}" ""

; Request user-level execution
RequestExecutionLevel user

; Compression Options
SetCompressor /SOLID lzma

; Icons
!define MUI_ICON "..\..\PC\icons\haven.ico"
!define MUI_UNICON "..\..\PC\icons\haven.ico"

; ------------------------------------------------------------------------------
; Modern UI Interface Configuration
; ------------------------------------------------------------------------------
!define MUI_HEADERIMAGE
!define MUI_ABORTWARNING

; Welcome Page
!define MUI_WELCOMEPAGE_TITLE "Welcome to Haven 1.0.0 Setup"
!define MUI_WELCOMEPAGE_TEXT "Haven is a high-performance, developer-friendly programming language natively designed for the Open Digital Continuity Standard (ODCS) by Anirudha Puthraya.$\r$\n$\r$\nThis wizard will install Haven 1.0.0, the complete Standard Library, native Tcl/Tk 9.0 GUI runtime, and Haven IDE (IDLE) onto your computer.$\r$\n$\r$\nClick Next to continue."
!insertmacro MUI_PAGE_WELCOME

; License Page (ODCS & Haven License)
!define MUI_LICENSEPAGE_TEXT_TOP "Please review the license terms before installing Haven:"
!insertmacro MUI_PAGE_LICENSE "..\..\LICENSE"

; Components Page
!insertmacro MUI_PAGE_COMPONENTS

; Directory Page
!insertmacro MUI_PAGE_DIRECTORY

; Installation Page
!insertmacro MUI_PAGE_INSTFILES

; Finish Page
!define MUI_FINISHPAGE_RUN "$INSTDIR\havenw.exe"
!define MUI_FINISHPAGE_RUN_PARAMETERS "-m idlelib"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Haven IDE (ODCS Edition) now"
!define MUI_FINISHPAGE_LINK "Open Digital Continuity Standard (ODCS) Specification"
!define MUI_FINISHPAGE_LINK_LOCATION "https://devguide.python.org/"
!insertmacro MUI_PAGE_FINISH

; Uninstaller Pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; ------------------------------------------------------------------------------
; Installer Sections
; ------------------------------------------------------------------------------

Section "Haven Core Runtime (Required)" SecCore
    SectionIn RO
    SetOutPath "$INSTDIR"
    
    ; Main Executables and Core Runtime
    File "..\..\dist\Haven-1.0.0-win64\haven.exe"
    File "..\..\dist\Haven-1.0.0-win64\havenw.exe"
    File "..\..\dist\Haven-1.0.0-win64\python.exe"
    File "..\..\dist\Haven-1.0.0-win64\pythonw.exe"
    File "..\..\dist\Haven-1.0.0-win64\python316.dll"
    File "..\..\dist\Haven-1.0.0-win64\python3.dll"
    File "..\..\dist\Haven-1.0.0-win64\vcruntime140.dll"
    File "..\..\dist\Haven-1.0.0-win64\vcruntime140_1.dll"
    File "..\..\dist\Haven-1.0.0-win64\haven.ico"
    File "..\..\dist\Haven-1.0.0-win64\haven.bat"
    File "..\..\dist\Haven-1.0.0-win64\haven_idle.bat"
    
    ; Extra Core DLLs
    File /nonfatal "..\..\dist\Haven-1.0.0-win64\sqlite3.dll"
    File /nonfatal "..\..\dist\Haven-1.0.0-win64\libcrypto-3.dll"
    File /nonfatal "..\..\dist\Haven-1.0.0-win64\libssl-3.dll"
    File /nonfatal "..\..\dist\Haven-1.0.0-win64\libffi-8.dll"
    File /nonfatal "..\..\dist\Haven-1.0.0-win64\zlib1.dll"
    File /nonfatal "..\..\dist\Haven-1.0.0-win64\tcl90.dll"
    File /nonfatal "..\..\dist\Haven-1.0.0-win64\tcl9tk90.dll"
    File /nonfatal "..\..\dist\Haven-1.0.0-win64\libtommath.dll"

    ; Compiled Binary Extensions
    SetOutPath "$INSTDIR\DLLs"
    File /r "..\..\dist\Haven-1.0.0-win64\DLLs\*.*"

    ; Standard Library
    SetOutPath "$INSTDIR\Lib"
    File /r "..\..\dist\Haven-1.0.0-win64\Lib\*.*"

    ; Tcl/Tk 9.0 Assets
    SetOutPath "$INSTDIR\tcl"
    File /r "..\..\dist\Haven-1.0.0-win64\tcl\*.*"

    ; Write Uninstaller
    SetOutPath "$INSTDIR"
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Register in Installed Programs
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "Haven 1.0.0 (ODCS Native Edition)"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "QuietUninstallString" '"$INSTDIR\Uninstall.exe" /S'
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\haven.ico"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "NoModify" 1
    WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "NoRepair" 1
SectionEnd

Section "Add Haven to PATH Environment" SecPath
    ; Append $INSTDIR to User PATH in HKCU\Environment
    ReadRegStr $0 HKCU "Environment" "Path"
    ${If} $0 == ""
        WriteRegStr HKCU "Environment" "Path" "$INSTDIR;$INSTDIR\Scripts"
    ${Else}
        ; Check if already exists
        Push "$INSTDIR"
        Push "$0"
        Call StrStr
        Pop $1
        ${If} $1 == ""
            WriteRegStr HKCU "Environment" "Path" "$0;$INSTDIR;$INSTDIR\Scripts"
        ${EndIf}
    ${EndIf}
    
    ; Notify Windows of environment variable changes
    SendMessage ${HWND_BROADCAST} ${WM_SETTINGCHANGE} 0 "STR:Environment" /TIMEOUT=5000
SectionEnd

Section "Register .hvn File Associations" SecAssoc
    ; Register .hvn and .haven extensions
    WriteRegStr HKCU "Software\Classes\.hvn" "" "Haven.SourceFile"
    WriteRegStr HKCU "Software\Classes\.haven" "" "Haven.SourceFile"
    WriteRegStr HKCU "Software\Classes\Haven.SourceFile" "" "Haven Source File (ODCS)"
    WriteRegStr HKCU "Software\Classes\Haven.SourceFile\DefaultIcon" "" "$INSTDIR\haven.ico,0"
    WriteRegStr HKCU "Software\Classes\Haven.SourceFile\shell\open" "" "Run with Haven"
    WriteRegStr HKCU "Software\Classes\Haven.SourceFile\shell\open\command" "" '"$INSTDIR\haven.exe" "%1" %*'
    WriteRegStr HKCU "Software\Classes\Haven.SourceFile\shell\edit" "" "Edit with Haven IDE"
    WriteRegStr HKCU "Software\Classes\Haven.SourceFile\shell\edit\command" "" '"$INSTDIR\havenw.exe" -m idlelib "%1"'
SectionEnd

Section "Start Menu & Desktop Shortcuts" SecShortcuts
    ; Start Menu Shortcuts
    CreateDirectory "$SMPROGRAMS\Haven 1.0.0"
    CreateShortcut "$SMPROGRAMS\Haven 1.0.0\Haven 1.0.0 (Command Line).lnk" "$INSTDIR\haven.exe" "" "$INSTDIR\haven.ico" 0
    CreateShortcut "$SMPROGRAMS\Haven 1.0.0\Haven IDE (IDLE).lnk" "$INSTDIR\havenw.exe" "-m idlelib" "$INSTDIR\haven.ico" 0
    CreateShortcut "$SMPROGRAMS\Haven 1.0.0\Uninstall Haven.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0

    ; Desktop Shortcut
    CreateShortcut "$DESKTOP\Haven IDE.lnk" "$INSTDIR\havenw.exe" "-m idlelib" "$INSTDIR\haven.ico" 0
SectionEnd

; ------------------------------------------------------------------------------
; Component Descriptions
; ------------------------------------------------------------------------------
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "The complete Haven language runtime engine, standard library, and Tcl/Tk 9.0 graphical assets."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPath} "Adds Haven to your environment PATH so 'haven' and 'havenw' can be invoked from any Command Prompt or PowerShell."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecAssoc} "Associates .hvn and .haven files to execute with Haven and edit with Haven IDE."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecShortcuts} "Creates convenient shortcuts on your Desktop and in the Windows Start Menu."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; ------------------------------------------------------------------------------
; Helper Functions
; ------------------------------------------------------------------------------
Function StrStr
  Exch $R1 ; substring
  Exch
  Exch $R2 ; string
  Push $R3
  Push $R4
  Push $R5
  StrLen $R3 $R1
  StrCpy $R4 0
  loop:
    StrCpy $R5 $R2 $R3 $R4
    StrCmp $R5 $R1 found
    StrCmp $R5 "" notfound
    IntOp $R4 $R4 + 1
    Goto loop
  found:
    StrCpy $R1 $R2 "" $R4
    Goto done
  notfound:
    StrCpy $R1 ""
  done:
    Pop $R5
    Pop $R4
    Pop $R3
    Pop $R2
    Exch $R1
FunctionEnd

; ------------------------------------------------------------------------------
; Uninstaller Section
; ------------------------------------------------------------------------------
Section "Uninstall"
    ; Remove Shortcuts
    Delete "$DESKTOP\Haven IDE.lnk"
    RMDir /r "$SMPROGRAMS\Haven 1.0.0"

    ; Remove File Associations
    DeleteRegKey HKCU "Software\Classes\.hvn"
    DeleteRegKey HKCU "Software\Classes\.haven"
    DeleteRegKey HKCU "Software\Classes\Haven.SourceFile"

    ; Remove Add/Remove Programs entry
    DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
    DeleteRegKey HKCU "${PRODUCT_DIR_REGKEY}"

    ; Remove Files
    RMDir /r "$INSTDIR\DLLs"
    RMDir /r "$INSTDIR\Lib"
    RMDir /r "$INSTDIR\tcl"
    Delete "$INSTDIR\*.*"
    RMDir "$INSTDIR"

    ; Broadcast setting change
    SendMessage ${HWND_BROADCAST} ${WM_SETTINGCHANGE} 0 "STR:Environment" /TIMEOUT=5000
SectionEnd
