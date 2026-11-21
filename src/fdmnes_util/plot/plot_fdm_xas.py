#!/usr/bin/env python3
"""Plot XAS spectra. File parsing and energy conversion belong elsewhere."""

from pathlib import Path


class PlotFdmXas:
    """Matplotlib visualizations for FDMNES XAS."""

    def plot(
        self,
        spectra,
        output,
        *,
        title=None,
        xlabel="Energy (eV)",
        ylabel="XAS",
    ):
        """plotの処理を実行する。
        
        Args:
            spectra: spectraを指定する。
            output: outputを指定する。
            title: titleを指定する。
            xlabel: xlabelを指定する。
            ylabel: ylabelを指定する。
        
        Returns:
            処理結果。
        
        """
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figure, axis = plt.subplots()
        for energy, intensity, label in spectra:
            axis.plot(energy, intensity, label=label)

        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.set_title(title)

        if any(label for _, _, label in spectra):
            axis.legend()

        figure.tight_layout()
        figure.savefig(output)
        plt.close(figure)
        return Path(output)

    def plot_sites(
        self,
        spectra,
        output,
        *,
        observed=None,
        xmin=None,
        xmax=None,
        ymax=None,
        fermi=False,
        fermi_position=None,
    ):
        """Draw computed and optionally observed XAS in separate panels.

        Args:
            spectra: Computed spectra as energy, intensity, label tuples.
            output: Destination path for the figure.
            observed: Optional Athena spectra for the upper panel.
            xmin: Optional lower limit of the energy axis.
            xmax: Optional upper limit of the energy axis.
            ymax: Optional upper limit of the absorption axis.
            fermi: Whether the energy axis is Fermi-relative.
            fermi_position: Energy of the vertical Fermi marker.

        Returns:
            pathlib.Path: Destination of the saved figure.
        """
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figure, axes = plt.subplots(
            2,
            1,
            figsize=(8.1, 9.89),
            sharex=True,
        )
        top, bottom = axes

        plotted = False
        for energy, intensity, label in spectra:
            bottom.plot(energy, intensity, linewidth=1, label=label)
            plotted = True

        if not plotted:
            plt.close(figure)
            raise ValueError("No XAS spectra to plot")

        bottom.set_ylabel("Absorption [arb. unit]")
        if fermi:
            bottom.set_xlabel("Energy above Fermi [eV]")
        else:
            bottom.set_xlabel("Photon Energy [eV]")

        if fermi_position is not None:
            bottom.axvline(
                fermi_position,
                color="black",
                linewidth=1,
            )

        bottom.legend(loc="lower right")
        if xmin is not None or xmax is not None:
            bottom.set_xlim(left=xmin, right=xmax)
        if ymax is not None:
            bottom.set_ylim(top=ymax)

        if observed:
            for energy, intensity, label in observed:
                top.plot(energy, intensity, label=label)
            top.legend(loc="lower right")
            top.set_ylabel("Observed [arb. unit]")
        else:
            top.set_visible(False)

        figure.tight_layout()
        figure.savefig(output)
        plt.close(figure)
        return Path(output)
