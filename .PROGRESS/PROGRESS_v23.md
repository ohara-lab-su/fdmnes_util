# Rebuild v23

- SAE `fdLDOSmulti.py` を参照し、3サイトのp-LDOSを縦3段で表示する編集可能なサンプルを追加。
- `PlotFdmDos.plot_multiple_sites()` を追加。エネルギー変換、Fermi線、共有x軸、凡例を実装。
- 原本の固定プレフィックスをCLIで変更可能にし、年度別SDクラスを明示的に選択。
- 原本のEPS/PDF/PNG同時保存と対話表示は未移植。既存の単一出力指定を利用。
- SAEのヘッダ履歴は今回のサンプルに原本に記載された内容を転記。
- 既存の全クラスのdocstring・Black準拠・28本の完全再現は未完了。
