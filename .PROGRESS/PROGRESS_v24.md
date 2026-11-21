# Rebuild v24

- SAE `FDconv_e2photoe.py` のヘッダとエネルギー変換を照合。
- `FdmPhotoenergy` の省略表記と不十分なdocstringを修正。原本の数値出力精度を維持。
- `AnalyzeFdmXas.photon_energy()` のdocstringを修正し、畳み込みデータ自身のエネルギー軸を使う理由を明記。
- `FDconv_e2photoe.py` にSAE由来コメントと原本の位置引数指定を追加。
- 異なる長さの生XAS/畳み込みXASを使った回帰テストを追加。
- `COMMAND_AUDIT.md` の `fdLDOSmulti.py` の矛盾した状態表示を修正。

未完了: 全28本の完全再現、原本ヘッダの全モジュール照合、全docstringの意味確認、Black整形。
