# 変更履歴

## v0.1.2（2026-11-23）

### 計算の実行

- `FdmRun.run()` は既定の `inp.txt` を1件だけ実行します。`run("Cu.inp")` のように入力名も指定できます。入力が存在しない場合は起動前にエラーを返します。Python が入力1件の `fdmfile.txt` を一時的に用意し、終了時に元の状態へ戻します。
- 既存の一覧を使う場合は `FdmRun.run_fdmfile()`、コマンドでは `FDrun.py --fdmfile` を明示します。一覧に記載された入力の存在を確認し、一覧をそのまま使って本体を起動します。
- `FdmRun.run_inputs()` は Python 側で入力順を管理し、入力ごとに FDMNES を起動します。戻り値は実行順のログパスのリストです。制限時間は一連の実行全体に適用します。

### 使用例と配布ファイル

- `fdmnes_util install` と `install script` は全サンプルをカレントディレクトリにコピーします。`install FDplot_XAS` のようにスクリプト名で1本を指定できます。`install list` は個別指定に使う名前と日本語の説明を1行ずつ表示します。
- `FDrun.py` と `FDmanual_examples.py` の冒頭に、入力名を指定する例、既存一覧を使う例、入力を保存してから実行する例、POSCAR からの入力作成例を追加しました。日英の利用ガイドも実行方法に合わせて更新しました。 [使い方](docs/ja/usage.md)
- v0.1.1 タグ以降にリポジトリへ追加された Apache License 2.0 の `LICENSE` を収録しています。

## v0.1.1（2026-11-22）

### 入力の準備と順次実行

- `FdmInp` から2026年形式の `*.inp` を作成・編集できます。`from_text()` で入力本文を開き、`from_poscar()` では `vasp_util` と `FdmStructure` で POSCAR の構造を取り込みます。キーワードブロックの追加・置換・削除や、切替エネルギーごとの計算半径の指定ができ、`save()` で保存します。読み込み形式の既定は2016年のままです。
- `FdmRun.run_inputs()` は Python で指定した順に複数の入力を実行します。一時的に使った `fdmfile.txt` は、終了時に以前の内容へ戻します。マニュアルの FCC 銅・磁鉄鉱・FeO₆ と POSCAR からの入力作成を例示する `FDmanual_examples.py` を収録しました。 [使い方](docs/ja/usage.md)
- v0.1.0 の変更履歴で案内した `FDrun.py`、`FDconv_sites.py`、`FDplot_SD.py`、`FDplot_SCF.py` を配布対象に収録しました。これらのスクリプトは v0.1.0 タグに含まれていませんでした。

### スクリプトの共通処理とドキュメント

- `FDmakeCconvAllsite.py` が使う `FdmConvolutionInputs` を `fdmnes_util.util.site_convolution_job_preparer.SiteConvolutionJobPreparer` に移し、改名しました。番号付きの生 XAS からサイト別の `conv_N.inp` と `fdmfile.txt` をまとめて準備します。
- `DosPlotSample` は `fdmnes_util.util.dos_plot_workflow.DosPlotWorkflow` に、`FdmResultFiles` は `fdmnes_util.util.result_file_operations.ResultFileOperations` に移し、改名しました。前者は LDOS・PDOS 描画の準備、後者は計算結果の一括整理を担当します。各コマンドの呼び出し先を更新しました。
- クラスとモジュールの docstring を日本語で整え、対応する入力・出力ファイルの名前やパターンを明記しました。日英の API リファレンスとコマンド監査表を更新しました。 [API リファレンス](docs/ja/manual_reference.md) · [コマンド監査表](scripts/COMMAND_AUDIT.md)

## v0.1.0（2026-11-22）

FDMNES の暫定的な順次実行機能と、2026年11月5日版で確認した入出力形式への対応を追加しました。

### 計算の実行（暫定・順次実行）

- `FdmRun.run()` は、指定した入力1件または作業フォルダの `fdmfile.txt` にあるジョブを、FDMNES 本体で実行します。一覧がなければ `read_pdb.inp` を使います。ジョブ一覧を使う場合の実行順は一覧の記載順です。`FdmRun` による同じ作業フォルダでの同時起動を防ぎます。
- 標準出力と標準エラーを実行ごとのログに保存します。時間制限を指定でき、終了コードが非ゼロの場合や本体が `STOP` を報告した場合はエラーを返します。入力1件の実行で `fdmfile.txt` を一時的に差し替えた場合は、終了時に元の内容を復元します。

### 2026年版の入出力

- **BAV**。改訂行が2026年11月5日版と一致する場合に `FdmBav2026` を選びます。`FdmBav.get_scf_history()` でサイクル番号と全エネルギー（eV）の組を取得でき、未記録のエネルギーは `None` で表します。従来の `get_n_scf_loop()` と `get_scf_toten()` でも同版の記録を取得できます。
- **SD**。`FdmSd` は列名から複素球面調和関数の射影や f 軌道列を検出し、`FdmSd2026` に委譲します。`format_year=2026` でも選択できます。通常の列構成には従来の2016・2020リーダーを使います。
- **計算入力**。`FdmInp` の既定は従来の実装を移した `FdmInp2016` です。`format_year=2026` を指定すると、複数の吸収サイトと畳み込みの各入力ファイル・重み・シフト・カットオフを取得できます。また、`Density_comp` と `Lmax_DOSout` を指定して計算入力を生成できます。
- **畳み込み XAS**。`FdmInp.write_convolution()` は重みとシフトを指定した複数サイトの畳み込み入力を生成し、`E_step_conv` で出力間隔、`Per_atom` で吸収原子一個あたりの強度を指定できます。`FdmConv` は `Header` が書いた2026年11月5日版の改訂行を検出すると `FdmConv2026` を選び、吸収端・畳み込み条件・シフトを読み取ります。通常の出力は `FdmConv2016` が読みます。

### 実行例と検証

- 2026年版の実行例は `FDrun.py`（本体の起動）、`FDconv_sites.py`（畳み込み入力の生成）、`FDplot_SD.py`（軌道射影の描画）、`FDplot_SCF.py`（SCF 全エネルギーの描画）です。日英の利用ガイドと API リファレンスを更新しました。[使い方](docs/ja/usage.md) · [スクリプトガイド](docs/ja/scripts.md)
- 2026年版本体で Au の f 軌道の射影値を出力列と照合し、Fe の2サイト畳み込みで 0.25 eV 刻みの出力と、`Per_atom` 指定時に強度が合計の半分になることを確認しました。2026年11月5日版以外の2022年以降の BAV 改訂日は自動選択の対象外です。

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
