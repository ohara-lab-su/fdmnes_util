"""FDMNES 2026年11月5日版の Header 付き畳み込み出力 ``*_conv.txt`` を読む。

FdmConv2026 は吸収列とともに、見出しにある改訂情報、吸収端、畳み込み条件、シフトを保持する。
"""
from pathlib import Path

import numpy as np

from .fdm_conv_2016 import FdmConv2016


class FdmConv2026:
    """FDMNES の出力 `*_conv.txt` を2026年形式で読み、改訂情報と畳み込み条件を保持する。"""
    REVISION_HEADER = "# FDMNES program, Revision 5th of November 2026"

    def __init__(self, filename):
        """コメント形式の改訂行と畳み込み条件を読み、その後の数値列を取得する。"""
        self.path = Path(filename)
        with self.path.open(encoding="utf-8", errors="replace") as stream:
            self.preamble = []
            self.parameters = {}
            self.shifts = ()
            line = stream.readline().strip()
            # Header が出力するコメント行の直後に、従来と同じ数値列の見出しがある。
            while line.startswith("#"):
                self.preamble.append(line)
                values, _, field = line[1:].partition("=")
                field = field.strip()
                if field.startswith("E_edge,"):
                    names = [name.strip() for name in field.split(",")]
                    self.parameters.update(zip(names, map(float, values.split())))
                elif field == "Shifts":
                    self.shifts = tuple(map(float, values.split()))
                line = stream.readline().strip()
            self.header = line
            self.values = np.loadtxt(stream, ndmin=2)

        if len(self.values) == 0 or self.values.shape[1] < 2:
            raise ValueError("FDMNES convolution output requires an XAS column")
        self.energy = self.values[:, 0]
        self.xas = self.values[:, 1:]

    def get_eng(self):
        """ファイルで定義された基準のエネルギー軸を返す。"""
        return self.energy

    def get_xas(self, spin=0):
        """指定した吸収強度列を返す。

        Args:
            spin: 0始まりの吸収強度列の番号。

        Returns:
            numpy.ndarray: 吸収強度の配列。
        """
        return self.xas[:, spin]

    @staticmethod
    def write_spectrum(filename, spectrum):
        """平均スペクトルは共通の SAE 書式で保存する。"""
        return FdmConv2016.write_spectrum(filename, spectrum)
