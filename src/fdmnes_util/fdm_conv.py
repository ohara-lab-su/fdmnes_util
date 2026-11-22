"""畳み込み XAS の形式を選び、対応するリーダーに委譲する。"""

from pathlib import Path

from .fdm_conv_2016 import FdmConv2016
from .fdm_conv_2026 import FdmConv2026


class FdmConv:
    """畳み込み XAS の共通の入口。"""

    def __init__(self, filename, *, format_year=None):
        """2026年の改訂行で始まる出力を検出する。形式を明示指定することもできる。"""
        self.path = Path(filename)
        if format_year is None:
            format_year = 2016
            with self.path.open(encoding="utf-8", errors="replace") as stream:
                if stream.readline().strip() == FdmConv2026.REVISION_HEADER:
                    format_year = 2026
        if format_year == 2016:
            self._reader = FdmConv2016(self.path)
        elif format_year == 2026:
            self._reader = FdmConv2026(self.path)
        else:
            raise ValueError(f"Unverified convolution layout: {format_year}")

        self.format_year = format_year
        self.header = self._reader.header
        self.values = self._reader.values
        self.energy = self._reader.energy
        self.xas = self._reader.xas
        self.preamble = getattr(self._reader, "preamble", [])
        self.parameters = getattr(self._reader, "parameters", {})
        self.shifts = getattr(self._reader, "shifts", ())

    def select_reader(self):
        """選んだ年別リーダーを返す。"""
        return self._reader

    def get_eng(self):
        """出力のエネルギー軸を返す。"""
        return self._reader.get_eng()

    def get_xas(self, spin=0):
        """指定した吸収強度列を返す。"""
        return self._reader.get_xas(spin=spin)

    @staticmethod
    def write_spectrum(filename, spectrum):
        """平均スペクトルは共通の SAE 書式で保存する。"""
        return FdmConv2016.write_spectrum(filename, spectrum)
