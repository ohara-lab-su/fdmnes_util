# rebuild v39

- `PlotFdmAverage.plot()` に `energy_offset` を追加。PDOS、畳み込みXAS、未畳み込みXASに同じエネルギーシフトを適用する。
- 編集可能な `fdPDOS_XAS_av.py` に `--energy-offset` を追加。
- 原本の `--fermi` の完全再現ではない。原本は FDMNES のエネルギーモードに応じて `E_edge`、`E_Fermi` を参照する。
- 軸の一致を検証する回帰テストを追加。
- 残作業：SAE原本の全オプション・全描画仕様の再現、全ファイルのdocstring・コメント・Black監査。
