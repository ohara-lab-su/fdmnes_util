#!/usr/bin/env python3
"""Plot averaged orbital-resolved DOS and optional XAS.

SAE source: ``sae/commands/fdPDOS_XAS_av.py``. The original program
uses a portrait layout with orbital blocks and an optional XAS panel.
"""

from pathlib import Path


class PlotFdmAverage:
    """Draw averaged FDMNES orbital projections and absorption spectra."""

    def plot(
        self,
        orbital_data,
        output,
        *,
        xas_data=None,
        raw_xas_data=None,
        emin=None,
        emax=None,
        dmax=None,
        ymax=None,
    ):
        """Save a stacked plot of orbital projections and optional XAS.

        Args:
            orbital_data: Sequence of (label, energy, DOS) records.
            output: Destination image filename.
            xas_data: Optional (energy, absorption) pair after broadening.
            raw_xas_data: Optional (energy, absorption) pair before broadening.
            emin: Optional minimum energy.
            emax: Optional maximum energy.
            dmax: Optional upper bound for each PDOS panel.
            ymax: Optional upper bound for the XAS panel.

        Returns:
            pathlib.Path: Path to the generated figure.

        Raises:
            ValueError: If no orbital data are provided.
        """
        if raw_xas_data is not None and xas_data is None:
            raise ValueError("Raw XAS overlay requires convolved XAS")

        if not orbital_data:
            raise ValueError("At least one orbital is required")

        if dmax is not None:
            if dmax <= 0:
                raise ValueError("dmax must be positive")

        if ymax is not None:
            if ymax <= 0:
                raise ValueError("ymax must be positive")

        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        panel_count = len(orbital_data)
        if xas_data is not None:
            panel_count += 1

        figure, axes = plt.subplots(
            panel_count,
            1,
            sharex=True,
            figsize=(7.0, 9.89),
            squeeze=False,
        )
        axis_index = 0
        for label, energy, density in orbital_data:
            axis = axes[axis_index, 0]
            axis.plot(energy, density, linewidth=1.8, label=label)
            axis.set_ylabel("PDOS [states/eV]")
            if dmax is not None:
                axis.set_ylim(top=dmax)
            axis.legend(loc="upper right")
            axis_index += 1

        if xas_data is not None:
            energy, absorption = xas_data
            axis = axes[axis_index, 0]
            axis.plot(
                energy,
                absorption,
                linewidth=1.8,
                color="black",
                label="XAS (with broadening)",
            )
            if raw_xas_data is not None:
                raw_energy, raw_absorption = raw_xas_data
                axis.plot(
                    raw_energy,
                    raw_absorption,
                    linewidth=1.0,
                    label="XAS (without broadening)",
                )
                axis.legend(loc="lower right")
            axis.set_ylabel("XAS [arb. unit]")
            if ymax is not None:
                axis.set_ylim(top=ymax)

        for axis_row in axes:
            axis = axis_row[0]
            if emin is not None:
                axis.set_xlim(left=emin)
            if emax is not None:
                axis.set_xlim(right=emax)

        axes[-1, 0].set_xlabel("Energy [eV]")
        figure.tight_layout()
        figure.savefig(output)
        plt.close(figure)
        return Path(output)
