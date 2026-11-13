"""
Haven Backend Framework - OpenAPI 3.0 Documentation & Interactive API Explorer
Open Digital Continuity Standard (ODCS) & Open Financial Continuity Standard (OFCS)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import json
from typing import Any, Dict, List
from .response import Response
from .router import Router


def build_openapi_spec(app_name: str, router: Router, version: str = "1.0.0") -> Dict[str, Any]:
    """Generates an OpenAPI 3.0.3 specification from registered Haven routes."""
    paths: Dict[str, Dict[str, Any]] = {}

    for entry in router.routes:
        path = entry.path_pattern
        method = entry.method.lower()
        if method == "*":
            continue

        if path not in paths:
            paths[path] = {}

        # Extract path parameters
        import re
        param_names = re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', path)
        parameters = [
            {
                "name": p,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": f"URL path parameter '{p}'"
            }
            for p in param_names
        ]

        docstring = getattr(entry.handler, "__doc__", "") or f"Handler for {entry.method} {path}"
        summary = docstring.strip().split("\n")[0] if docstring else f"{entry.method} {path}"

        tags = ["ODCS Continuity"] if path.startswith("/odcs") else (
            ["OFCS Financial"] if path.startswith("/ofcs") or path.startswith("/vault") else ["Application"]
        )

        operation: Dict[str, Any] = {
            "summary": summary,
            "description": docstring.strip(),
            "tags": tags,
            "responses": {
                "200": {
                    "description": "Successful operation",
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                }
            }
        }

        if parameters:
            operation["parameters"] = parameters

        if method in ("post", "put", "patch"):
            operation["requestBody"] = {
                "required": False,
                "content": {
                    "application/json": {
                        "schema": {"type": "object"}
                    }
                }
            }

        paths[path][method] = operation

    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": f"🦊 {app_name} API",
            "version": version,
            "description": (
                f"Interactive API Documentation for **{app_name}**.\n\n"
                "Built on the **Haven Programming Language** with native **Open Digital Continuity Standard (ODCS)** "
                "and **Open Financial Continuity Standard (OFCS)** invariants.\n\n"
                "Architect: **Anirudha Puthraya**."
            )
        },
        "paths": paths
    }
    return spec


def generate_interactive_docs_html(app_name: str, spec_url: str = "/openapi.json") -> str:
    """Generates an embedded Dark-Mode Interactive API Explorer with Haven Fox branding."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦊 {app_name} • Haven Interactive API Explorer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0a0e17;
            --card-bg: #111827;
            --border-color: #1f2937;
            --accent-cyan: #00f2fe;
            --accent-amber: #f59e0b;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --badge-get: #10b981;
            --badge-post: #3b82f6;
            --badge-put: #f59e0b;
            --badge-del: #ef4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Inter', -apple-system, sans-serif;
            padding: 2rem 1.5rem;
            line-height: 1.6;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
        }}
        .brand {{ display: flex; align-items: center; gap: 1rem; }}
        .fox-icon {{ font-size: 2.5rem; }}
        h1 {{ font-size: 1.8rem; font-weight: 700; color: #fff; }}
        .subtitle {{ color: var(--text-muted); font-size: 0.95rem; }}
        .badge-odcs {{
            background: linear-gradient(135deg, rgba(0, 242, 254, 0.15), rgba(79, 172, 254, 0.15));
            border: 1px solid var(--accent-cyan);
            color: var(--accent-cyan);
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .section-title {{
            font-size: 1.2rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            color: var(--accent-cyan);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .endpoint-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            margin-bottom: 1rem;
            overflow: hidden;
            transition: all 0.2s ease;
        }}
        .endpoint-card:hover {{ border-color: rgba(0, 242, 254, 0.4); }}
        .endpoint-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 1.25rem;
            cursor: pointer;
            user-select: none;
        }}
        .endpoint-left {{ display: flex; align-items: center; gap: 1rem; }}
        .method-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 0.8rem;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            text-transform: uppercase;
        }}
        .method-get {{ background: rgba(16, 185, 129, 0.2); color: var(--badge-get); border: 1px solid var(--badge-get); }}
        .method-post {{ background: rgba(59, 130, 246, 0.2); color: var(--badge-post); border: 1px solid var(--badge-post); }}
        .method-put {{ background: rgba(245, 158, 11, 0.2); color: var(--badge-put); border: 1px solid var(--badge-put); }}
        .method-delete {{ background: rgba(239, 68, 68, 0.2); color: var(--badge-del); border: 1px solid var(--badge-del); }}
        .path {{ font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #fff; }}
        .summary {{ color: var(--text-muted); font-size: 0.9rem; }}
        .endpoint-body {{
            display: none;
            padding: 1.25rem;
            background: #0d131f;
            border-top: 1px solid var(--border-color);
        }}
        .try-btn {{
            background: var(--accent-cyan);
            color: #000;
            border: none;
            font-weight: 600;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            margin-top: 0.75rem;
            transition: opacity 0.2s;
        }}
        .try-btn:hover {{ opacity: 0.85; }}
        .response-box {{
            margin-top: 1rem;
            background: #000;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #10b981;
            overflow-x: auto;
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <div class="fox-icon">🦊</div>
                <div>
                    <h1>{app_name}</h1>
                    <div class="subtitle">Haven Microservices Backend • ODCS & OFCS Protected</div>
                </div>
            </div>
            <div class="badge-odcs">ODCS Native 1.0.0</div>
        </header>

        <div id="endpoints-container">
            <div style="color: var(--text-muted); text-align: center; padding: 2rem;">Loading API Specification...</div>
        </div>
    </div>

    <script>
        fetch('{spec_url}')
            .then(r => r.json())
            .then(spec => {{
                const container = document.getElementById('endpoints-container');
                container.innerHTML = '';
                
                const tags = {{}};
                for (const [path, methods] of Object.entries(spec.paths)) {{
                    for (const [method, op] of Object.entries(methods)) {{
                        const tag = (op.tags && op.tags[0]) || 'General';
                        if (!tags[tag]) tags[tag] = [];
                        tags[tag].push({{ path, method, op }});
                    }}
                }}

                for (const [tag, items] of Object.entries(tags)) {{
                    const title = document.createElement('div');
                    title.className = 'section-title';
                    title.textContent = '⚡ ' + tag;
                    container.appendChild(title);

                    items.forEach(({{ path, method, op }}) => {{
                        const card = document.createElement('div');
                        card.className = 'endpoint-card';
                        
                        const mUpper = method.toUpperCase();
                        card.innerHTML = `
                            <div class="endpoint-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'">
                                <div class="endpoint-left">
                                    <span class="method-badge method-${{method}}">${{mUpper}}</span>
                                    <span class="path">${{path}}</span>
                                </div>
                                <div class="summary">${{op.summary || ''}}</div>
                            </div>
                            <div class="endpoint-body">
                                <p style="color: var(--text-muted); margin-bottom: 0.75rem;">${{op.description || 'No additional description.'}}</p>
                                <button class="try-btn" onclick="executeTestRequest(this, '${{method}}', '${{path}}')">Execute Request</button>
                                <pre class="response-box"></pre>
                            </div>
                        `;
                        container.appendChild(card);
                    }});
                }}
            }})
            .catch(err => {{
                document.getElementById('endpoints-container').innerHTML = '<p style="color:#ef4444;">Failed to load API spec.</p>';
            }});

        async function executeTestRequest(btn, method, path) {{
            const resBox = btn.nextElementSibling;
            resBox.style.display = 'block';
            resBox.textContent = 'Sending request...';
            try {{
                const res = await fetch(path, {{ method: method.toUpperCase() }});
                const data = await res.json().catch(() => res.text());
                resBox.textContent = JSON.stringify(data, null, 2);
            }} catch (e) {{
                resBox.textContent = 'Error: ' + e.message;
            }}
        }}
    </script>
</body>
</html>"""
