"""
Haven Language CLI Entry Point
Open Digital Continuity Standard (ODCS) by Anirudha Puthraya.
"""
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].endswith(('.hvn', '.haven')):
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            code = f.read()
        exec(compile(code, sys.argv[1], 'exec'))
    else:
        import idlelib.pyshell
        idlelib.pyshell.main()
