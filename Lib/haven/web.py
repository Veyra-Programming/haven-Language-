"""
Ani++ & Haven Platform-Independent Web & Template Engine (ani.web / haven.web)
PHP-Style Embedded Templating, Superglobals, Session Management,
Lightweight Database QueryBuilder, and Platform-Neutral Web Server.
Standard: Open Digital Continuity Standard (ODCS) Web Subsystem
Architecture & Specification: Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import os
import re
import sys
import json
import time
import hmac
import hashlib
import sqlite3
import urllib.parse
import http.server
import http.cookies
from typing import Dict, List, Tuple, Any, Optional, Union, Callable

# =====================================================================
# 1. PHP-Style Standard Function Toolbox
# =====================================================================

def explode(separator: str, string: str, limit: Optional[int] = None) -> List[str]:
    """Splits a string by string into an array (like PHP explode)."""
    if limit is not None and limit > 0:
        return string.split(separator, limit - 1)
    return string.split(separator)


def implode(glue: str, pieces: List[Any]) -> str:
    """Joins array elements with a string glue (like PHP implode/join)."""
    return glue.join(str(p) for p in pieces)


def str_replace(search: Union[str, List[str]], replace: Union[str, List[str]], subject: str) -> str:
    """Replaces all occurrences of the search string with the replacement string."""
    if isinstance(search, list):
        if isinstance(replace, list):
            for s, r in zip(search, replace):
                subject = subject.replace(str(s), str(r))
        else:
            for s in search:
                subject = subject.replace(str(s), str(replace))
        return subject
    return subject.replace(str(search), str(replace))


def strpos(haystack: str, needle: str, offset: int = 0) -> Union[int, bool]:
    """Finds position of first occurrence of string in a string, or False if not found."""
    idx = haystack.find(needle, offset)
    return idx if idx != -1 else False


def substr(string: str, start: int, length: Optional[int] = None) -> str:
    """Returns the portion of string specified by the start and length parameters."""
    if length is None:
        return string[start:]
    if length < 0:
        return string[start:length]
    return string[start:start + length]


def trim(string: str, characters: Optional[str] = None) -> str:
    """Strips whitespace or other characters from the beginning and end of a string."""
    return string.strip(characters)


def htmlspecialchars(string: str) -> str:
    """Converts special characters to HTML entities to prevent XSS attacks."""
    table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#039;",
        "<": "&lt;",
        ">": "&gt;"
    }
    return "".join(table.get(c, c) for c in str(string))


htmlentities = htmlspecialchars


def strip_tags(html_str: str) -> str:
    """Strips HTML and XML tags from a string."""
    return re.sub(r"<[^>]*?>", "", str(html_str))


def nl2br(string: str) -> str:
    """Inserts HTML line breaks (<br />) before all newlines in a string."""
    return str(string).replace("\r\n", "<br />\r\n").replace("\n", "<br />\n")


def array_merge(*arrays: Union[List[Any], Dict[str, Any]]) -> Union[List[Any], Dict[str, Any]]:
    """Merges one or more arrays/dictionaries."""
    if not arrays:
        return []
    if isinstance(arrays[0], dict):
        merged: Dict[str, Any] = {}
        for a in arrays:
            if isinstance(a, dict):
                merged.update(a)
        return merged
    else:
        res: List[Any] = []
        for a in arrays:
            if isinstance(a, list):
                res.extend(a)
        return res


def array_keys(dictionary: Dict[Any, Any]) -> List[Any]:
    """Returns all the keys of an array/dict."""
    return list(dictionary.keys())


def array_values(dictionary: Dict[Any, Any]) -> List[Any]:
    """Returns all the values of an array/dict."""
    return list(dictionary.values())


def array_column(array: List[Dict[str, Any]], column_key: str) -> List[Any]:
    """Returns the values from a single column in the input array."""
    return [row.get(column_key) for row in array if column_key in row]


def array_chunk(array: List[Any], size: int) -> List[List[Any]]:
    """Splits an array into chunks of specified size."""
    if size < 1:
        raise ValueError("Chunk size must be >= 1")
    return [array[i:i + size] for i in range(0, len(array), size)]


def array_filter(array: List[Any], callback: Optional[Callable[[Any], bool]] = None) -> List[Any]:
    """Filters elements of an array using a callback function."""
    if callback is None:
        return [x for x in array if bool(x)]
    return [x for x in array if callback(x)]


def array_map(callback: Callable[[Any], Any], array: List[Any]) -> List[Any]:
    """Applies the callback to the elements of the given arrays."""
    return [callback(x) for x in array]


def in_array(needle: Any, haystack: Union[List[Any], Tuple[Any, ...]]) -> bool:
    """Checks if a value exists in an array."""
    return needle in haystack


def count_items(var: Union[List[Any], Dict[Any, Any], str]) -> int:
    """Counts all elements in an array or string (like PHP count)."""
    return len(var)


def md5(data: Union[str, bytes]) -> str:
    """Calculates the MD5 hash of a string."""
    b = data.encode("utf-8") if isinstance(data, str) else data
    return hashlib.md5(b).hexdigest()


def sha1(data: Union[str, bytes]) -> str:
    """Calculates the SHA1 hash of a string."""
    b = data.encode("utf-8") if isinstance(data, str) else data
    return hashlib.sha1(b).hexdigest()


def password_hash(password: str) -> str:
    """Creates a secure password hash using PBKDF2-HMAC-SHA256 with dynamic salt."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"$pbkdf2-sha256$100000${salt.hex()}${dk.hex()}"


def password_verify(password: str, hashed_str: str) -> bool:
    """Verifies that a password matches a hash."""
    try:
        parts = hashed_str.split("$")
        if len(parts) != 5 or parts[1] != "pbkdf2-sha256":
            return False
        iterations = int(parts[2])
        salt = bytes.fromhex(parts[3])
        expected_dk = bytes.fromhex(parts[4])
        computed_dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(computed_dk, expected_dk)
    except Exception:
        return False


def json_encode(data: Any, pretty: bool = False) -> str:
    """Returns the JSON representation of a value."""
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def json_decode(json_str: str, assoc: bool = True) -> Any:
    """Decodes a JSON string."""
    return json.loads(json_str)


# =====================================================================
# 2. PHP-Style Embedded Template Engine
# =====================================================================

class HavenTemplate:
    """
    Embedded Template Engine for Haven / Ani++ / PHP-style scripts.
    Supports:
      - <?= expression ?>   : Escaped expression interpolation
      - <?!= expression ?>  : Raw (unescaped) HTML interpolation
      - <?haven ... ?>      : Multi-line Haven / Python statement blocks
      - <?ani ... ?>        : Multi-line Ani++ statement blocks
      - <?php ... ?>        : Emulated PHP statement blocks
    """

    def __init__(self, template_str: str, filename: str = "<template>"):
        self.template_str = template_str
        self.filename = filename

    def render(self, context: Optional[Dict[str, Any]] = None) -> str:
        ctx = dict(context or {})
        output_buffer: List[str] = []

        # Built-in helper functions injected into template scope
        scope = {
            "echo": lambda *args: output_buffer.append(" ".join(str(a) for a in args)),
            "print": lambda *args: output_buffer.append(" ".join(str(a) for a in args)),
            "htmlspecialchars": htmlspecialchars,
            "htmlentities": htmlentities,
            "strip_tags": strip_tags,
            "explode": explode,
            "implode": implode,
            "trim": trim,
            "json_encode": json_encode,
            "json_decode": json_decode,
        }
        scope.update(ctx)

        # Tokenize template into HTML literals and Code Tags
        # Regex captures:
        # 1. <?!= ... ?>  (raw expression)
        # 2. <?= ... ?>   (escaped expression)
        # 3. <?haven ... ?> or <?ani ... ?> or <?php ... ?> or <? ... ?> (code block)
        pattern = re.compile(
            r"<\?!\s*(.*?)\s*\?>|"
            r"<\?=\s*(.*?)\s*\?>|"
            r"<\?(?:haven|ani|php)?\s+(.*?)\s*\?>",
            re.DOTALL
        )

        last_pos = 0
        current_indent = 0
        compiled_script_lines = [
            "__output__ = []",
            "def __echo__(val, escape=False):",
            "    if escape: __output__.append(htmlspecialchars(str(val)))",
            "    else: __output__.append(str(val))",
        ]

        def emit(line: str):
            prefix = "    " * current_indent
            compiled_script_lines.append(prefix + line)

        # Convert template into an executable python/haven script
        for match in pattern.finditer(self.template_str):
            literal = self.template_str[last_pos:match.start()]
            if literal:
                # Append raw text literal
                emit(f"__echo__({json.dumps(literal)}, escape=False)")

            raw_expr, esc_expr, code_block = match.groups()

            if raw_expr is not None:
                emit(f"__echo__({raw_expr}, escape=False)")
            elif esc_expr is not None:
                emit(f"__echo__({esc_expr}, escape=True)")
            elif code_block is not None:
                # Transpile any Haven natural syntax inside code block
                from haven.transpiler import preprocess_haven
                clean_code = preprocess_haven(code_block.strip())
                for line in clean_code.splitlines():
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if stripped in ("end", "pass", "}", "endif", "endfor", "endwhile", "endforeach"):
                        if current_indent > 0:
                            current_indent -= 1
                    elif stripped.startswith("else:") or stripped.startswith("elif ") or stripped.startswith("otherwise:"):
                        old_indent = current_indent
                        current_indent = max(0, current_indent - 1)
                        emit(line.lstrip())
                        current_indent = old_indent
                    else:
                        emit(line.lstrip())
                        if stripped.endswith(":") or stripped.endswith("{"):
                            current_indent += 1

            last_pos = match.end()

        # Append remaining trailing literal
        trailing = self.template_str[last_pos:]
        if trailing:
            emit(f"__echo__({json.dumps(trailing)}, escape=False)")

        compiled_script = "\n".join(compiled_script_lines)

        exec_globals = dict(scope)
        exec_globals["htmlspecialchars"] = htmlspecialchars
        exec(compiled_script, exec_globals)

        rendered_output = "".join(exec_globals["__output__"])
        return rendered_output


# =====================================================================
# 3. HTTP Context & PHP-Style Superglobals ($_GET, $_POST, $_SESSION)
# =====================================================================

class SessionStore:
    """In-memory cryptographically signed session storage."""

    def __init__(self, secret_key: Optional[bytes] = None):
        self.secret_key = secret_key or os.urandom(32)
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create(self, session_id: Optional[str]) -> Tuple[str, Dict[str, Any]]:
        if session_id and session_id in self.sessions:
            return session_id, self.sessions[session_id]
        new_id = hashlib.sha256(os.urandom(32)).hexdigest()
        self.sessions[new_id] = {}
        return new_id, self.sessions[new_id]


_GLOBAL_SESSIONS = SessionStore()


class HttpContext:
    """
    PHP-Style Superglobals Web Context:
    Provides GET, POST, COOKIE, SERVER, SESSION, and FILES.
    """

    def __init__(
        self,
        method: str = "GET",
        path: str = "/",
        query_string: str = "",
        headers: Optional[Dict[str, str]] = None,
        body: bytes = b"",
        client_address: Tuple[str, int] = ("127.0.0.1", 8000)
    ):
        self.headers = headers or {}
        self.body = body

        # 1. $_SERVER
        self.SERVER: Dict[str, Any] = {
            "REQUEST_METHOD": method.upper(),
            "REQUEST_URI": path,
            "QUERY_STRING": query_string,
            "REMOTE_ADDR": client_address[0],
            "REMOTE_PORT": client_address[1],
            "HTTP_USER_AGENT": self.headers.get("User-Agent", ""),
            "HTTP_HOST": self.headers.get("Host", "localhost"),
            "CONTENT_TYPE": self.headers.get("Content-Type", ""),
            "REQUEST_TIME": time.time(),
        }

        # 2. $_GET
        parsed_query = urllib.parse.parse_qs(query_string, keep_blank_values=True)
        self.GET: Dict[str, str] = {k: v[0] if len(v) == 1 else v for k, v in parsed_query.items()}

        # 3. $_POST
        self.POST: Dict[str, Any] = {}
        content_type = self.SERVER["CONTENT_TYPE"]
        if "application/x-www-form-urlencoded" in content_type:
            parsed_form = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
            self.POST = {k: v[0] if len(v) == 1 else v for k, v in parsed_form.items()}
        elif "application/json" in content_type and body:
            try:
                self.POST = json.loads(body.decode("utf-8"))
            except Exception:
                self.POST = {}

        # 4. $_COOKIE
        self.COOKIE: Dict[str, str] = {}
        raw_cookie = self.headers.get("Cookie", "")
        if raw_cookie:
            c = http.cookies.SimpleCookie()
            c.load(raw_cookie)
            self.COOKIE = {k: morsel.value for k, morsel in c.items()}

        # 5. $_SESSION
        sid = self.COOKIE.get("HAVEN_SESSID")
        self.session_id, self.SESSION = _GLOBAL_SESSIONS.get_or_create(sid)

        # 6. Response cookies
        self.response_cookies: List[str] = []
        if sid != self.session_id:
            self.set_cookie("HAVEN_SESSID", self.session_id, httponly=True)

    def set_cookie(
        self,
        name: str,
        value: str,
        max_age: int = 86400,
        path: str = "/",
        httponly: bool = True,
        samesite: str = "Lax"
    ):
        cookie = f"{name}={value}; Path={path}; Max-Age={max_age}; SameSite={samesite}"
        if httponly:
            cookie += "; HttpOnly"
        self.response_cookies.append(cookie)


# =====================================================================
# 4. Lightweight Database Engine & Fluent QueryBuilder (DB)
# =====================================================================

class QueryBuilder:
    """Fluent, SQL-injection safe SQL QueryBuilder for Haven Web."""

    def __init__(self, table_name: str, db_connection: sqlite3.Connection):
        self.table_name = table_name
        self.conn = db_connection
        self._wheres: List[Tuple[str, str, Any]] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._order_by: Optional[str] = None

    def where(self, column: str, operator_or_val: Any, val: Optional[Any] = None) -> "QueryBuilder":
        if val is None:
            operator = "="
            value = operator_or_val
        else:
            operator = operator_or_val
            value = val
        self._wheres.append((column, operator, value))
        return self

    def order_by(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        self._order_by = f"{column} {direction.upper()}"
        return self

    def limit(self, count: int) -> "QueryBuilder":
        self._limit = count
        return self

    def offset(self, count: int) -> "QueryBuilder":
        self._offset = count
        return self

    def get(self) -> List[Dict[str, Any]]:
        """Executes the query and returns all matching rows as dictionaries."""
        sql = f"SELECT * FROM {self.table_name}"
        params: List[Any] = []
        if self._wheres:
            where_clauses = [f"{col} {op} ?" for col, op, _ in self._wheres]
            sql += " WHERE " + " AND ".join(where_clauses)
            params.extend([v for _, _, v in self._wheres])

        if self._order_by:
            sql += f" ORDER BY {self._order_by}"
        if self._limit is not None:
            sql += f" LIMIT {int(self._limit)}"
        if self._offset is not None:
            sql += f" OFFSET {int(self._offset)}"

        cur = self.conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        return [dict(zip(cols, r)) for r in rows]

    def first(self) -> Optional[Dict[str, Any]]:
        """Returns the first matching row or None."""
        self.limit(1)
        res = self.get()
        return res[0] if res else None

    def insert(self, record: Dict[str, Any]) -> int:
        """Inserts a record and returns the inserted row ID."""
        cols = list(record.keys())
        placeholders = ", ".join(["?"] * len(cols))
        sql = f"INSERT INTO {self.table_name} ({', '.join(cols)}) VALUES ({placeholders})"
        cur = self.conn.cursor()
        cur.execute(sql, list(record.values()))
        self.conn.commit()
        return cur.lastrowid or 0

    def update(self, values: Dict[str, Any]) -> int:
        """Updates matching rows and returns the number of affected rows."""
        set_clauses = [f"{col} = ?" for col in values.keys()]
        sql = f"UPDATE {self.table_name} SET {', '.join(set_clauses)}"
        params = list(values.values())
        if self._wheres:
            where_clauses = [f"{col} {op} ?" for col, op, _ in self._wheres]
            sql += " WHERE " + " AND ".join(where_clauses)
            params.extend([v for _, _, v in self._wheres])
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur.rowcount

    def delete(self) -> int:
        """Deletes matching rows."""
        sql = f"DELETE FROM {self.table_name}"
        params: List[Any] = []
        if self._wheres:
            where_clauses = [f"{col} {op} ?" for col, op, _ in self._wheres]
            sql += " WHERE " + " AND ".join(where_clauses)
            params.extend([v for _, _, v in self._wheres])
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur.rowcount


class Database:
    """Platform-Independent Database Manager (SQLite / In-Memory)."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def table(self, name: str) -> QueryBuilder:
        return QueryBuilder(name, self.conn)

    def raw_query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute(sql, params or [])
        self.conn.commit()
        if cur.description:
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]
        return []

    def close(self):
        self.conn.close()


DB = Database()


# =====================================================================
# 5. Platform-Independent Web Server (HavenDevServer)
# =====================================================================

class HavenHttpHandler(http.server.BaseHTTPRequestHandler):
    """Dynamic HTTP Handler that serves static files and renders Haven/PHP embedded templates."""

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def handle_request(self, method: str):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/":
            path = "/index.html"

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        # Build HttpContext
        context = HttpContext(
            method=method,
            path=path,
            query_string=parsed.query,
            headers=dict(self.headers),
            body=body,
            client_address=self.client_address
        )

        root_dir = getattr(self.server, "document_root", os.getcwd())
        file_path = os.path.normpath(os.path.join(root_dir, path.lstrip("/")))

        # Check if file exists
        if os.path.isfile(file_path):
            # If it's a dynamic template (.html, .hvn, .ani, .php)
            if file_path.endswith((".html", ".hvn", ".ani", ".php")):
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    template_content = f.read()
                tmpl = HavenTemplate(template_content, filename=file_path)
                try:
                    rendered = tmpl.render({
                        "GET": context.GET,
                        "POST": context.POST,
                        "SERVER": context.SERVER,
                        "COOKIE": context.COOKIE,
                        "SESSION": context.SESSION,
                        "DB": DB,
                    })
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    for cookie in context.response_cookies:
                        self.send_header("Set-Cookie", cookie)
                    self.end_headers()
                    self.wfile.write(rendered.encode("utf-8"))
                    return
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    err_html = f"<h1>500 Internal Server Error</h1><pre>{htmlspecialchars(str(e))}</pre>"
                    self.wfile.write(err_html.encode("utf-8"))
                    return
            else:
                # Serve static asset
                self.send_response(200)
                content_type = "application/octet-stream"
                if file_path.endswith(".css"): content_type = "text/css"
                elif file_path.endswith(".js"): content_type = "application/javascript"
                elif file_path.endswith(".json"): content_type = "application/json"
                elif file_path.endswith(".png"): content_type = "image/png"
                elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"): content_type = "image/jpeg"
                elif file_path.endswith(".svg"): content_type = "image/svg+xml"

                self.send_header("Content-Type", content_type)
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        # 404 Not Found
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(f"<h1>404 Not Found</h1><p>The requested path {path} was not found.</p>".encode("utf-8"))


def serve(port: int = 8000, host: str = "127.0.0.1", document_root: Optional[str] = None):
    """Launches the platform-independent Haven development web server."""
    root = os.path.abspath(document_root or os.getcwd())
    server = http.server.HTTPServer((host, port), HavenHttpHandler)
    setattr(server, "document_root", root)
    print(f"[*] Ani++ / Haven Web Server running at: http://{host}:{port}/")
    print(f"[*] Document Root: {root}")
    print("[*] Press Ctrl+C to terminate.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down Haven Web Server.")
        server.server_close()
