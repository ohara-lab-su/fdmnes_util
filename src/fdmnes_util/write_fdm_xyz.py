"""Write XYZ output from the parsed FDMNES calculation log."""
from pathlib import Path
class WriteFdmXyz:
    def write(self, symbols, positions,filename):
        if len(symbols)!=len(positions):raise ValueError('Atom/coordinate count mismatch')
        out=Path(filename)
        lines=[str(len(symbols)),'']
        lines += [f'{s} {x:.10f} {y:.10f} {z:.10f}' for s,(x,y,z) in zip(symbols,positions)]
        out.write_text('\n'.join(lines)+'\n')
        return out
