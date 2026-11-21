# rebuild v41

SAE `sae/commands/fdPDOS_XAS_av.py` の `FLAG_SP` / `FLAG_SPD` と `block_list` を参照し、軌道別PDOSのグループ表示を追加。

- `scripts/fdPDOS_XAS_av.py`: `--sp` と `--spd` を追加。元の `list4` と `list1` の軌道構成を使用する。
- `PlotFdmAverage.plot()`: `orbital_groups` によって複数軌道を一つのパネルに描画できるようにした。未指定時は従来の1軌道1パネルを維持。
- `tests/test_average_orbital_groups.py`: パネル数と重複グループの検出を検査。

未完了: SAEの完全な図配置、全28本の機能同等性、原本ヘッダの網羅的照合、全ファイルのdocstringとPEP 8/Black点検。
