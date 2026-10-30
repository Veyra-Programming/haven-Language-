"""
Haven Language Standalone Distribution Packager
Packages Haven v1.0.0 into a completely self-contained, clean Windows runtime.
Free from source code (.c, .h, .vcxproj, etc.) and ready for end-user deployment.
"""

import os
import sys
import shutil
import compileall
import zipfile

def package():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dist_root = os.path.join(repo_root, "dist")
    haven_dir = os.path.join(dist_root, "Haven-1.0.0-win64")
    
    print(f"[*] Packaging Haven v1.0.0 into: {haven_dir}")
    if os.path.exists(haven_dir):
        shutil.rmtree(haven_dir)
    os.makedirs(haven_dir, exist_ok=True)
    
    amd64_bin = os.path.join(repo_root, "PCbuild", "amd64")
    assert os.path.exists(amd64_bin), f"Release build not found in {amd64_bin}"
    
    # 1. Primary Executables & Core DLLs
    print("[+] Copying executables and core runtime DLLs...")
    binaries = [
        "haven.exe", "havenw.exe",
        "python.exe", "pythonw.exe",
        "python316.dll", "python3.dll",
        "vcruntime140.dll", "vcruntime140_1.dll",
        "sqlite3.dll", "libcrypto-3.dll", "libssl-3.dll", "libffi-8.dll",
        "zlib1.dll", "tcl90.dll", "tcl9tk90.dll"
    ]
    for b in binaries:
        src = os.path.join(amd64_bin, b)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(haven_dir, b))
        else:
            print(f"    [!] Warning: {b} not found in {amd64_bin}")
            
    # Copy Tcl/Tk binary DLLs (including libtommath.dll)
    tcl_bin_dir = os.path.join(repo_root, "externals", "tcltk-9.0.4.0", "amd64", "bin")
    if os.path.exists(tcl_bin_dir):
        for f in os.listdir(tcl_bin_dir):
            if f.endswith(".dll"):
                shutil.copy2(os.path.join(tcl_bin_dir, f), os.path.join(haven_dir, f))

    # 2. Extension Modules (.pyd) into DLLs/
    dlls_dir = os.path.join(haven_dir, "DLLs")
    os.makedirs(dlls_dir, exist_ok=True)
    print("[+] Copying compiled extension modules into DLLs/...")
    for f in os.listdir(amd64_bin):
        if f.endswith(".pyd") and not f.endswith("_d.pyd"):
            shutil.copy2(os.path.join(amd64_bin, f), os.path.join(dlls_dir, f))
            
    # Copy support DLLs into DLLs/ as well for lookup safety
    for d in ["sqlite3.dll", "libcrypto-3.dll", "libssl-3.dll", "tcl90.dll", "tcl9tk90.dll"]:
        src = os.path.join(amd64_bin, d)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dlls_dir, d))
    if os.path.exists(tcl_bin_dir):
        for f in os.listdir(tcl_bin_dir):
            if f.endswith(".dll"):
                shutil.copy2(os.path.join(tcl_bin_dir, f), os.path.join(dlls_dir, f))

    # 3. Standard Library into Lib/
    lib_dst = os.path.join(haven_dir, "Lib")
    lib_src = os.path.join(repo_root, "Lib")
    print("[+] Copying Standard Library to Lib/ (excluding developer tests & C-sources)...")
    
    def ignore_patterns(folder, files):
        # Exclude massive test suites and developer artifacts
        ignored = []
        if os.path.basename(folder) in ("test", "tests", "__pycache__"):
            return files
        for f in files:
            if f.endswith((".c", ".h", ".vcxproj", ".filters", ".obj")):
                ignored.append(f)
        return ignored

    shutil.copytree(lib_src, lib_dst, ignore=ignore_patterns, dirs_exist_ok=True)
    
    # Ensure haven_ai is also included
    haven_ai_src = os.path.join(repo_root, "haven_ai")
    if os.path.exists(haven_ai_src):
        shutil.copytree(haven_ai_src, os.path.join(lib_dst, "haven_ai"), dirs_exist_ok=True)

    # 4. Tcl/Tk Library Data into tcl/
    tcl_src = os.path.join(repo_root, "externals", "tcltk-9.0.4.0", "amd64", "lib")
    tcl_dst = os.path.join(haven_dir, "tcl")
    if os.path.exists(tcl_src):
        print("[+] Copying Tcl/Tk 9.0 library assets into tcl/ for Haven IDE...")
        shutil.copytree(tcl_src, tcl_dst, dirs_exist_ok=True)
        
    # 5. Icons and Launchers
    print("[+] Adding Haven branding and desktop launchers...")
    icon_src = os.path.join(repo_root, "PC", "icons", "haven.ico")
    if os.path.exists(icon_src):
        shutil.copy2(icon_src, os.path.join(haven_dir, "haven.ico"))

    # haven_idle.bat
    idle_bat_content = """@echo off
setlocal
set "HAVEN_DIR=%~dp0"
set "PYTHONPATH=%HAVEN_DIR%Lib;%HAVEN_DIR%"
set "TCL_LIBRARY=%HAVEN_DIR%tcl\\tcl9.0"
set "TK_LIBRARY=%HAVEN_DIR%tcl\\tk9.0"
start "Haven IDE" "%HAVEN_DIR%havenw.exe" -m idlelib %*
"""
    with open(os.path.join(haven_dir, "haven_idle.bat"), "w") as f:
        f.write(idle_bat_content)

    # haven.bat
    haven_bat_content = """@echo off
setlocal
set "HAVEN_DIR=%~dp0"
set "PYTHONPATH=%HAVEN_DIR%Lib;%HAVEN_DIR%"
"%HAVEN_DIR%haven.exe" %*
"""
    with open(os.path.join(haven_dir, "haven.bat"), "w") as f:
        f.write(haven_bat_content)

    # 6. Precompile Standard Library to Bytecode
    print("[+] Precompiling Standard Library to optimized bytecode...")
    compileall.compile_dir(lib_dst, maxlevels=10, quiet=1)

    # 7. Create Portable ZIP distribution
    zip_path = os.path.join(dist_root, "Haven-1.0.0-win64.zip")
    print(f"[+] Creating Portable ZIP Distribution: {zip_path}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(haven_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, haven_dir)
                zipf.write(full_path, rel_path)
                
    print(f"[✓] Standalone distribution successfully assembled at:\n    {haven_dir}")
    print(f"[✓] Portable ZIP distribution created at:\n    {zip_path}")

if __name__ == "__main__":
    package()
