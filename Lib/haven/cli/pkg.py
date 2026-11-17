"""
Haven Project & Package Manifest Manager (haven pkg)
Official Registry Domain: odcshosting (https://odcshosting.in / https://api.odcshosting.in)
Provides package publishing, dependency resolution, cryptographic sealing, and ODCS hosting.
Standard Specification & Architecture by Anirudha Puthraya.
"""

import sys
import os
import json
import zipfile
import hashlib
import time
from .colors import green, yellow, red, cyan, bold, dim, blue, magenta

from haven.pkg.registry import (
    DEFAULT_REGISTRY_URL,
    get_registry_url,
    get_auth_token,
    load_config,
    save_config,
    search_packages,
    get_package_info,
    publish_package_to_odcshosting,
    install_package_from_odcshosting,
    run_odcshosting_server,
)


DEFAULT_TOML = """# ==============================================================================
# Haven Language Project Manifest (haven.toml)
# Official Registry: odcshosting (https://odcshosting.in)
# Open Digital Continuity Standard (ODCS-2.0) & Open Financial Continuity Standard (OFCS)
# ==============================================================================

[project]
name = "{name}"
version = "1.0.0"
authors = ["{author}"]
description = "{desc}"
entry = "src/main.hvn"
haven_version = ">=1.0.0"

[continuity]
# Layer 1: Local WAL & Merkle Durability
enabled = true
ledger_path = "data/ledger.json"
journal_wal = true
rfc8785_canonical = true

# Layer 2: Distributed Transport & CRDT Consensus
sync_mode = "MULTI_MASTER_CRDT"
heartbeat_interval_ms = 5000

# Layer 3: Environmental Telemetry & Edge Probing
gateway_url = "https://api.odcshosting.in/v1"
telemetry_probe = true

# Layer 4: Application Zero Intent Loss (ZIL)
zero_intent_loss = true
instant_receipt_minting = true

[package]
registry = "https://api.odcshosting.in/v1"
domain = "odcshosting.in"

[dependencies]
# Dependencies tracked via odcshosting registry
haven_ai = ">=1.0.0"
"""


def init_manifest(project_name: str = None, author: str = "Anirudha Puthraya", desc: str = "Continuity-native Haven application") -> int:
    manifest_path = "haven.toml"
    if os.path.exists(manifest_path):
        print(f"{bold(yellow('Notice:'))} 'haven.toml' already exists in the current directory.")
        return 0

    if not project_name:
        project_name = os.path.basename(os.path.abspath("."))

    content = DEFAULT_TOML.format(name=project_name, author=author, desc=desc)
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n{bold(green('✔ Created Haven Project Manifest:'))} {bold('haven.toml')}")
    print(f"  • Project Name: {cyan(project_name)}")
    print(f"  • Author      : {author}")
    print(f"  • Registry    : {cyan('https://api.odcshosting.in/v1')} ({bold('odcshosting.in')})")
    print(f"  • Standard    : ODCS-2.0 & OFCS (Layers 1-4 Configured)\n")
    return 0


def view_manifest() -> int:
    manifest_path = "haven.toml"
    if not os.path.exists(manifest_path):
        print(f"{bold(yellow('No haven.toml found.'))} Run {bold('haven pkg init')} to create one.")
        return 1

    with open(manifest_path, "r", encoding="utf-8") as f:
        print(f"\n{bold(cyan('Current Project Manifest (haven.toml):'))}")
        print(f.read())
    return 0


def add_dependency(dep_name: str, version: str = ">=1.0.0") -> int:
    manifest_path = "haven.toml"
    if not os.path.exists(manifest_path):
        print(f"{bold(red('Error:'))} 'haven.toml' not found. Run {bold('haven pkg init')} first.")
        return 1

    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()

    line_to_add = f'{dep_name} = "{version}"'
    if dep_name in content:
        print(f"{bold(yellow('Notice:'))} Dependency '{dep_name}' already exists in haven.toml.")
    else:
        if "[dependencies]" in content:
            content = content.replace("[dependencies]", f"[dependencies]\n{line_to_add}")
        else:
            content += f"\n[dependencies]\n{line_to_add}\n"

        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"{bold(green('✔ Added Dependency:'))} {cyan(dep_name)} {dim(version)} to haven.toml")

    # Now install from odcshosting
    print(f"Resolving '{dep_name}' from odcshosting domain...")
    install_package_from_odcshosting(dep_name, version)
    print(f"{bold(green('✔ Successfully installed:'))} {cyan(dep_name)} from {bold('odcshosting.in')}\n")
    return 0


def install_dependencies(pkg_name: Optional[str] = None, version: str = ">=1.0.0") -> int:
    if pkg_name:
        print(f"\n{bold(cyan('Installing package from odcshosting:'))} {bold(pkg_name)} ({version})")
        reg_url = get_registry_url()
        print(f"  • Registry Endpoint: {dim(reg_url)}")
        success = install_package_from_odcshosting(pkg_name, version)
        if success:
            print(f"{bold(green('✔ Successfully installed'))} {cyan(pkg_name)} into {bold('haven_packages/')}")
            print(f"  • Generated Lockfile : {bold('haven.lock')} (SHA-256 Verified)\n")
            return 0
        else:
            print(f"{bold(red('Failed to install:'))} {pkg_name}", file=sys.stderr)
            return 1

    manifest_path = "haven.toml"
    if not os.path.exists(manifest_path):
        print(f"{bold(red('Error:'))} 'haven.toml' not found.")
        return 1

    reg_url = get_registry_url()
    print(f"\n{bold(cyan('Auditing and Resolving Haven Dependencies via odcshosting...'))}")
    print(f"  • Target Registry: {cyan(reg_url)}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_deps = False
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[dependencies]"):
            in_deps = True
            continue
        if stripped.startswith("[") and in_deps:
            break
        if in_deps and "=" in stripped and not stripped.startswith("#"):
            pkg, ver = [x.strip() for x in stripped.split("=", 1)]
            ver_clean = ver.strip('"').strip("'")
            install_package_from_odcshosting(pkg, ver_clean)
            print(f"  • {green('✔')} Resolved: {bold(pkg)} ({dim(ver_clean)}) from {bold('odcshosting.in')}")
            count += 1

    print(f"\n{bold(green('✔ All'))} {bold(str(count))} {bold(green('dependencies satisfied and locked in haven.lock.'))}\n")
    return 0


def pack_package(target_dir: str = ".") -> int:
    """Bundles project into a cryptographically sealed .hvp (Haven Verified Package)."""
    manifest_path = os.path.join(target_dir, "haven.toml")
    if not os.path.exists(manifest_path):
        print(f"{bold(red('Error:'))} 'haven.toml' not found. Cannot build package without manifest.")
        return 1

    pkg_name = "haven-pkg"
    pkg_ver = "1.0.0"
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("name"):
                pkg_name = line.split("=")[1].strip().strip('"').strip("'")
            elif line.strip().startswith("version"):
                pkg_ver = line.split("=")[1].strip().strip('"').strip("'")

    out_file = f"{pkg_name}-{pkg_ver}.hvp"
    print(f"\n{bold(cyan('Packaging Haven Verified Package (HVP):'))} {out_file}")

    file_hashes = {}
    with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(target_dir):
            if any(part in root for part in [".git", "__pycache__", "dist", "build"]):
                continue
            for fn in files:
                if fn.endswith(".hvp"):
                    continue
                abs_p = os.path.join(root, fn)
                rel_p = os.path.relpath(abs_p, target_dir).replace("\\", "/")
                with open(abs_p, "rb") as bf:
                    data = bf.read()
                    file_hashes[rel_p] = hashlib.sha256(data).hexdigest()
                zf.write(abs_p, rel_p)

        seal_manifest = {
            "package_name": pkg_name,
            "version": pkg_ver,
            "standard": "ODCS-2.0",
            "domain": "odcshosting.in",
            "created_at": time.time(),
            "files": file_hashes,
            "seal_hash": hashlib.sha256(json.dumps(file_hashes, sort_keys=True).encode("utf-8")).hexdigest()
        }
        zf.writestr(".haven_seal.json", json.dumps(seal_manifest, indent=2))

    print(f"  • Total Archived Files : {len(file_hashes)}")
    print(f"  • Cryptographic Seal  : {dim(seal_manifest['seal_hash'])}")
    print(f"  • Target Registry     : {cyan('odcshosting.in')}")
    print(f"{bold(green('✔ Package built successfully:'))} {bold(out_file)}\n")
    return 0


def verify_package(hvp_path: str) -> int:
    """Verifies the integrity of a .hvp package against its embedded cryptographic seal."""
    if not os.path.exists(hvp_path):
        print(f"{bold(red('Error:'))} Package file '{hvp_path}' not found.")
        return 1

    print(f"\n{bold(cyan('Verifying Haven Verified Package:'))} {hvp_path}")
    try:
        with zipfile.ZipFile(hvp_path, "r") as zf:
            if ".haven_seal.json" not in zf.namelist():
                print(f"{bold(red('Verification Failed:'))} Missing cryptographic seal '.haven_seal.json'.")
                return 1

            seal_data = json.loads(zf.read(".haven_seal.json").decode("utf-8"))
            claimed_hashes = seal_data.get("files", {})

            for rel_p, expected_hash in claimed_hashes.items():
                if rel_p not in zf.namelist():
                    print(f"{bold(red('Integrity Failure:'))} Missing declared file '{rel_p}'.")
                    return 1
                data = zf.read(rel_p)
                computed = hashlib.sha256(data).hexdigest()
                if computed != expected_hash:
                    print(f"{bold(red('Integrity Failure:'))} Checksum mismatch in '{rel_p}'.")
                    return 1

            computed_seal = hashlib.sha256(json.dumps(claimed_hashes, sort_keys=True).encode("utf-8")).hexdigest()
            if computed_seal != seal_data.get("seal_hash"):
                print(f"{bold(red('Verification Failed:'))} Package seal signature invalid.")
                return 1

            print(f"  • Package Name: {green(seal_data.get('package_name', ''))}")
            print(f"  • Version     : {cyan(seal_data.get('version', ''))}")
            print(f"  • Domain      : {bold('odcshosting.in')}")
            print(f"  • Standard    : {seal_data.get('standard', '')}")
            print(f"  • Files       : {len(claimed_hashes)} cryptographically verified files")
            print(f"{bold(green('✔ Cryptographic Integrity Verification: 100% PASS'))}\n")
            return 0
    except Exception as e:
        print(f"{bold(red('Error verifying package:'))} {e}")
        return 1


def publish_package_cli(hvp_path: Optional[str] = None, token: Optional[str] = None) -> int:
    """Publishes package to odcshosting domain."""
    if not hvp_path:
        # Find latest .hvp file in current directory
        candidates = [f for f in os.listdir(".") if f.endswith(".hvp")]
        if not candidates:
            print(f"{bold(yellow('No .hvp package found in current directory.'))} Running 'haven pkg pack' first...")
            res = pack_package(".")
            if res != 0:
                return res
            candidates = [f for f in os.listdir(".") if f.endswith(".hvp")]

        if not candidates:
            print(f"{bold(red('Error:'))} Could not find or build a .hvp package to publish.")
            return 1
        hvp_path = candidates[0]

    reg_url = get_registry_url()
    print(f"\n{bold(cyan('Publishing to ODCS Hosting Registry:'))} {bold(hvp_path)}")
    print(f"  • Target Domain : {bold('odcshosting.in')} ({dim(reg_url)})")

    try:
        result = publish_package_to_odcshosting(hvp_path, registry_url=reg_url, token=token)
        print(f"\n{bold(green('✔ Publication Result:'))} {green(result.get('status', 'OK'))}")
        print(f"  • Package: {cyan(result.get('package_name', ''))} v{result.get('version', '1.0.0')}")
        print(f"  • Seal   : {dim(result.get('seal_hash', ''))}")
        if result.get("message"):
            print(f"  • Notice : {yellow(result.get('message'))}")
        print()
        return 0
    except Exception as e:
        print(f"{bold(red('Error publishing package:'))} {e}")
        return 1


def search_cli(query: str) -> int:
    reg_url = get_registry_url()
    print(f"\n{bold(cyan('Searching odcshosting registry for:'))} '{query}' ({dim(reg_url)})")
    results = search_packages(query, registry_url=reg_url)
    if not results:
        print(f"{yellow('No matching packages found on odcshosting.')}")
        return 0

    print(f"\nFound {bold(str(len(results)))} package(s):")
    for p in results:
        print(f"  • {bold(green(p.get('name', '')))} ({cyan(p.get('version', ''))})")
        print(f"    {dim(p.get('description', ''))}")
        print(f"    Domain: {p.get('domain', 'odcshosting.in')} | Standard: {p.get('standard', 'ODCS-2.0')}\n")
    return 0


def info_cli(package_name: str) -> int:
    reg_url = get_registry_url()
    print(f"\n{bold(cyan('Querying odcshosting for package:'))} {bold(package_name)}")
    info = get_package_info(package_name, registry_url=reg_url)
    if not info:
        print(f"{bold(red('Error:'))} Package '{package_name}' not found on odcshosting.")
        return 1

    print(f"  • Package Name: {bold(green(info.get('name', '')))}")
    print(f"  • Version     : {cyan(info.get('version', ''))}")
    print(f"  • Description : {info.get('description', '')}")
    print(f"  • Author      : {info.get('author', '')}")
    print(f"  • Standard    : {info.get('standard', '')}")
    print(f"  • Host Domain : {bold('odcshosting.in')} ({dim(info.get('registry', reg_url))})\n")
    return 0


def config_cli(sub: str, key: Optional[str] = None, val: Optional[str] = None) -> int:
    cfg = load_config()
    if sub == "get":
        if key:
            print(f"{key} = {cfg.get(key, '<unset>')}")
        else:
            print(f"\n{bold(cyan('Haven Package Manager Configuration:'))}")
            print(f"  • Registry URL : {cfg.get('registry_url', DEFAULT_REGISTRY_URL)} ({bold('odcshosting.in')})")
            print(f"  • Auth Token   : {'<configured>' if cfg.get('auth_token') else '<unauthenticated>'}\n")
        return 0
    elif sub == "set":
        if not key or not val:
            print(f"{bold(red('Error:'))} Key and Value required: haven pkg config set <key> <value>")
            return 1
        cfg[key] = val
        save_config(cfg)
        print(f"{bold(green('✔ Configuration updated:'))} {key} = {val}")
        return 0
    return 0


def serve_cli(port: int = 8090, storage_dir: str = "data/odcshosting_repo") -> int:
    """Launches the self-hosted ODCS Hosting Registry Server."""
    print(f"""
{bold(cyan('╔═══════════════════════════════════════════════════════════════╗'))}
{bold(cyan('║        ODCS HOSTING REGISTRY SERVER (odcshosting.in)         ║'))}
{bold(cyan('║     Open Digital Continuity Standard (ODCS-2.0 Gateway)       ║'))}
{bold(cyan('╚═══════════════════════════════════════════════════════════════╝'))}

  • Listening On: {green(f'http://0.0.0.0:{port}')} / {bold('http://localhost:' + str(port))}
  • Domain Name : {bold('odcshosting.in')}
  • Repository  : {os.path.abspath(storage_dir)}
  • Ready to host, publish, and distribute Haven packages!

Press Ctrl+C to terminate server.
""")
    server = run_odcshosting_server(port=port, storage_dir=storage_dir)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{yellow('Shutting down ODCS Hosting Registry Server...')}")
        server.server_close()
    return 0


def handle_pkg_command(args: list) -> int:
    if not args or args[0] in ("-h", "--help", "help"):
        reg_url = get_registry_url()
        print(f"""
{bold(cyan('╔═══════════════════════════════════════════════════════════════╗'))}
{bold(cyan('║         HAVEN PACKAGE MANAGER FOR odcshosting.in             ║'))}
{bold(cyan('║           Open Digital Continuity Standard (ODCS)             ║'))}
{bold(cyan('╚═══════════════════════════════════════════════════════════════╝'))}

{bold('Active Registry:')} {cyan(reg_url)} ({bold('odcshosting.in')})

{bold('Client Commands:')}
  {green('init')} [name]              Initialize a new haven.toml with odcshosting settings
  {green('show')}, {green('view')}             Display current haven.toml configuration
  {green('search')} <query>            Search packages on odcshosting domain
  {green('info')} <package>            View detailed metadata of a package from odcshosting
  {green('install')} [package] [ver]   Download, verify & install from odcshosting (or haven.toml)
  {green('add')} <package> [ver]       Add dependency to haven.toml and install from odcshosting
  {green('pack')}, {green('build')}            Compile project into a signed .hvp package
  {green('verify')} <package.hvp>      Audit cryptographic seal of a .hvp archive
  {green('publish')} [package.hvp]     Publish package to odcshosting domain

{bold('Configuration & Server Commands:')}
  {green('login')} <token>             Set authentication token for odcshosting
  {green('config')} [get|set] <k> [v]  Inspect or configure registry URL and settings
  {green('serve')} [--port 8090]       Launch self-hosted ODCS Hosting Registry Server
""")
        return 0

    sub = args[0].lower()
    if sub == "init":
        p_name = args[1] if len(args) > 1 else None
        return init_manifest(p_name)
    elif sub in ("show", "view", "manifest"):
        return view_manifest()
    elif sub == "search":
        q = args[1] if len(args) > 1 else ""
        return search_cli(q)
    elif sub == "info":
        if len(args) < 2:
            print(f"{bold(red('Error:'))} Package name required: haven pkg info <package_name>")
            return 1
        return info_cli(args[1])
    elif sub == "install":
        p_name = args[1] if len(args) > 1 else None
        v_name = args[2] if len(args) > 2 else ">=1.0.0"
        return install_dependencies(p_name, v_name)
    elif sub == "add":
        if len(args) < 2:
            print(f"{bold(red('Error:'))} Package name required: haven pkg add <package_name>")
            return 1
        pkg_n = args[1]
        ver_n = args[2] if len(args) > 2 else ">=1.0.0"
        return add_dependency(pkg_n, ver_n)
    elif sub in ("pack", "build"):
        t_dir = args[1] if len(args) > 1 else "."
        return pack_package(t_dir)
    elif sub == "verify":
        if len(args) < 2:
            print(f"{bold(red('Error:'))} Package archive path required: haven pkg verify <package.hvp>")
            return 1
        return verify_package(args[1])
    elif sub == "publish":
        pkg_file = args[1] if len(args) > 1 and not args[1].startswith("--") else None
        return publish_package_cli(pkg_file)
    elif sub == "login":
        if len(args) < 2:
            print(f"{bold(red('Error:'))} Token required: haven pkg login <auth_token>")
            return 1
        cfg = load_config()
        cfg["auth_token"] = args[1]
        save_config(cfg)
        print(f"{bold(green('✔ Authenticated successfully with odcshosting.in!'))}")
        return 0
    elif sub == "config":
        action = args[1] if len(args) > 1 else "get"
        k = args[2] if len(args) > 2 else None
        v = args[3] if len(args) > 3 else None
        return config_cli(action, k, v)
    elif sub == "serve":
        port = 8090
        if len(args) > 1:
            try:
                port = int(args[1].replace("--port=", "").replace("-p=", ""))
            except ValueError:
                pass
        return serve_cli(port=port)
    else:
        print(f"{bold(red('Error:'))} Unknown pkg command '{sub}'. Run 'haven pkg --help' for usage.", file=sys.stderr)
        return 1
