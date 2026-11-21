#!/usr/bin/env python3
"""Density-of-states plotting, not embedded in read_sd implementations."""
from pathlib import Path
class PlotFdmDos:
    def plot(self,reader,output,orbitals=('s','p','d'),*,integrated=False):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,axis=plt.subplots()
        for index,orbital in enumerate(orbitals):
            if index>reader.get_lmax():continue
            y=reader.get_intldos(orbital) if integrated else reader.get_ldos(orbital)
            axis.plot(reader.get_eng(),y,label=orbital)
        axis.set(xlabel='Energy (eV)',ylabel='DOS')
        axis.legend();fig.tight_layout();fig.savefig(output);plt.close(fig)
        return Path(output)
