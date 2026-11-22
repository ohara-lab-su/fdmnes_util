#!/usr/bin/env python3
"""生 XAS ``<Filout>.txt`` と畳み込み XAS ``*_conv.txt`` を使う数値解析。

AnalyzeFdmXas は対応するリーダーや数値配列から平均とエネルギー軸変換を行う。全サイト処理では ``<Filout>_N.txt`` または ``<Filout>_N_conv.txt`` をリーダー経由で読み、サイト順の配列を返す。
"""
from pathlib import Path

import numpy as np

from .fdm_conv import FdmConv
from .fdm_txt import FdmTxt


class AnalyzeFdmXas:
    """生 XAS ``<Filout>.txt`` と畳み込み XAS ``*_conv.txt`` のリーダーを使い、スペクトルを数値解析する。"""
    @staticmethod
    def average(spectra, weights=None):
        """各スペクトルの先頭の吸収強度列を平均する。

        Args:
            spectra: 同じエネルギー格子でサンプリングされたスペクトルの並び。
            weights: スペクトルごとの相対重み。省略時は等重み。

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: 共通のエネルギー格子と平均 XAS。

        Raises:
            ValueError: スペクトルが空、格子が異なる、または重みが不正な場合。
        """
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

        if weights.shape != (len(spectra),) or not np.all(np.isfinite(weights)):
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
        """畳み込み XAS のエネルギー軸を光子エネルギーに変換する。

        エネルギーと吸収強度は畳み込みファイルの同じ行から取得する。生 XAS とはエネルギー格子が異なる場合がある。

        Args:
            convolution: 畳み込み出力を保持する FdmConv。
            raw_xas: 対応する生 XAS と吸収端・フェルミエネルギーを保持する FdmTxt。
            subtract_fermi: True の場合はフェルミエネルギーを引く。
            fermi_energy: エネルギー軸の基準に対応するフェルミエネルギー（eV）。

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: 変換後のエネルギーと XAS 強度。

        Raises:
            ValueError: 必要な吸収端またはフェルミエネルギーの記録がない場合。
        """
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
        """畳み込み XAS のエネルギー軸をフェルミ準位基準に変換する。

        SAE の `fdXAS_specified.py` に従い、`*_conv.txt` のエネルギー列からフェルミエネルギーだけを引く。

        Args:
            convolution: 畳み込み出力を保持する FdmConv。
            raw_xas: 対応する生 XAS と吸収端・フェルミエネルギーを保持する FdmTxt。

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: 元の行順でのフェルミ準位基準エネルギーと吸収強度。
        """
        energy = convolution.get_eng().copy()
        intensity = convolution.get_xas().copy()
        fermi_energy = raw_xas.get_efermi()
        energy -= fermi_energy
        return energy, intensity

    @staticmethod
    def energy_reference(energy, raw_xas, *, input_is_photon, fermi):
        """SAE の FDplot_XASs が使うエネルギー軸変換を行う。

        光子エネルギー指定がない計算の軸は吸収端基準。-f 指定時はフェルミ準位基準に変換する。計算軸が光子エネルギーの場合は E_edge と E_Fermi の両方を引く。

        Args:
            energy: エネルギー値の配列（eV）。
            raw_xas: 対応する生 XAS と吸収端・フェルミエネルギーを保持する FdmTxt。
            input_is_photon: 計算入力で Energpho を指定しているか。
            fermi: True の場合はフェルミ準位基準、False の場合は光子エネルギー基準。

        Returns:
            numpy.ndarray: 指定の基準に変換したエネルギー格子（eV）。

        Raises:
            ValueError: 生 XAS の見出しに吸収端エネルギーがない場合。
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
        """全サイト計算の出力を指定サイト順に読み込む。

        軸を変換する場合は input_is_photon と fermi を両方指定する。両方を省略するとファイルの軸を使う。

        Args:
            base_name: ディレクトリを含められる Filout 接頭辞。
            site_indices: 描画順に並べた1始まりの吸収サイト番号。
            convolved: True の場合は畳み込み、False の場合は生のサイトスペクトルを読む。
            input_is_photon: 計算入力で Energpho を指定しているか。
            fermi: True の場合はフェルミ準位基準、False の場合は光子エネルギー基準。

        Returns:
            list[tuple]: エネルギー、強度、サイトラベルの組のリスト。

        Raises:
            ValueError: サイト番号またはエネルギー基準の指定が不正な場合。
            OSError: 指定のスペクトルを開けない場合。
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
            raw_path = Path(f"{prefix}.txt")
            if convolved:
                output_path = Path(f"{prefix}_conv.txt")
                reader = FdmConv(output_path)
            else:
                reader = FdmTxt(raw_path)

            energy = reader.get_eng()
            intensity = reader.get_xas().copy()

            if input_is_photon is None:
                energy = energy.copy()
            else:
                if convolved:
                    raw_xas = FdmTxt(raw_path)
                else:
                    # 生スペクトルでは同じ reader が強度と吸収端を保持している。
                    raw_xas = reader
                energy = cls.energy_reference(
                    energy,
                    raw_xas,
                    input_is_photon=input_is_photon,
                    fermi=fermi,
                )

            label = f"absorber={index}"
            result.append((energy, intensity, label))

        return result
