"""XAS operations extracted from CLI scripts, independent from file readers."""
import numpy as np
class AnalyzeFdmXas:
    @staticmethod
    def average(spectra,weights=None):
        spectra=list(spectra)
        if not spectra:raise ValueError('No spectra')
        base=np.asarray(spectra[0].energy)
        for spectrum in spectra[1:]:
            if not np.array_equal(base,spectrum.energy):
                raise ValueError('Energy grids are different; interpolation not requested')
        w=np.ones(len(spectra)) if weights is None else np.asarray(weights,dtype=float)
        if len(w)!=len(spectra) or np.sum(w)==0:raise ValueError('Invalid weights')
        return base,np.average(np.stack([s.xas[:,0] for s in spectra]),axis=0,weights=w)
    @staticmethod
    def photon_energy(convolution,raw_xas,*,subtract_fermi=False,fermi_energy=None):
        if raw_xas.edge_energy is None:raise ValueError('Missing E_edge')
        if subtract_fermi and fermi_energy is None:raise ValueError('Missing Fermi energy')
        return convolution.energy+raw_xas.edge_energy-(fermi_energy if subtract_fermi else 0),convolution.xas[:,0]
