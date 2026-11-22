#!/usr/bin/env python3
"""Input and option handling shared by the editable LDOS and PDOS samples."""

import argparse
from pathlib import Path

from .analyze_fdm_average import AnalyzeFdmAverage
from .fdm_conv import FdmConv
from .fdm_inp import FdmInp
from .fdm_sd import FdmSd
from .fdm_txt import FdmTxt
from .fdmfile import Fdmfile


class DosPlotSample:
    """LDOS・PDOS サンプルのコマンド入力と描画データを組み立てる。"""

    def __init__(self, *, projected, shade_occupied=False):
        """軌道の描画方法と占有領域の塗り分けを指定する。

        Args:
            projected: True のとき磁気量子数ごとの PDOS を描く。
            shade_occupied: フェルミ準位より下の LDOS を塗り分ける。
        """
        self._projected = projected
        self._shade_occupied = shade_occupied
        self._kind = "LDOS"
        if projected:
            self._kind = "PDOS"

    def build_parser(self):
        """Build the shared SAE option parser for a DOS sample.

        Returns:
            argparse.ArgumentParser: Parser with the original option spellings.
        """
        parser = argparse.ArgumentParser(description=f"Plot FDMNES {self._kind}")
        parser.add_argument(
            "source",
            nargs="?",
            help="FDMNES input or direct SD text file",
        )
        parser.add_argument("-i", "--inp", "--inpname", dest="input_file")
        parser.add_argument("-f", "--filout", "--filoutname")
        parser.add_argument("-c", "--conv", "--convname")
        parser.add_argument("-t", "--txt", "--txtname")
        parser.add_argument("-s", "--sd", "--sdname")
        parser.add_argument("--filbav", "--bavname", dest="bav")
        parser.add_argument("--name")
        parser.add_argument("-o", "--output", "--head")
        parser.add_argument("--label")
        parser.add_argument("--outsuffix", default="")
        parser.add_argument("-a", "--atom", type=int)
        parser.add_argument("--year", type=int, choices=(2016, 2020))
        for name in (
            "emin",
            "emax",
            "ymax",
            "dmax",
            "weight",
            "xasweight",
            "txtweight",
            "dosweight",
        ):
            parser.add_argument(f"--{name}", type=float)
        parser.add_argument("-b", "--broad", action="store_true")
        parser.add_argument("-x", "--xas", action="store_true")
        for name in (
            "total",
            "intdos",
            "fermi",
            "s",
            "p",
            "sp",
            "spd",
            "up",
            "spin",
            "pdf",
            "nw",
        ):
            parser.add_argument(f"--{name}", action="store_true")
        parser.add_argument("--dn", "--down", action="store_true")
        if not self._projected:
            parser.add_argument("--d", action="store_true")
            parser.add_argument("--spdf", action="store_true")
            for orbital in "spdf":
                parser.add_argument(f"--dmax_{orbital}", type=float)
        return parser

    def plot(self, plotter, options):
        """Resolve a DOS sample's files and pass its data to the composite renderer.

        Args:
            plotter: PlotFdmDos instance used for figure generation.
            options: Namespace returned by build_parser.

        Returns:
            pathlib.Path: Main figure path.

        Raises:
            ValueError: If a requested spin or file format cannot be used.
        """
        input_path = options.source or options.input_file
        if (
            options.source
            and options.input_file is None
            and self._is_sd_table(options.source)
        ):
            reader = FdmSd(options.source, format_year=options.year).select_reader()
            output = options.output or f"{self._kind}.pdf"
            return plotter.plot(reader, output, integrated=options.intdos)

        input_file = FdmInp(Fdmfile.select_input(input_path))
        prefix = options.filout or input_file.get_filout()
        atom = options.atom
        if atom is None:
            atom = int(input_file.get_nonexc())
        sd_suffix = f"_sd{atom}.txt"
        sd_name = options.name or options.sd or prefix
        if not sd_name.endswith(".txt"):
            sd_name += sd_suffix
        ispin = input_file.get_ispin()
        if options.spin or options.dn:
            ispin = 2
        reader = FdmSd(
            sd_name, format_year=options.year, ispin=ispin, weight=options.dosweight
        ).select_reader()
        spins = (0,)
        spin_labels = ("", "")
        spin_suffix = ""
        if options.up:
            spin_labels = ("_up", "")
            spin_suffix = "_up"
        elif options.dn:
            spins = (1,)
            spin_labels = ("", "_dn")
            spin_suffix = "_dn"
        elif ispin == 2:
            spins = (1, 0)
            spin_labels = ("_up", "_dn")
            spin_suffix = "_spin"
        if max(spins) >= reader.get_ispin():
            raise ValueError("The selected SD layout has no requested spin channel")

        available = "spdf"
        if self._projected:
            available = "spd"
        available = available[: reader.get_lmax() + 1]
        orbitals = available
        for selection in ("s", "p", "d", "sp", "spd", "spdf"):
            if getattr(options, selection, False):
                orbitals = selection
        if any(orbital not in available for orbital in orbitals):
            raise ValueError("The requested orbital group is absent from the SD file")

        groups = []
        if options.total:
            groups.append(("total",))
        if self._projected:
            orbit_groups = {
                "s": [("s",)],
                "p": [("p_y", "p_z", "p_x")],
                "d": [("d_xy", "d_yz", "d_3z2-r2", "d_xz", "d_x2-y2")],
            }
            # In the SAE s/p layout p_z is drawn separately from p_x and p_y.
            if orbitals == "sp":
                orbit_groups["p"] = [("p_z",), ("p_y", "p_x")]
            for orbital in reversed(orbitals):
                groups.extend(reversed(orbit_groups[orbital]))
        else:
            groups.extend((orbital,) for orbital in orbitals)

        raw_name = options.name or options.txt or prefix
        raw = FdmTxt(raw_name.removesuffix(".txt") + ".txt")
        shift, fermi_position = AnalyzeFdmAverage().energy_reference(
            input_file, raw, options.fermi
        )
        xlabel = "Photon Energy [eV]"
        fermi_suffix = ""
        if options.fermi:
            fermi_position = 0.0
            xlabel = "Energy above Fermi [eV]"
            fermi_suffix = "_fermi"

        xas = []
        if options.xas or options.broad:
            conv_name = options.name or options.conv or prefix
            conv_name = conv_name.removesuffix("_conv.txt") + "_conv.txt"
            conv = FdmConv(conv_name)
            conv_weight = options.weight
            if conv_weight is None:
                conv_weight = options.xasweight
            raw_weight = options.weight
            if raw_weight is None:
                raw_weight = options.txtweight
            xas.append(
                (
                    conv.get_eng() + shift,
                    self._divide(conv.get_xas(), conv_weight),
                    "XAS (with broadening)",
                )
            )
            if options.broad:
                for spin in spins:
                    xas.append(
                        (
                            raw.get_eng() + shift,
                            self._divide(raw.get_xas(spin), raw_weight),
                            "XAS" + spin_labels[spin],
                        )
                    )

        output = Path(
            f"{self._kind}{atom}{options.outsuffix}{spin_suffix}{fermi_suffix}.pdf"
        )
        if options.output:
            output = Path(options.output)
            if output.suffix.lower() not in (".pdf", ".eps", ".png"):
                output = Path(
                    f"{output}_{atom}{options.outsuffix}{spin_suffix}{fermi_suffix}.pdf"
                )
        orbital_max = {}
        for orbital in "spdf":
            maximum = getattr(options, f"dmax_{orbital}", None)
            if maximum is not None:
                orbital_max[orbital] = maximum

        # SAE PDOS parses --intdos but draws component projections only. The
        # 2020 format has group integrals, with no per-component integral columns.
        return plotter.plot_composite(
            reader,
            output,
            groups=groups,
            spins=spins,
            spin_labels=spin_labels,
            projected=self._projected,
            integrated=options.intdos and not self._projected,
            xas=xas,
            shift=shift,
            fermi_position=fermi_position,
            xlabel=xlabel,
            limits=(options.emin, options.emax),
            density_max=options.dmax,
            orbital_max=orbital_max,
            xas_max=options.ymax,
            label=options.label or str(atom),
            extra_formats=options.pdf,
            show=not options.nw,
            shade_occupied=self._shade_occupied,
        )

    @staticmethod
    def _divide(values, weight):
        """Apply the SAE intensity divisor while preserving the energy grid.

        Args:
            values: Spectrum intensity array.
            weight: Positive divisor, or None to leave the intensity unchanged.

        Returns:
            numpy.ndarray: Scaled intensities.

        Raises:
            ValueError: If the divisor is nonpositive or nonfinite.
        """
        from math import isfinite

        if weight is None:
            return values
        if not isfinite(weight) or weight <= 0:
            raise ValueError("Intensity weight must be a positive finite divisor")
        return values / weight

    @staticmethod
    def _is_sd_table(filename):
        """Distinguish an SD table from a positional SAE input ending in .txt.

        Args:
            filename: Path provided as the first positional argument.

        Returns:
            bool: True when the first record is an SD energy header.
        """
        with Path(filename).open(encoding="utf-8", errors="replace") as stream:
            header = stream.readline().lower().split()
        return bool(header and header[0] in ("e", "energy"))
