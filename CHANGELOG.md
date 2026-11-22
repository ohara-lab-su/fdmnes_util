# 変更履歴

## v0.0.1（2026-11-22）

v0.0.0 のバグ修正版です。クラス化の際に書き換えた処理を SAE 原本と照合し、原本のコードやコメントを再利用できる箇所を復元しました。読み取りと描画の不具合は、実ファイルの値や書式を根拠に修正しました。

### 読み取り・書き出しの修正

- BAV は `FDMNES II program` と、年の末尾が切れた2016年9月1日版の見出しを認識します。複数のクラスタ座標表や結晶基底の変換行列がある場合は、SAE と同じく最後の表を採用します。
- `FdmSd(..., format_year=None)` は SD 自身の列名で2016形式と2020形式を選びます。BAV の改訂年から誤判定していた2019年 Cu の出力を読めます。2016形式は SAE の列配置に従って列数を検査します。2021年・2026年 Ni で確認した31列の磁性形式では、上下スピンの軌道列と、両スピン共通の `total`・`Int(total)` を読みます。対応する描画コマンドでは `--year` の省略と2016・2020の明示指定を利用できます。
- `FdmInp` は `File_out` などを `Filout` として認識し、`Filout`・`Absorber`・`Conv_out`・`Calculation` が繰り返された場合は最後の定義を使います。`get_calculation()` と `get_conv_out()` はファイル名を返します。`Calculation` 行の重みやシフトはファイル名に含めません。
- 生 XAS の見出しにある `E_edge` と `Z` を項目名で読み取ります。平均 XAS、光子エネルギーに変換したスペクトル、XYZ、`fdmfile.txt` の見出し・空行・固定幅などを SAE の書式に合わせました。

### 構造処理と公開 API の整理

- 結晶・分子の組み立て、FDMNES 構造節の書き出し、POSCAR 出力用の構造変換を `FdmStructure` に集約しました。`StructureConversion` の `fdm_to_atoms()` と `poscar_to_atoms()` は `FdmStructure` に移動しました。汎用読み取りの `other_to_atoms()` 相当は ASE の `ase.io.read()` を使います。
- `VaspPoscarFile` を廃止し、`FDvasp2fdm.py` は外部の `vasp_util.vasp_poscar.VaspPoscar` を直接使います。SAE の位置引数と `--ipput` を復元し、`-i` と `--input` も引き続き使えます。
- `AnalyzeFdmLog(...).positions()` は年別 BAV リーダーの `get_atoms_index_j()` と `get_position()` に置き換えました。年別リーダーの共通処理は一か所にまとめ、既存の公開メソッド名を維持しました。`FdmXyz.render()` と `FdmXyz.write()` は標準 XYZ の読み取りと同じ `fdmnes_util.xyz.Xyz` に統合しました。

### 描画コマンドの互換性修正

- XAS・LDOS・PDOS の例で、SAE のパネル配置、曲線、凡例、フェルミ準位の縦線を復元しました。`fdLDOS.py` は計算入力、サイト番号、軌道番号の指定を受け付け、既定でサイト1の p-LDOS を描きます。`fdLDOS_color.py` は占有側の塗り分けを多段 LDOS・TDOS・XAS と組み合わせられます。
- `fdLDOS0_specified.py` は入力省略時に原本どおり Pd6 の5サイトを合計して6で割ります。`fdMulti_3.py` と `fdPDOS_XAS_av.py` は入力省略時に原本の試料パスを使います。`fdPDOS_XAS_av.py` のフェルミ準位の縦線は表示軸の基準に合わせます。
- `FDplot_XASs.py` と `fdLDOSmulti.py` は保存先の指定を省略すると、SAE と同じ EPS・PDF・PNG を出力します。同じ図を複数形式で保存する処理は図を再利用します。
- `FDplot_XAS_LDOS.py` は位置引数で計算入力を指定できます。入力指定を省略すると `fdmfile.txt` の先頭ジョブを使い、`fdmfile.txt` がない場合は `read_pdb.inp` を使います。

### 検証と既知の制限

- 配布スクリプト28本を起動し、26本の予定した出力・操作と、歴史的な BUG 版2本の変換を行わない終了を確認しました。Fe の XYZ と畳み込みジョブファイルは SAE 原本とバイト単位で一致しました。主要 XAS・LDOS・PDOS の3コマンドでは、比較した8パネルの配置、10本の曲線、フェルミ準位の位置が一致しました。pytest は134件通過し、Sphinx は日英とサイトルートの3版をビルドできました。各コマンドの差と検証範囲は[コマンド監査表](scripts/COMMAND_AUDIT.md)を参照してください。
- 2022年以降の BAV の自動選択と、2021年・2026年の実出力で確認した SCF の履歴形式は未対応です。`Absorber` や `Calculation` の単値 getter は一つのブロックから複数値を返しません。詳細は[開発引き継ぎ書](FDMNES_CODEX_HANDOFF.ja.md)を参照してください。
- 日英の API リファレンスとスクリプト説明を更新しました。旧作業記録 `.PROGRESS/` は Git の追跡対象から外しました。

## v0.0.0（2026-11-21）

初版。Structural Analysis Environment（SAE）のFDMNES関連プログラムを、Python 3.10以降で使えるクラスライブラリと編集用サンプルに再構成しました。

- `FdmInp` と `Fdmfile` で計算入力とジョブ一覧を扱い、BAV、SD、生・畳み込みXASにはファイル形式ごとのクラスを用意しました。BAVとSDは2016形式と2020形式のリーダーを分け、SDは形式を明示して選択します。
- XASの吸収端・フェルミ準位を基準としたエネルギー変換、複数計算のXAS・PDOSの平均化、XAS・LDOS・PDOSの描画をライブラリにまとめました。Athenaの実験スペクトルとの比較や、サイト別の畳み込み入力の生成にも対応しました。
- CIF・PDB・XYZ・VASP POSCARとFDMNESの構造を扱う変換サンプルを収録しました。VASP POSCARの読み込みには別パッケージの `vasp_util`、CIFの読み込みやPOSCARの書き出しにはASEを利用します。
- SAEの `FD*` / `fd*` に対応する28本の編集用サンプルを収録しました。`fdmnes_util install script` で作業ディレクトリへコピーできます。元のスクリプトにある各オプションや出力の再現状況は[コマンド監査表](scripts/COMMAND_AUDIT.md)に記録しています。
- 日英の利用ガイド、スクリプトの実行例、手書きAPIリファレンス、Sphinxによる自動生成APIを整備しました。[日本語README](README.ja.md)
