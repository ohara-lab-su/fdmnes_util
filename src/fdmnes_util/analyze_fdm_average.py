#!/usr/bin/env python3
"""Average corresponding FDMNES spectra without changing their energy grids.

SAE source: ``sae/commands/fdPDOS_XAS_av.py`` (2015-09-09; Python 2/3
update 2018-08-17). The original script averages three calculations.
This module extracts that numerical operation into a reusable class.
"""

import numpy as np


class AnalyzeFdmAverage:
    """Average data from independent calculations on a shared energy grid."""

    def energy_reference(self, input_file, spectrum, fermi=False):
        """Determine the shared energy shift used by the SAE average plot.

        The source script distinguishes FDMNES Fermi-relative and photon-energy
        calculation modes. Its photon-energy-to-Fermi branch contains a
        subtraction without assignment; this implementation corrects that
        specific defect rather than reproducing an undefined offset.

        Args:
            input_file: FdmInp instance describing the calculation mode.
            spectrum: FdmTxt instance containing edge and Fermi energies.
            fermi: If True, use the Fermi-relative energy reference.
                Otherwise, use photon energy.

        Returns:
            tuple[float, float]: Energy-axis shift and absolute Fermi
            position in the photon-energy reference, both in eV.

        Raises:
            ValueError: If the required energy metadata is not finite.
        """
        edge_energy = float(spectrum.get_eedge())
        fermi_energy = float(spectrum.get_efermi())

        if not np.isfinite(edge_energy):
            raise ValueError("The absorption-edge energy must be finite")
        if not np.isfinite(fermi_energy):
            raise ValueError("The Fermi energy must be finite")

        absolute_fermi = edge_energy + fermi_energy
        photon_mode = input_file.get_energygpho()

        if photon_mode:
            if fermi:
                energy_shift = -absolute_fermi
            else:
                energy_shift = 0.0
        else:
            if fermi:
                energy_shift = -fermi_energy
            else:
                energy_shift = edge_energy

        return energy_shift, absolute_fermi

    def average(self, readers, value_method, *, divisor=None, **kwargs):
        """Return the common energy axis and arithmetic mean of a quantity.

        Args:
            readers: Nonempty sequence of FDMNES output objects.
            value_method: Name of the data access method on each object.
            divisor: Optional positive divisor for the sum, used for SAE's
                per-atom normalization. Defaults to the number of readers.
            **kwargs: Arguments passed to the selected data access method.

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: Energy and mean values.

        Raises:
            ValueError: If readers are missing, grids disagree, or numerical
                values are non-finite or have inconsistent dimensions.
            AttributeError: If the requested accessor is unavailable.
        """
        if not readers:
            raise ValueError("At least one calculation is required")
        if divisor is None:
            divisor = len(readers)
        if not np.isfinite(divisor) or divisor <= 0:
            raise ValueError("The averaging divisor must be positive and finite")

        reference_energy = np.asarray(readers[0].get_eng(), dtype=float)
        if reference_energy.ndim != 1:
            raise ValueError("Energy grid must be one-dimensional")
        if reference_energy.size == 0:
            raise ValueError("Energy grid must not be empty")
        if not np.all(np.isfinite(reference_energy)):
            raise ValueError("Energy grid contains non-finite values")

        sum_values = None

        for reader in readers:
            energy = np.asarray(reader.get_eng(), dtype=float)
            if energy.ndim != 1:
                raise ValueError("Energy grid must be one-dimensional")
            if not np.all(np.isfinite(energy)):
                raise ValueError("Energy grid contains non-finite values")
            if energy.shape != reference_energy.shape:
                raise ValueError("Energy grid lengths differ between calculations")
            if not np.allclose(energy, reference_energy, rtol=0.0, atol=1e-8):
                raise ValueError("Energy grids differ between calculations")

            accessor = getattr(reader, value_method)
            values = np.asarray(accessor(**kwargs), dtype=float)
            if values.ndim == 0:
                raise ValueError("Spectrum values must have an energy dimension")
            if not np.all(np.isfinite(values)):
                raise ValueError("Spectrum contains non-finite values")
            if values.shape[0] != reference_energy.shape[0]:
                raise ValueError("Energy and data lengths differ")

            if sum_values is None:
                sum_values = np.zeros_like(values, dtype=float)
            if values.shape != sum_values.shape:
                raise ValueError("Data shapes differ between calculations")
            sum_values += values

        mean_values = sum_values / divisor
        return reference_energy.copy(), mean_values
