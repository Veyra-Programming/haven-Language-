"""
Updater Script for Haven Website (Heaven Language)
Injects 20 Real Operating System Packages, Exact Hashes, and Auto-Detection
Standard Specification & Architecture by Anirudha Puthraya
"""

import os
import json
import re

MANIFEST_PATH = r"E:\Heaven Language\dist\downloads\downloads_manifest.json"
HTML_PATH = r"E:\ODCS models\heaven\index.html"
JS_PATH = r"E:\ODCS models\heaven\js\heaven.js"

with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
    packages = json.load(f)

print(f"Loaded {len(packages)} OS packages from manifest.")

# Map icon for each platform
ICONS = {
    "win-setup": "📦",
    "win-portable": "🗂️",
    "win-cli": "⚡",
    "win-arm64": "💻",
    "linux-deb-amd64": "🐧",
    "linux-deb-arm64": "🐧",
    "linux-rpm-x86_64": "📦",
    "linux-rpm-arm64": "📦",
    "linux-appimage-x64": "🚀",
    "linux-appimage-arm64": "🚀",
    "linux-arch": "🏹",
    "linux-alpine": "🏔️",
    "linux-tar-x64": "🗜️",
    "linux-tar-arm64": "🍓",
    "macos-silicon": "🍏",
    "macos-intel": "🍏",
    "macos-universal": "🍏",
    "unix-freebsd": "😈",
    "mobile-android": "📱",
    "cloud-wasm": "🌐",
}

BADGE_COLORS = {
    "windows": "background: linear-gradient(135deg, #0284c7, #06b6d4);",
    "linux": "background: linear-gradient(135deg, #e11d48, #be123c);",
    "macos": "background: linear-gradient(135deg, #a855f7, #6366f1);",
    "unix": "background: linear-gradient(135deg, #f59e0b, #d97706);",
    "mobile": "background: linear-gradient(135deg, #10b981, #059669);",
    "wasm": "background: linear-gradient(135deg, #6366f1, #3b82f6);",
}

# Generate 20 Cards HTML
cards_html = []
for pkg in packages:
    pkg_id = pkg["id"]
    icon = ICONS.get(pkg_id, "📦")
    os_cat = pkg["os"]
    badge_style = BADGE_COLORS.get(os_cat, "background: var(--cyan-primary);")
    featured_class = " featured" if pkg.get("featured") else ""
    btn_class = "btn-primary" if pkg.get("featured") else "btn-secondary"
    
    badge_html = f'<div class="dl-badge-featured" style="{badge_style}">{pkg["badge"]}</div>' if pkg.get("badge") else ""

    card = f"""          <!-- {pkg['id']}: {pkg['name']} -->
          <div class="dl-release-card{featured_class}" data-platform="{os_cat}" id="card-{pkg_id}">
            {badge_html}
            <div class="dl-card-head">
              <div class="dl-icon-box">{icon}</div>
              <div>
                <h3 class="dl-title">{pkg['name']}</h3>
                <span class="dl-version-tag">{pkg['file']}</span>
              </div>
            </div>
            <p class="dl-desc">
              {pkg['desc']}
            </p>
            <div class="dl-meta-info">
              <div>Platform: <strong>{pkg['platform']}</strong></div>
              <div>Size: <strong>{pkg['size']}</strong></div>
              <div>Format: <strong>{pkg['format']}</strong></div>
            </div>
            <div class="dl-sha-box">
              <span class="dl-sha-label">SHA-256:</span>
              <code class="dl-sha-val" title="{pkg['sha256']}">{pkg['sha256_short']}</code>
              <button type="button" class="btn-copy-sha" onclick="navigator.clipboard.writeText('{pkg['sha256']}'); this.innerText='✓ Copied!'; setTimeout(()=>this.innerText='Copy Hash', 2000)" style="background:transparent; border:1px solid rgba(255,255,255,0.2); color:var(--text-dim); padding:2px 6px; font-size:0.7rem; border-radius:4px; margin-left:auto; cursor:pointer;">Copy Hash</button>
            </div>
            <a href="downloads/{pkg['file']}" download="{pkg['file']}" class="{btn_class} dl-action-btn" style="{badge_style if pkg.get('featured') else ''}">
              <span>⬇️ Download {pkg['name'].replace('Haven ', '')}</span>
            </a>
          </div>"""
    cards_html.append(card)

generated_cards = "\n\n".join(cards_html)

# Generate Tabs HTML
tabs_html = """        <!-- Operating System Filter Tabs (All 20 Operating Systems) -->
        <div class="os-filter-strip" role="tablist" aria-label="Operating System Filter">
          <button type="button" class="os-tab-btn active" data-os="all">All Operating Systems (20)</button>
          <button type="button" class="os-tab-btn" data-os="windows">🪟 Windows (4)</button>
          <button type="button" class="os-tab-btn" data-os="linux">🐧 Linux (10)</button>
          <button type="button" class="os-tab-btn" data-os="macos">🍏 macOS (3)</button>
          <button type="button" class="os-tab-btn" data-os="unix">⚡ BSD & Unix (1)</button>
          <button type="button" class="os-tab-btn" data-os="mobile">📱 Mobile / Android (1)</button>
          <button type="button" class="os-tab-btn" data-os="wasm">🌐 WebAssembly (1)</button>
        </div>"""

# Read existing HTML
with open(HTML_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace Navigation Link text
html_content = html_content.replace(
    '<span>Downloads (All OS) ??</span>',
    '<span>Downloads (20 OS) ⬇️</span>'
).replace(
    '<span>Downloads (All OS) 📦</span>',
    '<span>Downloads (20 OS) ⬇️</span>'
)

# Update Header Download Button
html_content = re.sub(
    r'<a href="#downloads" class="btn-primary btn-header-dl"[^>]*>[\s\S]*?</a>',
    '<a href="downloads/Haven-1.0.0-win64-Setup.exe" download="Haven-1.0.0-win64-Setup.exe" class="btn-primary btn-header-dl" id="btn-header-download" title="Download Official Haven Windows Installer (.exe)">\n          <span class="dl-icon">⬇️</span>\n          <span class="dl-text">Download .EXE</span>\n        </a>',
    html_content
)

# Update Hero Download Buttons
hero_replacement = """              <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                <a href="downloads/Haven-1.0.0-win64-Setup.exe" download="Haven-1.0.0-win64-Setup.exe" class="btn-primary haven-btn-lg" id="btn-hero-download" title="Download Official Haven Windows Installer">
                  <span class="btn-sparkle">✦</span>
                  <span id="hero-download-text">Download Haven for Windows (v1.0.0)</span>
                </a>
                <a href="#downloads" class="btn-secondary haven-btn-lg" title="Browse all 20 Supported Operating Systems">
                  <span>Browse All 20 OS Releases ⬇️</span>
                </a>
              </div>"""

html_content = re.sub(
    r'<a href="#downloads" class="btn-primary haven-btn-lg">[\s\S]*?</a>',
    hero_replacement,
    html_content
)

# Replace Tabs
html_content = re.sub(
    r'<div class="os-filter-strip"[\s\S]*?</div>\s*<!-- Release Cards Matrix',
    tabs_html + "\n\n        <!-- Release Cards Matrix",
    html_content
)

# Replace Cards Grid
cards_grid_pattern = r'<div class="downloads-cards-grid" id="downloads-cards-grid">[\s\S]*?</div>\s*<!-- Custom Uploaded Releases'
new_grid = f'<div class="downloads-cards-grid" id="downloads-cards-grid">\n{generated_cards}\n        </div>\n\n        <!-- Custom Uploaded Releases'
html_content = re.sub(cards_grid_pattern, new_grid, html_content)

# Update subtitle
html_content = html_content.replace(
    'Official production compilers, runtimes, installers, and containers for <strong>Windows</strong>, <strong>Linux</strong>, <strong>macOS</strong>, and <strong>WebAssembly</strong>.',
    'Official production compilers, verified packages, installers, and containers for <strong>20 Operating Systems & Platforms</strong> including Windows, Linux, macOS, FreeBSD, Android Termux, and WebAssembly.'
)

# Write updated HTML
with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print("[+] Updated HTML at:", HTML_PATH)

# Now update heaven.js to include client OS detection
with open(JS_PATH, "r", encoding="utf-8") as f:
    js_content = f.read()

os_detect_code = """
// Auto-Detect Client Operating System and Personalize Download Buttons
function initClientOsDetection() {
  const ua = navigator.userAgent || '';
  const platform = navigator.platform || '';
  let clientOs = 'windows';
  let clientFile = 'downloads/Haven-1.0.0-win64-Setup.exe';
  let clientText = 'Download Haven for Windows (.exe)';
  let headerText = 'Download .EXE';

  if (/Mac|iPhone|iPod|iPad/i.test(platform) || /Macintosh/i.test(ua)) {
    clientOs = 'macos';
    clientFile = 'downloads/Haven-1.0.0-macOS-Universal.dmg';
    clientText = 'Download Haven for macOS (.dmg)';
    headerText = 'Download .DMG';
  } else if (/Android/i.test(ua)) {
    clientOs = 'mobile';
    clientFile = 'downloads/haven-1.0.0-android-arm64.tar.gz';
    clientText = 'Download Haven for Android (Termux)';
    headerText = 'Download Android';
  } else if (/Linux/i.test(platform) || /Linux/i.test(ua)) {
    clientOs = 'linux';
    clientFile = 'downloads/haven-1.0.0-x86_64.AppImage';
    clientText = 'Download Haven for Linux (.AppImage)';
    headerText = 'Download Linux';
  }

  // Update Hero & Header Download Buttons
  const heroBtn = document.getElementById('btn-hero-download');
  const heroText = document.getElementById('hero-download-text');
  const headerBtn = document.getElementById('btn-header-download');

  if (heroBtn && clientFile) {
    heroBtn.setAttribute('href', clientFile);
    heroBtn.setAttribute('download', clientFile.split('/').pop());
    if (heroText) heroText.textContent = clientText;
  }
  if (headerBtn && clientFile) {
    headerBtn.setAttribute('href', clientFile);
    headerBtn.setAttribute('download', clientFile.split('/').pop());
    const textSpan = headerBtn.querySelector('.dl-text');
    if (textSpan) textSpan.textContent = headerText;
  }

  // Highlight Detected OS Tab and card if on downloads view
  console.log('[Haven OS Detector] Client Operating System identified as:', clientOs);
}
"""

# Update presets in heaven.js if needed
if "mesh: {" not in js_content:
    mesh_presets = '''  mesh: {
    name: "L2 Gossip Mesh & CRDTs",
    code: `// ODCS Layer 2: P2P Gossip Mesh & Conflict-Free Replication
from odcs.mesh import GossipMesh

set mesh to GossipMesh()
set ambulance_edge to mesh.create_node("Edge-Ambulance")
set cloud_hub to mesh.create_node("Cloud-Hub")

print "Simulating mountain tunnel radio disconnect..."
mesh.isolate("Edge-Ambulance")

// Disconnected mutations in tunnel
ambulance_edge.mutate_counter("PlasmaUnits", -15)
ambulance_edge.mutate_set_add("FieldSupplies", "SplintKit")

// Central cloud mutations
cloud_hub.mutate_counter("PlasmaUnits", 50)
cloud_hub.mutate_set_add("FieldSupplies", "OxygenTank")

print "Ambulance exits tunnel -> Restoring link & triggering gossip..."
mesh.heal_all()
mesh.sync_until_stable()
mesh.assert_converged()

print "Strong Eventual Consistency (SEC) Proven: 100% Convergence!"
print "Converged Plasma Units: " + String(ambulance_edge.get_counter("PlasmaUnits").value)
print "Zero Intent Loss across all partitions verified."`
  },

  adaptation: {
    name: "L3 & L4: Adaptation & Intent UX",
    code: `// ODCS Layer 3 & 4: Environmental Adaptation & Zero Intent Loss
from odcs import EnvironmentalTelemetry, ContinuityMode, adaptive_policy, ZeroIntentLossManager

set tele to EnvironmentalTelemetry()
set intent_mgr to ZeroIntentLossManager()

// Layer 4: Preserve user intent with instant durable receipt
set receipt to intent_mgr.preserve_intent("Dr. Vance", "ICU_EmergencyOrder", {"med": "Epinephrine", "dose": "1mg"})
print "Layer 4 Zero Intent Loss Receipt: " + receipt.intent_id + " [STATUS: SEALED]"

// Layer 3: Dynamic Adaptive Policy Execution
function airgap_offline_handler():
    print "L3 Policy: Operating in Airgap Offline Mode via Local WAL"
    return "SAVED_TO_LOCAL_JOURNAL"

@adaptive_policy(on_airgap=airgap_offline_handler)
function submit_order():
    return "SENT_TO_BROADBAND_CLOUD"

EnvironmentalTelemetry.set_override(ContinuityMode.AIRGAP_OFFLINE)
set result to submit_order()
print "Execution Result: " + result`
  }
};'''
    js_content = re.sub(r'\}\s*;\s*\n\s*function initPlayground', mesh_presets + '\n\nfunction initPlayground', js_content, count=1)
    with open(JS_PATH, "w", encoding="utf-8") as f:
        f.write(js_content)
    print("[+] Injected L2 Mesh and L3/L4 Adaptation Presets into heaven.js")

if "initClientOsDetection" not in js_content:
    # Append to heaven.js and invoke in DOMContentLoaded
    js_content += os_detect_code
    js_content = js_content.replace(
        "initOsFilterTabs();",
        "initOsFilterTabs();\n  initClientOsDetection();"
    )
    with open(JS_PATH, "w", encoding="utf-8") as f:
        f.write(js_content)
    print("[+] Updated JS with OS Auto-Detection at:", JS_PATH)

# Ensure legal link in heaven/index.html footer
heaven_html_path = r"E:\ODCS models\heaven\index.html"
with open(heaven_html_path, "r", encoding="utf-8") as f:
    h_html = f.read()
if "legal.html" not in h_html:
    target_link = '<li><a href="../admin/" class="footer-link">Administrator Portal</a></li>'
    new_link = '<li><a href="../legal.html" class="footer-link">Legal &amp; Policy Hub</a></li>\n            <li><a href="../admin/" class="footer-link">Administrator Portal</a></li>'
    h_html = h_html.replace(target_link, new_link, 1)
    with open(heaven_html_path, "w", encoding="utf-8") as f:
        f.write(h_html)
    print("[+] Updated heaven/index.html footer with Legal & Policy Hub link.")

print("Website update successfully finalized!")

