#!/usr/bin/env python3
"""XAS numerical operations that do not depend on Matplotlib or CLI options."""

from pathlib import Path

import numpy as np

from .read_fdm_conv import ReadFdmConv
from .read_fdm_txt import ReadFdmTxt


class AnalyzeFdmXas:
    """Numerical analysis of FDMNES absorption spectra."""

    @staticmethod
    def average(spectra, weights=None):
        spectra = list(spectra)
        if not spectra:
            raise ValueError("No spectra")

        energy = np.asarray(spectra[0].energy)
        for spectrum in spectra[1:]:
            if not np.array_equal(energy, spectrum.energy):
                raise ValueError(
                    "Energy grids are different; interpolation not requested"
                )

        if weights is None:
            weights = np.ones(len(spectra))
        else:
            weights = np.asarray(weights, dtype=float)

        if len(weights) != len(spectra):
            raise ValueError("Invalid weights")
        if np.sum(weights) == 0:
            raise ValueError("Invalid weights")

        intensities = []
        for spectrum in spectra:
            intensities.append(spectrum.xas[:, 0])

        values = np.stack(intensities)
        average = np.average(values, axis=0, weights=weights)
        return energy, average

    @staticmethod
    def photon_energy(
        convolution,
        raw_xas,
        *,
        subtract_fermi=False,
        fermi_energy=None,
    ):
        if raw_xas.edge_energy is None:
            raise ValueError("Missing E_edge")

        if subtract_fermi and fermi_energy is None:
            raise ValueError("Missing Fermi energy")

        zero = 0.0
        if subtract_fermi:
            zero = fermi_energy

        energy = convolution.energy + raw_xas.edge_energy - zero
        intensity = convolution.xas[:, 0]
        return energy, intensity

    @staticmethod
    def fermi_relative_convolution(convolution, raw_xas):
        """Convert a convolved spectrum to the Fermi-relative energy axis.

        The original ``fdXAS_specified.py`` subtracts the Fermi energy
        from the energy column in ``*_conv.txt``. It does not add the
        absorption-edge energy in this particular plotting operation.

        Args:
            convolution: Reader for the convolved FDMNES spectrum.
            raw_xas: Reader for the corresponding non-convolved spectrum.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: Fermi-relative energy
                and absorption intensity, in the original row order.
        """
        energy = convolution.get_eng().copy()
        intensity = convolution.get_xas().copy()
        fermi_energy = raw_xas.get_efermi()
        energy -= fermi_energy
        return energy, intensity

    @staticmethod
    def energy_reference(energy, raw_xas, *, input_is_photon, fermi):
        """Apply the energy-axis rules used by the original FDplot_XASs script.

        For non-photon-energy input the calculation's axis is relative to the
        absorption edge. With ``-f``, the axis becomes relative to E_Fermi.
        When input is already photon energy, the original script subtracts
        both E_edge and E_Fermi to produce the Fermi-relative axis.
        """
        energy = np.asarray(energy)
        edge_energy = raw_xas.get_eedge()
        fermi_energy = raw_xas.get_efermi()

        if edge_energy is None:
            raise ValueError("The raw XAS file has no edge energy")

        if input_is_photon:
            if fermi:
                return energy - fermi_energy - edge_energy
            return energy.copy()

        if fermi:
            return energy - fermi_energy

        return energy + edge_energy

    @classmethod
    def site_spectra(
        cls,
        base_name,
        site_indices,
        *,
        convolved=True,
        input_is_photon=None,
        fermi=None,
    ):
        """Read individual allsite outputs without changing site ordering.

        ``input_is_photon`` and ``fermi`` must be passed together to request
        an energy-axis conversion. Omission of both retains the old raw axis.
        """
        indices = list(site_indices)
        if not indices:
            raise ValueError("At least one absorbing site is required")
        if len(set(indices)) != len(indices):
            raise ValueError("Duplicate absorbing-site numbers")

        if (input_is_photon is None) != (fermi is None):
            raise ValueError("Specify both energy-reference options")

        result = []
        for index in indices:
            if not isinstance(index, int) or index < 1:
                raise ValueError(f"Invalid absorbing-site number: {index!r}")

            prefix = Path(f"{base_name}_{index}")
            if convolved:
                output_path = Path(f"{prefix}_conv.txt")
                reader = ReadFdmConv(output_path)
            else:
                output_path = Path(f"{prefix}.txt")
                reader = ReadFdmTxt(output_path)

            energy = reader.get_eng().copy()
            intensity = reader.get_xas().copy()

            if input_is_photon is not None:
                raw_xas = ReadFdmTxt(Path(f"{prefix}.txt"))
                energy = cls.energy_reference(
                    energy,
                    raw_xas,
                    input_is_photon=input_is_photon,
                    fermi=fermi,
                )

            label = f"absorber={index}"
            result.append((energy, intensity, label))

        return result
