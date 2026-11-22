#!/usr/bin/env python3
"""FDMNES の計算入力 ``*.inp``・``fdmfile.txt`` と、生 XAS ``<Filout>.txt``・畳み込み XAS ``*_conv.txt``・BAV ``*_bav.txt``・SD ``*_sdN.txt`` を扱うライブラリ。

このモジュール自体はファイルを開かない。各形式の読み書き、実行管理、解析・描画はそれぞれのモジュールが担当する。
"""