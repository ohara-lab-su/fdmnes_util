#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/fdmfile.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*-
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
# *.txt ファイル
#
###############################################################################
#
# 2018.08.15
#  Python2/3 両対応
#
# 2015.11.12 startup
#
###############################################################################
# トップディレクトリ関係のエラーは ImportError ではキャッチ出来ない
###############################################################################
# import gzip
# import optparse
# import numpy as np
# sys.path.append('../..')
# import SpaceGroupEnvironment as SGE
###############################################################################
###############################################################################
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""Read the FDMNES ``fdmfile.txt`` list of calculation inputs."""

from pathlib import Path


class Fdmfile:
    """Read the filenames contained in an FDMNES batch list."""

    def __init__(self, filename="fdmfile.txt"):
        """Load the batch list.

        Args:
            filename: Path to ``fdmfile.txt``.

        Raises:
            ValueError: If the list is empty or incomplete.
        """
        self.path = Path(filename)
        lines = []
        for line in self.path.read_text().splitlines():
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
        if not lines:
            raise ValueError("Empty fdmfile.txt")
        count = int(lines[0])
        self.filenames = lines[1 : 1 + count]
        if len(self.filenames) != count:
            raise ValueError("Incomplete fdmfile.txt")

    def get_filout(self):
        """Return the first calculation filename, or an empty string."""
        if self.filenames:
            return self.filenames[0]
        return ""

    @staticmethod
    def write(filenames, filename="fdmfile.txt"):
        """Write the job count and each input filename.

        Args:
            filenames: Iterable of FDMNES input filenames.
            filename: Destination path for the job-list file.

        Returns:
            Path: Path of the generated job-list file.
        """
        input_names = list(filenames)
        output_path = Path(filename)
        output_lines = ["", str(len(input_names))]

        for input_name in input_names:
            output_lines.append(str(input_name))

        output_text = "\n".join(output_lines) + "\n"
        output_path.write_text(output_text, encoding="utf-8")
        return output_path
