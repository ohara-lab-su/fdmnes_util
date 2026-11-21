# rebuild v20

- SAE `FDpbd2fdm.py` を参照し、`Pdb` クラスと編集可能な `FDpbd2fdm.py` を追加。
- `CRYST1` の有無で結晶・分子を区別し、座標読み込みは原本と同じくASEに委譲。
- 分子はCartesian座標、結晶は格子とfractional座標を出力。
- `pyproject.toml` の `structure` オプションにASEを追加。`setup.py` は使用しない。
- 元スクリプトの標準出力への構造表示、出力名などは完全再現していない。
- SAEの28スクリプト全機能の再現と全ファイルの可読性監査は継続課題。
