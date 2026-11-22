#!/usr/bin/env python3
# SAE source: sae/commands/FDplot_XAS.py
# fmt: off
# ---- SAE original header ----
# Copyright Kengo NAKADA; SAE class library.
##########################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
#
#   *_conv.txt plot program
#    ファイル名自動判別を付け加えただけの基本的な XAS plot
#
#   fdXAS.py のゴージャス版
#   fdXAS は書き換えるのを前提としたスクリプト(小文字系)
#
#   Kエッジ版
#
#   SPIN 暫定対応版
#    ただし、read_pdb.inp と conv.inp 両対応を意識して、自動判別ではなく
#    -s もしくは --spin オプション時に強制的に対応させる
#    spin の計算で -s をつけていない時は up-spin の DOS を描く
#
#   Weight
#     もしPd19クラスター（つまりPd原子が19個)で、計算したサイトがall-siteで
#     4つならば(サイト内には同種の対称性の複数の原子を含む)
#
#     FDplot_xas.py -a 1 2 3 4 -w 19
#      とプロットすると、４つのサイトの平均値を19で割る(1原子あたり)に
#      変換した XANES をプロットする
#
#    このとき、DOS プロットも一緒にすると DOS のときはサイト情報は
#    そもそもが原子一個あたりなので（サイト内は一個の原子扱い）
#
#       FDplot_xas.py -d -x 4
#       とする(xはDOS weight)
#
#    両方時にプロットするには
#      FDplot_xas.py -a 1 2 3 4 -w 19 -d -x 4
#
##########################################################################
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.11.23
#  L2,L3 の計算に対応
#
# 2015.09.08
#  _0.txt _0_conv.txt _0_sd0.txt 出力系を追加・修正
#
# 2015.09.08
#  オプション、ファイル名取得系を整理整頓
#
# 2015.07.06
#   XAS の Weight と DOS の Weight を別に設定可能にした
#
# 2015.07.02
#  spin対応(DOSのプロットでupとdownの併記プロット)
#  その代わりに LDOS のプロットで p軌道のみ出力
#
# 2015.07.01
#  平均化ルーチンで重み(平均する際に割る数)を引数に追加したのを呼び出すように
#
# 2015.07.01
#   average モードで XAS だけではなく DOS も対応(ReadFdmSdの対応化)
#
# 2015.06.30
#   average モードを追加
#    filout 名 + _ + 数字 + _conv.txt
#    ファイルを複数読み込み平均化してプロットするモードを追加
#
# 2015.06.30
#   可変長オプションに変更
#   optparser() --> argparse()
#
# 2015.06.30
#   -i 指定で conv.inp を読み込んで 別途に計算した XAS conv を
#   プロットできるように修正
#
#   このとき、conv.inp ファイル中の conv_out 情報を取得して
#   プロットする名前を獲得できる
#
#   さらにDOS モードの時は
#     conv.inp 中の Filout から *_bav.txt 名を取得して情報を入手がかのう
#
#   つまり、Convolution 名とログファイル名の２つの名前を扱える
#
# 2015.06.24
#  実験データもプロット可能に
#        obs_file = filout+'_obs.txt.nor'
#
# 2015.06.23
#  DOSもプロット可能に
#
# 2015.06.19 FDplot_XAS startup
#
# 2015.05.21 fdXAS startup
#
##########################################################################
################################################################################
# ---- End of SAE original header ----
"""``*.inp`` または出力接頭辞から生 XAS ``<Filout>.txt`` と ``*_conv.txt`` を解決して描く。

オプションにより ``*_sdN.txt`` や実験の ``*.nor`` を読み、平均スペクトル・SD 表も保存できる。

計算入力を指定すると SAE のエネルギー基準と既定の重ね描きを使う。Filout を位置引数にすると単一のスペクトルをデータファイルから直接描ける。
"""
# fmt: on

import argparse
from pathlib import Path

from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage
from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.athena_nor import AthenaNor
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.fdm_txt import FdmTxt
from fdmnes_util.fdmfile import Fdmfile
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
__copyright__ = "Copyright 2015, Kengo NAKADA"
__license__ = "MIT"


class XasPlotSample:
    """``*.inp`` または出力接頭辞から生 XAS ``<Filout>.txt``・``*_conv.txt``・``*_sdN.txt`` を選び、平均や図の生成につなぐ。"""
    def run(self, argv=None):
        """計算・実測スペクトルを読み、SAE の比較図を描く。

        Args:
            argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

        Returns:
            pathlib.Path: 保存したファイルのパス。
        """
        parser = argparse.ArgumentParser(description="Plot FDMNES XAS")
        parser.add_argument(
            "prefix",
            nargs="?",
            help="Plot directly from a Filout prefix",
        )
        parser.add_argument("-i", "--inp", "--inpname", dest="input_file")
        parser.add_argument("-f", "--filout", "--filoutname")
        parser.add_argument("-c", "--conv", "--convolution")
        parser.add_argument("-t", "--txt", "--textname")
        parser.add_argument("-s", "--sd", "--sdname")
        parser.add_argument("--filbav", "--bavname", dest="bav")
        parser.add_argument("--name", help="Common prefix for the calculation outputs")
        parser.add_argument("-o", dest="short_o", help="SAE Athena overlay path")
        parser.add_argument("--obs", help="Athena overlay file")
        parser.add_argument("--output", help="Figure path or SAE output prefix")
        parser.add_argument("-a", "--absorber", nargs="*", type=int)
        parser.add_argument("-w", "--weight", type=float)
        parser.add_argument("-x", "--dosweight", type=float)
        parser.add_argument("--year", type=int, choices=(2016, 2020))
        parser.add_argument("-b", "--broad", action="store_true")
        parser.add_argument("-d", "--dos", action="store_true")
        parser.add_argument("-n", "--nonsubtract", action="store_true")
        parser.add_argument("--dn", "--down", action="store_true")
        for flag in ("xas", "fermi", "l2", "l3", "l23", "up", "spin", "pdf", "nw"):
            parser.add_argument(f"--{flag}", action="store_true")
        for limit in ("emin", "emax", "ymax", "dmax"):
            parser.add_argument(f"--{limit}", type=float)
        options = parser.parse_args(argv)

        input_file = None
        if (
            options.input_file is not None
            or options.prefix is None
            or options.fermi
            or options.dos
        ):
            input_file = FdmInp(Fdmfile.select_input(options.input_file))

        filout = options.filout or options.prefix
        if filout is None and input_file is not None:
            calculation = input_file.get_calculation()
            filout = calculation.removesuffix(".txt") or input_file.get_filout()
        if not filout and not options.name:
            parser.error("Specify a Filout prefix or an input containing Filout")
        sites = options.absorber or []
        if any(site < 1 for site in sites) or len(set(sites)) != len(sites):
            parser.error("Select distinct positive absorbing-site indices")

        raw_name = options.name or options.txt or filout
        conv_name = options.name or options.conv or filout
        if input_file is not None and not (options.name or options.conv):
            conv_name = input_file.get_conv_out() or conv_name
        correct_energy = input_file is not None and not options.nonsubtract
        show_raw = options.xas or not options.broad
        show_convolved = not options.xas and (options.broad or input_file is not None)

        raw_readers = []
        if show_raw or correct_energy or sites:
            raw_readers = [
                FdmTxt(path) for path in self._spectrum_paths(raw_name, ".txt", sites)
            ]
        convolved_readers = []
        if show_convolved or sites:
            convolved_readers = [
                FdmConv(path)
                for path in self._spectrum_paths(conv_name, "_conv.txt", sites)
            ]

        raw = None
        if raw_readers:
            raw = raw_readers[0]
        average = AnalyzeFdmAverage()
        raw_curves = []
        if show_raw or sites:
            raw_curves = self._raw_curves(average, raw_readers, options)
        convolved_curve = None
        if convolved_readers:
            grid, intensity = average.average(
                convolved_readers, "get_xas", divisor=options.weight
            )
            convolved_curve = (grid, intensity, "XAS broad")

        spectra = []
        if show_raw:
            spectra.extend(raw_curves)
        if show_convolved:
            spectra.append(convolved_curve)
        if correct_energy:
            spectra = self._shift_curves(spectra, input_file, raw, options.fermi)

        xlabel = "Energy (eV)"
        fermi_position = None
        if correct_energy:
            if options.fermi:
                xlabel = "Energy above Fermi [eV]"
                fermi_position = 0.0
            else:
                xlabel = "Photon Energy [eV]"
                fermi_position = raw.get_eedge() + raw.get_efermi()

        dos = []
        if options.dos:
            dos = self._dos_curves(average, options, input_file, filout, raw)
        if sites:
            FdmTxt.write_spectrum(f"{filout}_0.txt", raw.metadata, raw_curves[0][:2])
            FdmConv.write_spectrum(f"{filout}_0_conv.txt", convolved_curve[:2])

        observed_path = options.obs
        output = options.output
        if options.short_o:
            # Older examples used -o for an explicit image filename.
            if Path(options.short_o).suffix.lower() in (".pdf", ".png", ".eps"):
                output = output or options.short_o
            else:
                observed_path = observed_path or options.short_o
        observed = None
        if observed_path:
            path = Path(observed_path)
            if not path.is_file():
                path = Path(f"{filout}_obs.txt.nor")
            experiment = AthenaNor(path)
            observed = (experiment.get_eng(), experiment.get_nor(), "obs.")

        if output is None:
            output = "XAS"
            if options.name:
                output += f"_{Path(options.name).name}"
            output += ".pdf"
        elif Path(output).suffix.lower() not in (".pdf", ".eps", ".png"):
            output += "_"
            if options.name:
                output += f"_{Path(options.name).name}"
            output += ".pdf"

        plotter = PlotFdmXas()
        if input_file is None and observed is None and not (sites or options.pdf):
            return plotter.plot(
                spectra,
                output,
                xlabel=xlabel,
                xmin=options.emin,
                xmax=options.emax,
                ymax=options.ymax,
            )
        return plotter.plot_composite(
            spectra,
            output,
            observed=observed,
            dos=dos,
            xlabel=xlabel,
            xmin=options.emin,
            xmax=options.emax,
            ymax=options.ymax,
            dmax=options.dmax,
            fermi_position=fermi_position,
            extra_formats=options.pdf,
            show=not options.nw,
        )

    @staticmethod
    def _spectrum_paths(prefix, suffix, sites):
        """選んだ計算の生 XAS または畳み込み XAS のパスを組み立てる。

        Args:
            prefix: スペクトルの接頭辞またはファイル名。
            suffix: スペクトルの種類を識別するファイル名の接尾辞。
            sites: 平均する場合に選ぶ1始まりの吸収サイト番号。

        Returns:
            list[str]: サイト順の入力ファイル名。
        """
        stem = prefix.removesuffix(suffix)
        if sites:
            return [f"{stem}_{site}{suffix}" for site in sites]
        if prefix.endswith(".txt"):
            return [prefix]
        return [stem + suffix]

    @staticmethod
    def _raw_curves(average, readers, options):
        """吸収端とスピンで列を選択し、平均を取る。

        Args:
            average: 格子の検証と強度の平均を担当する解析クラス。
            readers: 読み取りに使うリーダーの並び。
            options: オプション解析で得た Namespace。

        Returns:
            list[tuple]: 生 XAS の各曲線のエネルギー格子、強度、ラベル。
        """
        spins = [0]
        if options.dn and not options.up:
            spins = [1]
        elif options.spin and not options.up and readers[0].get_xas_all().shape[1] > 1:
            spins = [0, 1]
        edges = []
        if options.l2 or options.l23:
            edges.append("L2")
        if options.l3 or options.l23:
            edges.append("L3")

        curves = []
        for spin in spins:
            suffix = ""
            if options.spin or options.up or options.dn:
                suffix = (" up", " down")[spin]
            if edges:
                for edge in edges:
                    grid, values = average.average(
                        readers,
                        "get_edge_xas",
                        edge=edge,
                        spin=spin,
                        divisor=options.weight,
                    )
                    curves.append((grid, values, f"XAS ({edge}{suffix})"))
            else:
                grid, values = average.average(
                    readers, "get_xas", spin=spin, divisor=options.weight
                )
                curves.append((grid, values, "XAS" + suffix))
        return curves

    def _dos_curves(self, average, options, input_file, filout, raw):
        """SD のエネルギー格子上でサイトの s・p 軌道の LDOS を読み込むか、平均する。

        Args:
            average: 格子の検証と強度の平均を担当する解析クラス。
            options: オプション解析で得た Namespace。
            input_file: 計算条件とエネルギー基準を読む FdmInp。
            filout: ディレクトリを含められる出力ファイルの接頭辞。
            raw: 吸収端とフェルミエネルギーを保持する生 XAS リーダー。

        Returns:
            list[tuple]: LDOS 曲線ごとのエネルギー格子、密度配列、ラベル。
        """
        prefix = options.name or options.sd or filout
        ispin = input_file.get_ispin()
        if options.spin or options.dn:
            ispin = 2
        readers = [
            FdmSd(path, format_year=options.year, ispin=ispin).select_reader()
            for path in self._spectrum_paths(prefix, "_sd0.txt", options.absorber)
        ]

        spins = [0]
        if options.dn and not options.up:
            spins = [1]
        elif options.spin and not options.up:
            spins = [0, 1]
        orbitals = ["s", "p"]
        if options.spin:
            orbitals = ["p"]
        divisor = options.dosweight
        if divisor is None and options.absorber:
            divisor = options.weight

        curves = []
        for orbital in orbitals:
            for spin in spins:
                grid, density = average.average(
                    readers, "get_ldos", l=orbital, spin=spin, divisor=divisor
                )
                label = f"absorber-LDOS({orbital})"
                if options.spin or options.dn or options.up:
                    label += (" up", " down")[spin]
                curves.append((grid, density, label))
        if options.absorber:
            columns = getattr(readers[0], "columns", None)
            if columns is None:
                columns = readers[0].header
            for reader in readers[1:]:
                names = getattr(reader, "columns", None)
                if names is None:
                    names = reader.header
                if names != columns:
                    raise ValueError("SD column labels differ between absorbing sites")
            grid, densities = average.average(readers, "get_densities", divisor=divisor)
            FdmSd.write_table(f"{filout}_0_sd0.txt", columns, grid, densities)
        if not options.nonsubtract:
            curves = self._shift_curves(curves, input_file, raw, options.fermi)
        return curves

    @staticmethod
    def _shift_curves(curves, input_file, raw, fermi):
        """計算 XAS のメタデータに基づいて各曲線のエネルギー格子を移動する。

        Args:
            curves: エネルギー、強度、ラベルの組の並び。
            input_file: 計算条件とエネルギー基準を読む FdmInp。
            raw: 吸収端とフェルミエネルギーを保持する生 XAS リーダー。
            fermi: True の場合はフェルミ準位基準、False の場合は光子エネルギー基準。

        Returns:
            list[tuple]: 指定されたエネルギー基準での曲線の並び。
        """
        shifted = []
        for grid, intensity, label in curves:
            energy = AnalyzeFdmXas.energy_reference(
                grid, raw, input_is_photon=input_file.get_energygpho(), fermi=fermi
            )
            shifted.append((energy, intensity, label))
        return shifted


def main(argv=None):
    return XasPlotSample().run(argv)


if __name__ == "__main__":
    main()
