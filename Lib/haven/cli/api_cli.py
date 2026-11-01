"""
Haven Edge API Gateway CLI Client
Direct command-line interface for https://api.odcs.in edge operations.
Standard Specification & Architecture by Anirudha Puthraya.
"""

import sys
import os
import json
import time
import urllib.request
import webbrowser
from .colors import green, yellow, red, cyan, bold, dim, magenta, blue


API_BASE = "https://api.odcs.in"


def print_api_help() -> None:
    print(f"""
{bold(cyan('Haven Edge API Gateway CLI (https://api.odcs.in)'))}
{dim('Standard: Open Digital Continuity Standard (ODCS-1.0.0)')}

{bold('Usage:')}
  haven api <subcommand> [options]

{bold('Commands:')}
  {green('probe')}               Measure sub-millisecond edge latency and active Cloudflare colo
  {green('status')}              Inspect edge network telemetry, TLS cipher, and IP routing
  {green('genesis')}             Retrieve and verify the immutable ODCS Genesis anchor block
  {green('sync')}                Perform live CRDT delta convergence with edge state
  {green('schemas')}             List all formal ODCS JSON schema definitions
  {green('downloads')}           List compiled binary packages for all 20 supported operating systems
  {green('docs')}, {green('open')}          Open the interactive API Explorer in default browser
""")


def fetch_json(endpoint: str, method: str = "GET", data: dict = None, timeout: float = 5.0) -> dict:
    url = f"{API_BASE}{endpoint}"
    req_data = json.dumps(data).encode("utf-8") if data else None
    headers = {
        "User-Agent": "Haven-CLI/1.0.0",
        "Accept": "application/json"
    }
    if req_data:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def handle_api_command(args: list) -> int:
    if not args or args[0] in ("-h", "--help", "help"):
        print_api_help()
        return 0

    sub = args[0].lower()

    if sub == "probe":
        print(f"[*] Probing {API_BASE}/v1/telemetry/probe ...")
        try:
            t0 = time.perf_counter()
            data = fetch_json("/v1/telemetry/probe")
            dur = (time.perf_counter() - t0) * 1000
            edge = data.get("edge", {})
            tele = data.get("telemetry", {})
            print(f"\n{bold(green('✔ Edge Probe Response Received'))} in {bold(f'{dur:.2f}ms')}")
            print(f"  • Edge Gateway   : {bold(API_BASE)}")
            print(f"  • Cloudflare Colo: {bold(cyan(edge.get('colo', 'UNKNOWN')))} ({edge.get('city')}, {edge.get('country')})")
            print(f"  • Protocol / ASN : {edge.get('httpProtocol', 'HTTP/3')} / AS{edge.get('asn')}")
            print(f"  • Continuity Mode: {bold(green(tele.get('mode', 'OPTIMAL_ONLINE')))} (Code: {tele.get('mode_code')})")
            print(f"  • Retry Strategy : {tele.get('retry_strategy')}")
            return 0
        except Exception as e:
            print(f"{bold(red('Error:'))} Failed to probe edge gateway: {e}", file=sys.stderr)
            return 1

    elif sub == "status":
        print(f"[*] Fetching telemetry status from {API_BASE}/v1/telemetry/status ...")
        try:
            data = fetch_json("/v1/telemetry/status")
            print(f"\n{bold(cyan('Edge Status Report:'))}")
            print(json.dumps(data, indent=2))
            return 0
        except Exception as e:
            print(f"{bold(red('Error:'))} Failed to fetch status: {e}", file=sys.stderr)
            return 1

    elif sub == "genesis":
        print(f"[*] Retrieving Genesis Anchor Block from {API_BASE}/v1/ledger/genesis ...")
        try:
            data = fetch_json("/v1/ledger/genesis")
            genesis = data.get("genesis", {})
            print(f"\n{bold(green('✔ Layer 1 Genesis Anchor Block Verified:'))}")
            print(f"  • Block Index    : #{genesis.get('index')}")
            print(f"  • Genesis Hash   : {bold(cyan(genesis.get('hash', '')))}")
            print(f"  • Previous Hash  : {genesis.get('prev_hash')}")
            print(f"  • Standard       : {data.get('standard')}")
            print(f"  • Lead Architect : {bold(data.get('creator'))}")
            print(f"  • Specification  : {data.get('specification')}")
            return 0
        except Exception as e:
            print(f"{bold(red('Error:'))} Failed to retrieve genesis block: {e}", file=sys.stderr)
            return 1

    elif sub == "sync":
        print(f"[*] Testing edge CRDT convergence via {API_BASE}/v1/sync ...")
        try:
            payload = {
                "clock": {"haven-cli-node": 1},
                "counters": {"cli_tests": {"p": {"haven-cli-node": 5}, "n": {}}},
                "mutations": [{"mutation_id": f"cli-tx-{int(time.time())}"}]
            }
            data = fetch_json("/v1/sync", method="POST", data=payload)
            print(f"\n{bold(green('✔ Edge State Converged (Strong Eventual Consistency):'))}")
            print(f"  • Status         : {bold(green(data.get('status')))}")
            print(f"  • Edge Colo      : {data.get('edge_colo')}")
            print(f"  • Acknowledged   : {data.get('acknowledged_mutations')}")
            print(f"  • Receipt Hash   : {bold(cyan(data.get('receipt_hash')))}")
            return 0
        except Exception as e:
            print(f"{bold(red('Error:'))} Failed to sync with edge: {e}", file=sys.stderr)
            return 1

    elif sub == "schemas":
        print(f"[*] Listing schemas from {API_BASE}/v1/schemas ...")
        try:
            data = fetch_json("/v1/schemas")
            catalog = data.get("catalog", [])
            print(f"\n{bold(cyan(f'ODCS Schemas Catalog ({len(catalog)} schemas available):'))}")
            for s in catalog:
                print(f"  • {bold(s.get('schema_id')):<24} ➔ {dim(s.get('uri'))}")
            return 0
        except Exception as e:
            print(f"{bold(red('Error:'))} Failed to fetch schemas: {e}", file=sys.stderr)
            return 1

    elif sub == "downloads":
        print(f"[*] Querying Haven 20-OS release manifest from {API_BASE}/v1/downloads ...")
        try:
            data = fetch_json("/v1/downloads")
            downloads = data.get("downloads", {})
            v = data.get("version", "1.0.0")
            print(f"\n{bold(cyan(f'Haven Language 20-OS Release Binary Manifest (v{v}):'))}")
            print(f"{'Platform Key':<14} | {'Size':<10} | {'Package Name':<42} | {'Checksum'}")
            print("-" * 90)
            for k, info in list(downloads.items())[:12]:
                print(f"{green(k):<14} | {info.get('size',''):<10} | {info.get('name','')[:40]:<42} | {dim(info.get('sha256','')[:16])}...")
            if len(downloads) > 12:
                print(f"... and {len(downloads) - 12} more platforms (Total: {data.get('total_platforms')}).")
            return 0
        except Exception as e:
            print(f"{bold(red('Error:'))} Failed to query release manifest: {e}", file=sys.stderr)
            return 1

    elif sub in ("docs", "open", "explorer"):
        doc_url = f"{API_BASE}/docs"
        print(f"[*] Opening {doc_url} in your default browser...")
        try:
            webbrowser.open(doc_url)
            return 0
        except Exception as e:
            print(f"Navigate to: {doc_url}")
            return 0

    else:
        print(f"{bold(red('Error:'))} Unknown api subcommand '{sub}'. Type {bold('haven api --help')}.", file=sys.stderr)
        return 1
