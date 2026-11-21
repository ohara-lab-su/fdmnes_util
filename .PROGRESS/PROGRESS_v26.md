# rebuild v26

- SAE `fdLDOS_color.py` の `plt.fill_between(..., where=eng < EF0)` に基づき、占有LDOSの塗りつぶしを `PlotFdmDos.plot_occupied_ldos()` に実装。
- 編集可能なサンプル `scripts/fdLDOS_color.py` を追加。`fdmnes_util install script` の既存の配布方式により同梱。
- SAE原本の主要な履歴をサンプル先頭に記載。原本の全オプション、XAS・TDOS・スピンの複合描画は未再現。
- 他の未実装スクリプトおよび既存コードの規約違反は未解消。
