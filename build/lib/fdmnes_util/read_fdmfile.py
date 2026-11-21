"""FDMNES fdmfile.txt calculation input list."""
from pathlib import Path
class ReadFdmfile:
    def __init__(self,filename='fdmfile.txt'):
        self.path=Path(filename)
        lines=[s.strip() for s in self.path.read_text().splitlines() if s.strip()]
        if not lines:raise ValueError('Empty fdmfile.txt')
        count=int(lines[0]);self.filenames=lines[1:1+count]
        if len(self.filenames)!=count:raise ValueError('Incomplete fdmfile.txt')
    def get_filout(self):return self.filenames[0] if self.filenames else ''
