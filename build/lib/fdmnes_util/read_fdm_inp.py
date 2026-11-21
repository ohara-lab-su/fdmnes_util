"""FDMNES .inp input: file tags and optional crystal structure."""
from pathlib import Path
import re

class ReadFdmInp:
    """Parse FDMNES input keywords without requiring a Crystal section."""
    KEYWORDS = {'filout','spin','allsite','energpho','energygpho',
                'convolution','conv_out','calculation','nonexc','crystal'}
    def __init__(self, filename='read_pdb.inp'):
        self.path=Path(filename)
        self.lines=self.path.read_text(encoding='utf-8',errors='replace').splitlines()
        self.tags={}
        current=None
        for line in self.lines:
            content=line.split('!',1)[0].split('#',1)[0].strip()
            if not content or content.startswith('!'):continue
            words=content.split()
            key=words[0].lower()
            if key == 'end':break
            if key in self.KEYWORDS:
                current=key
                self.tags.setdefault(key,[])
                if len(words)>1:self.tags[key].append(' '.join(words[1:]))
            elif current:
                self.tags[current].append(content)
    def get_filout(self):
        values=self.tags.get('filout',[])
        return values[0] if values else ''
    def get_ispin(self):return 2 if 'spin' in self.tags else 1
    def get_allsite(self):return 'allsite' in self.tags
    def get_energygpho(self):return 'energpho' in self.tags or 'energygpho' in self.tags
    def get_nonexc(self):return 'nonexc' in self.tags
    def get_convolution(self):return 'convolution' in self.tags
    def get_conv_out(self):return self.tags.get('conv_out',[''])[0] if self.tags.get('conv_out') else ''
    def get_calculation(self):return self.tags.get('calculation',[''])[0] if self.tags.get('calculation') else ''
    def get_cellparam(self):
        entries=self.tags.get('crystal',[])
        if not entries: return None
        numbers=[]
        for row in entries:
            try:numbers=[float(x) for x in row.split()[:6]]
            except ValueError:continue
            if len(numbers)==6:return numbers
        return None
