#!/usr/bin/env python3
"""Average corresponding FDMNES spectra without changing their energy grids.

SAE source: ``sae/commands/fdPDOS_XAS_av.py`` (2015-09-09; Python 2/3
update 2018-08-17). The original script averages three calculations.
This module extracts that numerical operation into a reusable class.
"""

import numpy as np


class AnalyzeFdmAverage:
    """Average data from independent calculations on a shared energy grid."""

    def average(self, readers, value_method, **kwargs):
        """Return the common energy axis and arithmetic mean of a quantity.

        Args:
            readers: Nonempty sequence of FDMNES output objects.
            value_method: Name of the data access method on each object.
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

        mean_values = sum_values / len(readers)
        return reference_energy.copy(), mean_values
