# Rebuild v7 — plotパッケージの整理とXAS/LDOSの複合表示

- `plot_fdm_xas.py`、`plot_fdm_dos.py` を `src/fdmnes_util/plot/` に移動し、`commands/` と並列配置しました。
- 参照しているCLI・テストのimportを更新しました。旧パスを残す互換モジュールは作っていません。
- `PlotFdmDos` の一行分岐、三項演算子、セミコロン区切りの処理を展開しました。
- `PlotFdmXasLdos` と `FDplot_XAS_LDOS` CLIを追加しました。XASとサイト別LDOSの積み重ね描画を再現しています。
- 元の`FDplot_XAS_LDOS.py`にはエネルギー軸変換の未代入式があるため、既存の`AnalyzeFdmXas.energy_reference()`に明示して軸変換を実行しています。
- SD形式の自動推測は行わず、現時点では `--year 2016|2020` を必須にしています。2022形式は未確認です。
- このCLIは原本の全オプション・表示仕様の同等性を確認したものではなく、部分実装です。
