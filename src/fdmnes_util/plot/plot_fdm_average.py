#!/usr/bin/env python3
"""Plot averaged orbital-resolved DOS and optional XAS.

SAE source: ``sae/commands/fdPDOS_XAS_av.py``. The original program
uses a portrait layout with orbital blocks and an optional XAS panel.
"""

from . import _PlotFigure


class PlotFdmAverage(_PlotFigure):
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
        energy_offset=0.0,
        orbital_groups=None,
        fermi_position=None,
        xlabel="Photon Energy [eV]",
        extra_formats=False,
        show=False,
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
            energy_offset: Energy shift in eV applied to every plotted curve.
            orbital_groups: Optional orbital-name groups. Each group is
                plotted in one panel, following the SAE orbital block layout.
            fermi_position: Fermi level in the displayed energy reference, in eV.
            xlabel: Label for the displayed energy reference.
            extra_formats: Save the same figure in PDF, EPS, and PNG.
            show: Display the saved figure.

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

        import numpy as np

        if not np.isfinite(energy_offset):
            raise ValueError("energy_offset must be finite")

        import matplotlib.pyplot as plt

        # The original SAE figure groups orbital curves into three panels.
        # Keep the ungrouped behavior for callers that do not select a mode.
        panels = []
        if orbital_groups is None:
            for curve in orbital_data:
                panels.append([curve])
        else:
            used_orbitals = set()
            for group in orbital_groups:
                panel_curves = []
                for orbital in group:
                    if orbital in used_orbitals:
                        raise ValueError("Orbital groups must not overlap")
                    used_orbitals.add(orbital)
                    for curve in orbital_data:
                        label = curve[0]
                        if label.endswith("-" + orbital):
                            panel_curves.append(curve)
                if panel_curves:
                    panels.append(panel_curves)
            if not panels:
                raise ValueError("No orbital data match the selected groups")

        panel_count = len(panels)
        if xas_data is not None:
            panel_count += 1

        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 15
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 10
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.4
            figure = plt.figure(figsize=(7.0, 9.89))
            orgx = 0.17
            orgy = 0.08
            off = 0.016
            xsize = 0.75
            ysize0 = 0.81
            ysize = ysize0 / panel_count
            num = 0
            if xas_data is not None:
                plt.axes([orgx, orgy, xsize, ysize])
                engx, xas = xas_data
                plt.plot(
                    np.asarray(engx) + energy_offset,
                    xas,
                    linewidth=2,
                    color="black",
                    label="XAS (with broadening)",
                )
                if raw_xas_data is not None:
                    eng_p, dos_p = raw_xas_data
                    color = plt.cm.prism((num + 1) * 10)
                    plt.plot(
                        np.asarray(eng_p) + energy_offset,
                        dos_p,
                        linewidth=1,
                        color=color,
                        label="XAS",
                    )
                plt.ticklabel_format(axis="x", useOffset=False)
                if fermi_position is not None:
                    plt.axvline(x=fermi_position, color="black", linewidth=1)
                plt.xlim(xmax=emax, xmin=emin)
                plt.ylim(ymin=0, ymax=ymax)
                leg = plt.legend(loc="lower right")
                leg.get_frame().set_alpha(0.5)
                plt.xlabel(xlabel)
                plt.ylabel("Absorption [arb. unit]")
                orgy = orgy + ysize + off
            for index, panel_curves in enumerate(reversed(panels)):
                plt.axes([orgx, orgy, xsize, ysize])
                for label, energy, density in panel_curves:
                    num += 1
                    color = plt.cm.prism((num + 1) * 10)
                    plt.plot(
                        np.asarray(energy) + energy_offset,
                        density,
                        linewidth=2,
                        color=color,
                        label=label,
                    )
                plt.ticklabel_format(axis="x", useOffset=False)
                if fermi_position is not None:
                    plt.axvline(x=fermi_position, color="black", linewidth=1)
                plt.xlim(xmax=emax, xmin=emin)
                plt.ylim(ymin=0, ymax=dmax)
                leg = plt.legend(loc="upper right")
                leg.get_frame().set_alpha(0.5)
                if index == min(1, len(panels) - 1):
                    plt.ylabel("DOS [state/eV]")
                if index == 0 and xas_data is None:
                    plt.xlabel(xlabel)
                else:
                    plt.xticks([])
                orgy = orgy + ysize + off
            return self._save_figure(figure, output, extra_formats=extra_formats, show=show)
