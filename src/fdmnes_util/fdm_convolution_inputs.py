#!/usr/bin/env python3
# Original SAE source: FDmakeCconvAllsite.py
# SAE: K.NAKADA, kengo.nakada@gmail.com
# SAE: 2018.08.17 - Python2/3 両対応
# SAE: 2015.06.30 startup
"""生 XAS ``<Filout>_N.txt`` を参照する ``conv_N.inp`` と ``fdmfile.txt`` を生成する。

FdmConvolutionInputs は番号付きのスペクトルをファイル名順に探し、各サイトの畳み込み入力を SAE 由来の書式で組み立てる。
"""
from glob import escape
from os.path import relpath
from pathlib import Path
import re

from .fdmfile import Fdmfile


class FdmConvolutionInputs:
    """生 XAS ``<Filout>_N.txt`` を参照して、``conv_N.inp`` と ``fdmfile.txt`` を生成する。"""
    def write(self, filout, output_dir="."):
        """サイト別の畳み込み入力とジョブ一覧を生成する。

        生スペクトルは `<Filout>_<number>.txt` の名前を使う。畳み込み済みの結果や、番号以外が付いたファイルは対象外。

        Args:
            filout: ディレクトリを含められる出力ファイルの接頭辞。
            output_dir: 生成した入力を保存し、FDMNES を実行するディレクトリ。

        Returns:
            list[str]: 元のスペクトル名を辞書順に並べた順序での入力ファイル名。

        Raises:
            ValueError: Filout にファイル名の部分がない場合。
            OSError: 計算入力またはジョブ一覧を書き出せない場合。
        """
        prefix_path = Path(filout)
        source_directory = prefix_path.parent
        prefix_name = prefix_path.name
        if not prefix_name:
            raise ValueError("Filout must include a filename prefix")
        output_directory = Path(output_dir)
        output_directory.mkdir(parents=True, exist_ok=True)

        # SAE selects numbered site spectra in lexicographic filename order.
        spectrum_pattern = re.compile(re.escape(prefix_name) + r"_\d+\.txt")
        source_spectra = []
        for candidate in sorted(source_directory.glob(escape(prefix_name) + "_*.txt")):
            if candidate.is_file() and spectrum_pattern.fullmatch(candidate.name):
                source_spectra.append(candidate)

        input_names = []
        job_prefix = relpath(prefix_path, output_directory)
        for site_number, spectrum in enumerate(source_spectra, start=1):
            input_name = f"conv_{site_number}.inp"
            calculation_name = relpath(spectrum, output_directory)
            convolution_name = str(Path(calculation_name).with_suffix("")) + "_conv.txt"
            input_path = output_directory / input_name
            with input_path.open("w", encoding="utf-8") as convinp:
                print("", file=convinp)
                print(" Filout", file=convinp)
                print("   " + job_prefix, file=convinp)
                print("", file=convinp)
                print(" Calculation", file=convinp)
                print("   " + calculation_name, file=convinp)
                print("", file=convinp)
                print(" Conv_out", file=convinp)
                print("   " + convolution_name, file=convinp)
                print("", file=convinp)
                print(" Convolution", file=convinp)
                print("", file=convinp)
                print("END", file=convinp)
            input_names.append(input_name)

        job_list_path = output_directory / "fdmfile.txt"
        Fdmfile.write(input_names, job_list_path)
        return input_names
