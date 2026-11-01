"""
Deployer & Builder for Haven Admin Articles & Interactive Reader System
Standard Specification & Architecture by Anirudha Puthraya
"""

import os
import json
import re

SOURCE_ROOT = r"E:\Heaven Language"
HEAVEN_DIR = r"E:\ODCS models\heaven"
ADMIN_DIR = r"E:\ODCS models\admin"

from haven.cli.articles import ADMIN_ARTICLES

print(f"Loaded {len(ADMIN_ARTICLES)} Admin Architectural Essays from haven.cli.articles.")

# 1. Generate E:\ODCS models\heaven\js\admin_articles_data.js
articles_js_content = "/**\n * HAVEN LANGUAGE & ODCS: ADMIN ARTICLES & ESSAYS REPOSITORY\n * Standard Specification & Architecture by Anirudha Puthraya\n */\n\n"
articles_js_content += "const DEFAULT_ADMIN_ARTICLES = " + json.dumps(ADMIN_ARTICLES, indent=2) + ";\n\n"
articles_js_content += """function getAdminArticles() {
  try {
    const custom = localStorage.getItem('odcs_haven_admin_articles');
    if (custom) {
      const parsed = JSON.parse(custom);
      if (Array.isArray(parsed) && parsed.length > 0) {
        // Merge with defaults if needed
        const ids = new Set(parsed.map(a => a.id));
        const merged = [...parsed];
        for (const def of DEFAULT_ADMIN_ARTICLES) {
          if (!ids.has(def.id)) {
            merged.push(def);
          }
        }
        return merged;
      }
    }
  } catch (e) {
    console.warn('Error reading custom articles:', e);
  }
  return DEFAULT_ADMIN_ARTICLES;
}
"""

js_data_path = os.path.join(HEAVEN_DIR, "js", "admin_articles_data.js")
with open(js_data_path, "w", encoding="utf-8") as f:
    f.write(articles_js_content)
print("[+] Created:", js_data_path)

# Also copy to Admin directory for Admin dashboard
admin_js_data_path = os.path.join(ADMIN_DIR, "js", "admin_articles_data.js")
with open(admin_js_data_path, "w", encoding="utf-8") as f:
    f.write(articles_js_content)
print("[+] Created:", admin_js_data_path)

# 2. Append CSS Styles to heaven.css
css_path = os.path.join(HEAVEN_DIR, "css", "heaven.css")
with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

articles_css = """
/* ==========================================================================
   ADMIN ARTICLES & ARCHITECTURAL ESSAYS SYSTEM (By Anirudha Puthraya)
   ========================================================================== */

.articles-controls-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem 1.5rem;
  background: var(--haven-bg-card);
  border: 1px solid rgba(0, 240, 255, 0.15);
  border-radius: 12px;
}

.article-cat-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.article-cat-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-dim);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.article-cat-btn:hover {
  background: rgba(0, 240, 255, 0.1);
  color: var(--cyan-primary);
  border-color: rgba(0, 240, 255, 0.3);
}

.article-cat-btn.active {
  background: linear-gradient(135deg, rgba(0, 240, 255, 0.2), rgba(168, 85, 247, 0.2));
  color: var(--cyan-primary);
  border-color: var(--cyan-primary);
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.25);
}

.article-search-wrapper {
  position: relative;
  min-width: 260px;
}

.article-search-input {
  width: 100%;
  background: rgba(10, 15, 30, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 0.6rem 1rem 0.6rem 2.2rem;
  border-radius: 8px;
  font-size: 0.88rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.article-search-input:focus {
  border-color: var(--cyan-primary);
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.25);
}

.article-search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-dim);
  pointer-events: none;
}

.articles-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.75rem;
}

.article-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--haven-bg-card);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 1.75rem;
  overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s, box-shadow 0.3s;
}

.article-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #a855f7, #00f0ff);
  opacity: 0.7;
}

.article-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 240, 255, 0.35);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 240, 255, 0.15);
}

.article-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.85rem;
}

.article-category-badge {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  background: rgba(168, 85, 247, 0.15);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.article-read-time {
  font-size: 0.78rem;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.article-title-link {
  color: #fff;
  text-decoration: none;
}

.article-card-title {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.35;
  color: #fff;
  margin-bottom: 0.65rem;
  transition: color 0.2s;
}

.article-card:hover .article-card-title {
  color: var(--cyan-primary);
}

.article-card-subtitle {
  font-size: 0.9rem;
  color: var(--text-dim);
  line-height: 1.5;
  margin-bottom: 1.25rem;
  flex: 1;
}

.article-tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1.25rem;
}

.article-tag-pill {
  font-size: 0.72rem;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.04);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.article-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: auto;
}

.article-author-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.author-avatar-img {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1.5px solid var(--cyan-primary);
  background: #111;
  object-fit: cover;
}

.author-name-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: #f1f5f9;
}

.author-role-text {
  font-size: 0.72rem;
  color: var(--text-dim);
}

.article-action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-read-article {
  background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(168, 85, 247, 0.15));
  border: 1px solid rgba(0, 240, 255, 0.4);
  color: var(--cyan-primary);
  padding: 0.45rem 0.85rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.btn-read-article:hover {
  background: var(--cyan-primary);
  color: #060814;
  box-shadow: 0 0 12px rgba(0, 240, 255, 0.4);
}

.btn-listen-article {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #e2e8f0;
  padding: 0.45rem 0.75rem;
  border-radius: 6px;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-listen-article:hover {
  background: rgba(168, 85, 247, 0.2);
  border-color: #a855f7;
  color: #d8b4fe;
}

/* ==========================================================================
   ARTICLE READER MODAL
   ========================================================================== */

.article-reader-modal {
  position: fixed;
  inset: 0;
  z-index: 99999;
  background: rgba(6, 8, 20, 0.85);
  backdrop-filter: blur(16px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow-y: auto;
  padding: 2rem 1rem;
}

.reader-progress-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  z-index: 100000;
}

.reader-progress-bar {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, #a855f7, #00f0ff, #10b981);
  transition: width 0.1s;
}

.reader-container {
  position: relative;
  width: 100%;
  max-width: 860px;
  background: #0d1224;
  border: 1px solid rgba(0, 240, 255, 0.25);
  border-radius: 16px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.75);
  overflow: hidden;
  margin-top: 1rem;
  margin-bottom: 3rem;
  transition: background-color 0.3s, color 0.3s;
}

/* Themes */
.reader-container.theme-dark {
  background: #0d1224;
  color: #f1f5f9;
}

.reader-container.theme-sepia {
  background: #231d16;
  color: #f4ecd8;
}

.reader-container.theme-sepia .reader-content-body {
  color: #ded1b8;
}

.reader-container.theme-midnight {
  background: #05070f;
  color: #e2e8f0;
}

.reader-top-toolbar {
  position: sticky;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1.5rem;
  background: rgba(13, 18, 36, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 10;
}

.reader-theme-sepia .reader-top-toolbar {
  background: rgba(35, 29, 22, 0.95);
}

.reader-toolbar-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.audio-player-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(168, 85, 247, 0.15);
  border: 1px solid rgba(168, 85, 247, 0.4);
  color: #c084fc;
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.audio-player-pill:hover {
  background: rgba(168, 85, 247, 0.3);
  color: #fff;
}

.audio-wave-anim {
  display: inline-flex;
  gap: 2px;
  height: 12px;
  align-items: flex-end;
}

.audio-wave-anim span {
  width: 2px;
  background: #c084fc;
  border-radius: 1px;
  animation: audioWave 1s infinite ease-in-out;
}

.audio-wave-anim span:nth-child(2) { animation-delay: 0.2s; }
.audio-wave-anim span:nth-child(3) { animation-delay: 0.4s; }

@keyframes audioWave {
  0%, 100% { height: 4px; }
  50% { height: 12px; }
}

.reader-toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.btn-reader-ctrl {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: var(--text-dim);
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-reader-ctrl:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.btn-close-reader {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-close-reader:hover {
  background: #ef4444;
  color: #fff;
}

.reader-header-area {
  padding: 2.5rem 2.5rem 1.5rem 2.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.reader-category-pill {
  display: inline-block;
  background: rgba(0, 240, 255, 0.15);
  color: var(--cyan-primary);
  border: 1px solid rgba(0, 240, 255, 0.3);
  padding: 0.3rem 0.85rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.reader-article-title {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.25;
  color: #fff;
  margin-bottom: 1rem;
}

.reader-article-subtitle {
  font-size: 1.15rem;
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.reader-meta-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.reader-author-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.reader-author-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid var(--cyan-primary);
  background: #111;
  object-fit: cover;
}

.reader-author-name {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
}

.reader-author-title {
  font-size: 0.8rem;
  color: var(--text-dim);
}

.reader-content-body {
  padding: 2.5rem;
  font-size: 1.08rem;
  line-height: 1.8;
  color: #e2e8f0;
}

.reader-content-body h1 {
  font-size: 1.85rem;
  font-weight: 800;
  color: #fff;
  margin: 2rem 0 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.5rem;
}

.reader-content-body h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--cyan-primary);
  margin: 2rem 0 0.85rem 0;
}

.reader-content-body h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #c084fc;
  margin: 1.5rem 0 0.75rem 0;
}

.reader-content-body p {
  margin-bottom: 1.4rem;
}

.reader-content-body blockquote {
  border-left: 4px solid var(--cyan-primary);
  background: rgba(0, 240, 255, 0.06);
  padding: 1.2rem 1.5rem;
  border-radius: 0 8px 8px 0;
  margin: 1.5rem 0;
  font-style: italic;
  color: #e0f2fe;
}

.reader-content-body pre {
  position: relative;
  background: #060914;
  border: 1px solid rgba(0, 240, 255, 0.25);
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  margin: 1.5rem 0;
  overflow-x: auto;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
}

.reader-content-body code {
  font-family: 'JetBrains Mono', monospace;
  background: rgba(255, 255, 255, 0.08);
  color: #38bdf8;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.9em;
}

.reader-content-body pre code {
  background: transparent;
  padding: 0;
  color: #f8fafc;
}

.reader-content-body ul, .reader-content-body ol {
  margin: 1rem 0 1.5rem 1.5rem;
}

.reader-content-body li {
  margin-bottom: 0.5rem;
}

.reader-footer-author-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: rgba(0, 240, 255, 0.05);
  border: 1px solid rgba(0, 240, 255, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 3rem 2.5rem 2.5rem 2.5rem;
}

.reader-footer-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 2px solid var(--cyan-primary);
}

.reader-author-bio-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.35rem;
}

.reader-author-bio-desc {
  font-size: 0.88rem;
  color: var(--text-dim);
  line-height: 1.5;
}

@media (max-width: 768px) {
  .articles-cards-grid {
    grid-template-columns: 1fr;
  }
  .reader-header-area, .reader-content-body {
    padding: 1.5rem;
  }
  .reader-article-title {
    font-size: 1.75rem;
  }
}
"""

if "ADMIN ARTICLES & ARCHITECTURAL ESSAYS SYSTEM" not in css_content:
    css_content += articles_css
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_content)
    print("[+] Appended article styles to:", css_path)
else:
    print("[*] Article styles already in CSS.")

print("Step 1 & 2 completed.")
