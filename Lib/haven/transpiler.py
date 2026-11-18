"""
Ani++ / Haven Language Preprocessor & Dual-Grammar Engine
Transforms Ani++, Star Language syntax, Global Natural Dialects, and Haven natural English
into standardized high-performance AST bytecode.
Architecture & Specification by Anirudha Puthraya.
Standard: ODCS-1.0.0 & OFCS-1.0.0
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import re
from .i18n import translate_dialects


def preprocess_haven(source_code: str) -> str:
    """
    Transforms Ani++, Star, Natural English, and Dialect code into standard Haven/Python AST.
    Guarantees 100% universal compatibility across all platforms and runtimes.
    """
    # 1. Apply Universal Global Natural Dialects translation
    source_code = translate_dialects(source_code)
    lines = source_code.splitlines()
    processed_lines = []

    for line in lines:
        stripped = line.strip()

        # Skip comments and empty lines
        if not stripped or stripped.startswith("#"):
            processed_lines.append(line)
            continue

        indent = line[:len(line) - len(line.lstrip())]

        # 2. 'end' statement -> 'pass'
        if stripped == "end":
            processed_lines.append(indent + "pass")
            continue

        # 3. Transform Star Arrow Lambdas FIRST so assignments can capture them
        # '() -> expr' -> 'lambda: expr', '(x, y) -> expr' -> 'lambda x, y: expr'
        curr_line = line
        if not re.search(r'^\s*(def|function|define)\b', curr_line):
            curr_line = re.sub(r'\(\)\s*->\s*', 'lambda: ', curr_line)
            curr_line = re.sub(r'\(([a-zA-Z_][a-zA-Z0-9_,\s]*)\)\s*->\s*', r'lambda \1: ', curr_line)

        # 4. 'use <module>' -> 'import <module>'
        m_use = re.match(r'^(\s*)use\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s*$', curr_line)
        if m_use:
            processed_lines.append(f"{m_use.group(1)}import {m_use.group(2)}")
            continue

        # 5. 'variable <name> = <val>' -> '<name> = <val>'
        m_var = re.match(r'^(\s*)variable\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', curr_line)
        if m_var:
            lead, name, val = m_var.groups()
            processed_lines.append(f"{lead}{name} = {val}")
            continue

        # 6. 'constant <NAME> = <val>' -> '<NAME> = <val>'
        m_const = re.match(r'^(\s*)constant\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', curr_line)
        if m_const:
            lead, name, val = m_const.groups()
            processed_lines.append(f"{lead}{name} = {val}")
            continue

        # 7. 'durable record <Name>:' -> '@durable_record\nclass <Name>:'
        m_durable = re.match(r'^(\s*)durable\s+record\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:$', curr_line)
        if m_durable:
            lead, name = m_durable.groups()
            processed_lines.append(f"{lead}@durable_record\n{lead}class {name}:")
            continue

        # 8. 'to <name>(<args>):' -> 'def <name>(<args>):'
        m_to = re.match(r'^(\s*)to\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)\s*:$', curr_line)
        if m_to:
            lead, name, args = m_to.groups()
            processed_lines.append(f"{lead}def {name}({args}):")
            continue

        # 8b. 'to <name>:' -> 'def <name>():'
        m_to_bare = re.match(r'^(\s*)to\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:$', curr_line)
        if m_to_bare:
            lead, name = m_to_bare.groups()
            processed_lines.append(f"{lead}def {name}():")
            continue

        # 9. 'say <expr...>' -> 'print(<expr...>)'
        m_say = re.match(r'^(\s*)say\s+(.+)$', curr_line)
        if m_say:
            lead, expr = m_say.groups()
            processed_lines.append(f"{lead}print({expr})")
            continue

        # 10. 'show <expr...>' -> 'print(<expr...>)'
        m_show = re.match(r'^(\s*)show\s+(.+)$', curr_line)
        if m_show:
            lead, expr = m_show.groups()
            processed_lines.append(f"{lead}print({expr})")
            continue

        # 11. 'increase <var> by <val>' -> '<var> += <val>'
        m_inc = re.match(r'^(\s*)increase\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+by\s+(.+)$', curr_line)
        if m_inc:
            lead, var, val = m_inc.groups()
            processed_lines.append(f"{lead}{var} += {val}")
            continue

        # 12. 'decrease <var> by <val>' -> '<var> -= <val>'
        m_dec = re.match(r'^(\s*)decrease\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+by\s+(.+)$', curr_line)
        if m_dec:
            lead, var, val = m_dec.groups()
            processed_lines.append(f"{lead}{var} -= {val}")
            continue

        # 13. 'give back <val>' -> 'return <val>'
        m_ret = re.match(r'^(\s*)give\s+back\s*(.*)$', curr_line)
        if m_ret:
            lead, val = m_ret.groups()
            processed_lines.append(f"{lead}return {val}" if val else f"{lead}return")
            continue

        # 14. 'remember <var> as <val>' -> '<var> = <val>'
        m_rem = re.match(r'^(\s*)remember\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+(.+)$', curr_line)
        if m_rem:
            lead, var, val = m_rem.groups()
            processed_lines.append(f"{lead}{var} = {val}")
            continue

        # 15. 'set <name> to <val>' -> '<name> = <val>'
        m_set = re.match(r'^(\s*)set\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+to\s+(.+)$', curr_line)
        if m_set:
            lead, name, val = m_set.groups()
            processed_lines.append(f"{lead}{name} = {val}")
            continue

        # 16. 'let <name> be <val>' -> '<name> = <val>'
        m_let = re.match(r'^(\s*)let\s+([a-zA-Z_0-9_,\s]+)\s+be\s+(.+)$', curr_line)
        if m_let:
            lead, name, val = m_let.groups()
            processed_lines.append(f"{lead}{name} = {val}")
            continue

        # 17. 'whenever <cond>:' -> 'if <cond>:'
        m_when = re.match(r'^(\s*)whenever\s+(.+):$', curr_line)
        if m_when:
            lead, cond = m_when.groups()
            processed_lines.append(f"{lead}if {cond}:")
            continue

        # 18. 'otherwise if <cond>:' -> 'elif <cond>:'
        m_elif = re.match(r'^(\s*)otherwise\s+if\s+(.+):$', curr_line)
        if m_elif:
            lead, cond = m_elif.groups()
            processed_lines.append(f"{lead}elif {cond}:")
            continue

        # 19. 'otherwise:' -> 'else:'
        m_else = re.match(r'^(\s*)otherwise\s*:$', curr_line)
        if m_else:
            lead = m_else.group(1)
            processed_lines.append(f"{lead}else:")
            continue

        # 20. 'forever:' -> 'while True:'
        m_forever = re.match(r'^(\s*)forever\s*:$', curr_line)
        if m_forever:
            lead = m_forever.group(1)
            processed_lines.append(f"{lead}while True:")
            continue

        # 21. 'ensure <cond> otherwise <msg>' -> 'assert <cond>, <msg>'
        m_ensure = re.match(r'^(\s*)ensure\s+(.+?)\s+otherwise\s+(.+)$', curr_line)
        if m_ensure:
            lead, cond, msg = m_ensure.groups()
            processed_lines.append(f"{lead}assert {cond}, {msg}")
            continue

        # 22. 'preserve <asset> as <alias> into <ledger>' -> 'checkpoint(<asset>, alias=<alias>, ledger=<ledger>)'
        m_pres = re.match(r'^(\s*)preserve\s+(.+?)\s+as\s+(.+?)\s+into\s+(.+)$', curr_line)
        if m_pres:
            lead, asset, alias, ledger = m_pres.groups()
            processed_lines.append(f"{lead}checkpoint({asset}, alias={alias}, ledger={ledger})")
            continue

        # 23. 'recover as <err>:' -> 'except Exception as <err>:'
        m_rec_as = re.match(r'^(\s*)recover\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:$', curr_line)
        if m_rec_as:
            lead, err = m_rec_as.groups()
            processed_lines.append(f"{lead}except Exception as {err}:")
            continue

        # 24. 'recover:' -> 'except Exception:'
        m_rec = re.match(r'^(\s*)recover\s*:$', curr_line)
        if m_rec:
            lead = m_rec.group(1)
            processed_lines.append(f"{lead}except Exception:")
            continue

        # 25. 'unless <cond>:' -> 'if not (<cond>):'
        m_unless = re.match(r'^(\s*)unless\s+(.+):$', curr_line)
        if m_unless:
            lead, cond = m_unless.groups()
            processed_lines.append(f"{lead}if not ({cond}):")
            continue

        # 26. 'until <cond>:' -> 'while not (<cond>):'
        m_until = re.match(r'^(\s*)until\s+(.+):$', curr_line)
        if m_until:
            lead, cond = m_until.groups()
            processed_lines.append(f"{lead}while not ({cond}):")
            continue

        # 27. 'repeat <N> times:' -> 'for _ in range(<N>):'
        m_repeat = re.match(r'^(\s*)repeat\s+(.+?)\s+times\s*:$', curr_line)
        if m_repeat:
            lead, n = m_repeat.groups()
            processed_lines.append(f"{lead}for _ in range({n}):")
            continue

        # 28. 'for each <item> in <coll>:' -> 'for <item> in <coll>:'
        m_each = re.match(r'^(\s*)for\s+each\s+(.+?)\s+in\s+(.+):$', curr_line)
        if m_each:
            lead, item, coll = m_each.groups()
            processed_lines.append(f"{lead}for {item} in {coll}:")
            continue

        processed_lines.append(curr_line)

    return "\n".join(processed_lines)
