"""All Matplotlib calls for XAS, distinct from readers and CLI."""
from pathlib import Path
class PlotFdmXas:
    def plot(self,spectra,output,*,title=None,xlabel='Energy (eV)',ylabel='XAS'):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,axis=plt.subplots()
        for energy,intensity,label in spectra:axis.plot(energy,intensity,label=label)
        axis.set(xlabel=xlabel,ylabel=ylabel,title=title)
        if any(label for _,_,label in spectra):axis.legend()
        fig.tight_layout();fig.savefig(output);plt.close(fig)
        return Path(output)
