# rebuild v32

- `AnalyzeFdmAverage` のXAS平均化経路に専用回帰テストを追加。
- 異なるXASエネルギー格子を拒否するテストを追加。
- NaN・無限大のスペクトル値、空のエネルギー軸、非一次元エネルギー軸を明示的に拒否する処理を追加。
- `COMMAND_AUDIT.md` の `fdMulti_2_XAS+LDOS+EXP.py` を、v31で追加済みのサンプルに合わせて修正。
- 新規のSAEスクリプト移植は今回なし。28本すべての完全再現は未達。

## 継続課題

SAEの未収録スクリプト3本（`FDfdm2vasp.py` とVASP変換のBUG版2本）、既存スクリプトの全オプション、SAE原本ヘッダの照合、全docstringの内容確認、Blackによる整形。
