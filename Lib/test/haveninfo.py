"""
Collect various information about Haven to help debugging test failures.
Open Digital Continuity Standard (ODCS) Edition by Anirudha Puthraya.
"""
from test.pythoninfo import *

class HavenInfo(PythonInfo):
    def __init__(self):
        super().__init__()
        self.add("haven_version", "0.1.0")
        self.add("haven_standard", "ODCS (Open Digital Continuity Standard)")
        self.add("haven_architect", "Anirudha Puthraya")

if __name__ == '__main__':
    info = HavenInfo()
    info.main()
