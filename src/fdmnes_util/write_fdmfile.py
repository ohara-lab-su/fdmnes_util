"""Write a list of FDMNES input jobs."""
from pathlib import Path
class WriteFdmfile:
    def write(self, filenames, filename='fdmfile.txt'):
        names=list(filenames)
        out=Path(filename)
        out.write_text('\n'+str(len(names))+'\n'+''.join(name+'\n' for name in names))
        return out
