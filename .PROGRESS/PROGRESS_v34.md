# rebuild v34

SAE `fdPDOS_XAS_av.py` の `--dmax` (DOS上限) と `--ymax` (XAS上限) を編集可能なサンプルと `PlotFdmAverage` に追加。両軸の上限を独立に設定する。非正の上限値は拒否する。

サンプル冒頭の開発履歴は `sae(1).zip` の `sae/commands/fdPDOS_XAS_av.py` から原文をコメントとして収録した。元コードにあるバグや未移植オプションの存在を消していない。

`fdmnes_util install script` と `pyproject.toml` の構成は維持。全28本の機能再現、全クラスの履歴コメント照合、Black整形は未完了。
