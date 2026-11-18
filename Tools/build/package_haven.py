"""
Haven Language Standalone Distribution Packager & Installer Builder
Packages Haven v2.1.1 GA (ODCS Edition) into a self-contained Windows runtime
and compiles a native standalone Windows Setup installer executable (.exe).
Author: Anirudha Puthraya
"""

import compileall
import os
import shutil
import subprocess
import zipfile


def package():
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    dist_root = os.path.join(repo_root, "dist")
    haven_dir = os.path.join(dist_root, "Haven-2.1.1-GA-win64")

    print(f"[*] Packaging Haven v2.1.1 GA into: {haven_dir}")
    if os.path.exists(haven_dir):
        shutil.rmtree(haven_dir)
    os.makedirs(haven_dir, exist_ok=True)

    amd64_bin = os.path.join(repo_root, "PCbuild", "amd64")
    assert os.path.exists(amd64_bin), f"Release build not found in {amd64_bin}"

    # 1. Primary Executables & Core DLLs
    print("[+] Copying executables and core runtime DLLs...")
    binaries = [
        "haven.exe",
        "havenw.exe",
        "python316.dll",
        "python3.dll",
        "vcruntime140.dll",
        "vcruntime140_1.dll",
        "sqlite3.dll",
        "libcrypto-3.dll",
        "libssl-3.dll",
        "libffi-8.dll",
        "zlib1.dll",
        "tcl90.dll",
        "tcl9tk90.dll",
    ]
    for b in binaries:
        src = os.path.join(amd64_bin, b)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(haven_dir, b))
        else:
            print(f"    [!] Note: {b} not in {amd64_bin}")

    # Copy Tcl/Tk binary DLLs
    tcl_bin_dir = os.path.join(
        repo_root, "externals", "tcltk-9.0.4.0", "amd64", "bin"
    )
    if os.path.exists(tcl_bin_dir):
        for f in os.listdir(tcl_bin_dir):
            if f.endswith(".dll"):
                shutil.copy2(
                    os.path.join(tcl_bin_dir, f), os.path.join(haven_dir, f)
                )

    # 2. Extension Modules (.pyd) into DLLs/
    dlls_dir = os.path.join(haven_dir, "DLLs")
    os.makedirs(dlls_dir, exist_ok=True)
    print("[+] Copying compiled extension modules into DLLs/...")
    for f in os.listdir(amd64_bin):
        if f.endswith(".pyd") and not f.endswith("_d.pyd"):
            shutil.copy2(os.path.join(amd64_bin, f), os.path.join(dlls_dir, f))

    # Copy support DLLs into DLLs/ for lookup safety
    for d in [
        "sqlite3.dll",
        "libcrypto-3.dll",
        "libssl-3.dll",
        "tcl90.dll",
        "tcl9tk90.dll",
    ]:
        src = os.path.join(amd64_bin, d)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dlls_dir, d))
    if os.path.exists(tcl_bin_dir):
        for f in os.listdir(tcl_bin_dir):
            if f.endswith(".dll"):
                shutil.copy2(
                    os.path.join(tcl_bin_dir, f), os.path.join(dlls_dir, f)
                )

    # 3. Standard Library into Lib/ (including hvn, str, star, Flutter, Material)
    lib_dst = os.path.join(haven_dir, "Lib")
    lib_src = os.path.join(repo_root, "Lib")
    print(
        "[+] Copying Standard Library to Lib/ (including hvn and str ecosystems)..."
    )

    def ignore_patterns(folder, files):
        ignored = []
        if os.path.basename(folder) in ("test", "tests", "__pycache__"):
            return files
        for f in files:
            if f.endswith((".c", ".h", ".vcxproj", ".filters", ".obj")):
                ignored.append(f)
        return ignored

    shutil.copytree(
        lib_src, lib_dst, ignore=ignore_patterns, dirs_exist_ok=True
    )

    # Copy sitecustomize.py
    sitecust_src = os.path.join(repo_root, "Lib", "sitecustomize.py")
    if os.path.exists(sitecust_src):
        shutil.copy2(sitecust_src, os.path.join(lib_dst, "sitecustomize.py"))

    # 4. Tcl/Tk Library Data into tcl/
    tcl_src = os.path.join(
        repo_root, "externals", "tcltk-9.0.4.0", "amd64", "lib"
    )
    tcl_dst = os.path.join(haven_dir, "tcl")
    if os.path.exists(tcl_src):
        print(
            "[+] Copying Tcl/Tk 9.0 library assets into tcl/ for Haven IDE..."
        )
        shutil.copytree(tcl_src, tcl_dst, dirs_exist_ok=True)

    # 5. Icons, Launchers & Scripts
    print("[+] Adding Haven branding and unified desktop launchers...")
    icon_src = os.path.join(repo_root, "PC", "icons", "haven.ico")
    if os.path.exists(icon_src):
        shutil.copy2(icon_src, os.path.join(haven_dir, "haven.ico"))

    # haven.py entry point
    haven_py_src = os.path.join(repo_root, "haven.py")
    if os.path.exists(haven_py_src):
        shutil.copy2(haven_py_src, os.path.join(haven_dir, "haven.py"))

    # Root launchers
    for launcher in [
        "haven.bat",
        "hvn.bat",
        "str.bat",
        "star.bat",
        "haven_idle.bat",
        "LICENSE",
        "CHANGELOG.md",
    ]:
        l_src = os.path.join(repo_root, launcher)
        if os.path.exists(l_src):
            shutil.copy2(l_src, os.path.join(haven_dir, launcher))

    # 6. Precompile Standard Library to Bytecode
    print("[+] Precompiling Standard Library to optimized bytecode...")
    compileall.compile_dir(lib_dst, maxlevels=10, quiet=1)

    # 7. Create Portable ZIP distribution
    zip_path = os.path.join(dist_root, "Haven-2.1.1-GA-win64.zip")
    print(f"[+] Creating Portable ZIP Distribution: {zip_path}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(haven_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, haven_dir)
                zipf.write(full_path, rel_path)

    # Also keep Haven-1.0.0-win64.zip compatible name if needed
    shutil.copy2(zip_path, os.path.join(dist_root, "Haven-1.0.0-win64.zip"))

    print(
        f"[✓] Standalone distribution successfully assembled at:\n    {haven_dir}"
    )
    print(f"[✓] Portable ZIP distribution created at:\n    {zip_path}")

    # 8. Compile Native Windows Setup Executable (Haven-2.1.1-GA-Setup.exe)
    csc_path = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
    if not os.path.exists(csc_path):
        csc_path = r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"

    installer_cs = os.path.join(repo_root, "Tools", "build", "Installer.cs")
    setup_exe = os.path.join(dist_root, "Haven-2.1.1-GA-Setup.exe")

    if os.path.exists(csc_path) and os.path.exists(installer_cs):
        print(
            f"[+] Compiling Native Windows Setup Executable with C# compiler..."
        )
        cmd = [
            csc_path,
            "/target:winexe",
            "/platform:x64",
            "/optimize+",
            "/reference:System.IO.Compression.dll",
            "/reference:System.IO.Compression.FileSystem.dll",
            f"/win32icon:{icon_src}",
            f"/resource:{zip_path},HavenDistribution.zip",
            f"/out:{setup_exe}",
            installer_cs,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(setup_exe):
            print(
                f"[✓] Native Windows Installer EXE successfully built at:\n    {setup_exe}"
            )
            # Also create Haven-Setup.exe alias
            shutil.copy2(setup_exe, os.path.join(dist_root, "Haven-Setup.exe"))
            shutil.copy2(
                setup_exe,
                os.path.join(dist_root, "Haven-2.1.1-GA-win64-Setup.exe"),
            )
        else:
            print(
                f"[!] C# compilation returned code {res.returncode}:\n{res.stdout}\n{res.stderr}"
            )
    else:
        print("[!] CSC compiler not found, skipping setup.exe build.")


if __name__ == "__main__":
    package()
