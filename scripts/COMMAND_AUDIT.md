# SAE コマンドと fdmnes_util の照合

基準は配布アーカイブ `sae_original.zip` に収録された `sae/commands/` の同名スクリプトです。POSCAR の API は `vasp_util_original.zip` と、動作確認に使用した `vasp-util 0.0.9` で照合しました。Git の比較基点には `v0.0.0` タグと、統廃合前の `027da16` を使用しました。

## 廃止したモジュールとメソッドの行き先

| 旧コード | 現在の実装と移行方法 | 配布スクリプトの呼び出し |
| --- | --- | --- |
| `_elements.py` の原子番号・元素記号の辞書 | [`fdm_structure.py`](../src/fdmnes_util/fdm_structure.py) の `ElementTable.get_atomic_symbol0()`、`get_atomic_number1()`。配布済みの元素表を使用 | `FDbav2xyz.py` は BAV 経由、構造出力コマンドは `FdmStructure` 経由 |
| `AnalyzeFdmLog(reader).positions()` と `_cluster` | [`fdm_bav.py`](../src/fdmnes_util/fdm_bav.py) の共通リーダーが座標表を読む。利用者は年別リーダーの `get_atoms_index_j()`、`get_position()` を呼ぶ | `FDbav2xyz.py` は両 getter を直接使用 |
| モジュール関数 `_crystal_basis_transform()` | 年別 BAV リーダー共通の `get_t()`。SAE と同じ行列要素の配置を維持 | XYZ の書き出し自体は直交座標を使う。変換行列は公開 BAV API で取得可能 |
| 年別 BAV クラスに重複していた `__init__`、`get_edge`、`get_nspin`、`is_self_consistent`、`get_max_scf_iterations`、`get_n_scf_loop`、`get_scf_toten`、`get_position`、`get_atoms_index_j`、`get_natom`、`get_e_edge`、`get_ngroup`、`get_t` | 共通の `_FdmBavReader` に実装を置き、年別クラスが既存のメソッド名を継承する。終了行が異なる `get_lmax()` は各年別クラスに残る | `FDbav2xyz.py` と `FDgetfermi.py` の入口は `FdmBav.select_reader()` |
| `VaspPoscarFile(filename)`、`get_lattice_vectors()`、`get_direct_positions()`、`get_symbols()` | 外部の `vasp_util.vasp_poscar.VaspPoscar(str(filename))`。取得メソッドは順に `get_lattice_vectors()`、`get_coords_direct()`、`get_atom_indices()` | `FDvasp2fdm.py` が実クラスを直接生成し、`FdmStructure` に渡す |
| `StructureConversion.fdm_to_atoms()`、`poscar_to_atoms()`、`other_to_atoms()` | 前二者は **同名**の `FdmStructure` メソッド。最後のメソッドは ASE の委譲だけだったため、同等の呼び出しは `ase.io.read(filename, format=...)` | `FDfdm2vasp.py` は `FdmStructure.fdm_to_atoms()`。CIF/PDB の読み取りは該当形式クラス |
| `FdmXyz().render()`、`FdmXyz().write()` | [`xyz.py`](../src/fdmnes_util/xyz.py) の `Xyz.render()` と `Xyz.write()`。標準 XYZ の読み取りも `Xyz` が担当 | `FDbav2xyz.py` は `Xyz.render/write`、`FDxyz2fdm.py` は `Xyz(filename)` |
| `plot/_figure.py` の `save_figure()` | [`plot/__init__.py`](../src/fdmnes_util/plot/__init__.py) の描画クラス共通 `_save_figure()`。描画結果の保存・表示・終了を受け持つ | `PlotFdmDos`、`PlotFdmXas`、`PlotFdmXasLdos`、`PlotFdmAverage` を使うコマンド |
| `dos_plot_arguments()`、`plot_dos_sample()` とその補助関数 | [`DosPlotSample`](../src/fdmnes_util/dos_plot_sample.py) の `build_parser()`、`plot()` と非公開メソッド。ファイル選択と表示オプションをまとめる | `FDplot_LDOS.py`、`FDplot_PDOS.py`、`fdLDOS_color.py` |
| `FDplot_XAS.py` の `_spectrum_paths`、`_raw_curves`、`_dos_curves`、`_shift_curves` | 同じスクリプトの `XasPlotSample` のメソッド。格子検査、平均・変換の計算は既存解析クラスに委譲 | `main()` が `XasPlotSample.run()` を呼ぶ |
| `fdLDOS_color.py` の `_main_sd_file` | 同じスクリプトの `OccupiedLdosSample._run_sd_file()` | `main()` が `OccupiedLdosSample.run()` を呼ぶ |
| `cli.install_scripts()` | `ScriptInstaller.install_scripts()`。既存の import 名は同じメソッドへの別名 | `fdmnes_util install script` の実行経路を維持 |
| `AthenaNor._read_e0_comment()`、`FdmSd2020._check_spin()` | E0 の抽出は `AthenaNor.__init__` のコメント読取りに集約。SD のスピン検査と列選択は `_spin_suffix()` が担当 | Athena の読取りと SD を使う描画コマンド |
| 途中のコミットに存在した `FdmBav2026` | 0.0.1 の現行ツリーに該当クラスはない。2021年・2026年形式の SCF 履歴対応は引き継ぎ書に記録 | 2022年以降の BAV を年別リーダーへ自動選択する経路は未対応 |

SAE の `ReadFdmInp` と `WriteFdmInp` は `FdmInp`、`ReadFdmFdmfile` と `WriteFdmfile` は `Fdmfile` に対応します。生・畳み込み XAS は `FdmTxt` と `FdmConv`、BAV と SD はそれぞれの選択クラスと年別クラス、Athena は `AthenaNor` に対応します。

### v0.0.0 より前のモジュール名

以下はコミット `a8b4f0a` で廃止した18ファイルの現在の行き先です。

| 旧ファイル | 行き先 |
| --- | --- |
| `read_athena_nor.py` | `athena_nor.AthenaNor` |
| `read_fdm_bav.py`、`read_fdm_bav_2016.py`、`read_fdm_bav_2020.py` | `fdm_bav.FdmBav`、`fdm_bav_2016.FdmBav2016`、`fdm_bav_2020.FdmBav2020` |
| `read_fdm_sd.py`、`read_fdm_sd_2016.py`、`read_fdm_sd_2020.py` | `fdm_sd.FdmSd`、`fdm_sd_2016.FdmSd2016`、`fdm_sd_2020.FdmSd2020` |
| `read_fdm_txt.py`、`read_fdm_conv.py` | `fdm_txt.FdmTxt`、`fdm_conv.FdmConv` |
| `read_fdm_inp.py`、`write_fdm_inp.py` | `fdm_inp.FdmInp` の読取りと `render/write` |
| `read_fdmfile.py`、`write_fdmfile.py` | `fdmfile.Fdmfile` の読取りと `write` |
| `read_vasp_poscar.py` | 外部 `vasp_util.vasp_poscar.VaspPoscar` |
| `write_fdm_convolution_inputs.py`、`write_fdm_photoenergy.py` | `fdm_convolution_inputs.FdmConvolutionInputs.write`、`fdm_photoenergy.FdmPhotoenergy.write` |
| `write_fdm_structure.py`、`write_fdm_xyz.py` | `fdm_structure.FdmStructure.write`、`xyz.Xyz.write` |

## 配布スクリプト28本の呼び出しと動作差

下表の「実行」は現行コマンドを実際に起動した確認です。「原版比較」は同じ入力で SAE のコマンド、または明記した原版処理を実行して比較した範囲です。実験ファイルや試料名を置き換えたケースでは、元の試料データの再現性までは含みません。

| スクリプト | SAE の呼び出し → 現行の呼び出し | 挙動の差、理由、確認 |
| --- | --- | --- |
| [FDbav2xyz.py](FDbav2xyz.py) | `ReadFdmBav.get_natom/get_position/get_atoms_index_j` と直接出力 → `FdmBav.select_reader`、年別 getter、`Xyz.render/write` | Fe 実 BAV の227原子 XYZ が原版とバイト一致。現在もファイル出力と標準出力を選択できる。 |
| [FDcif2fdm.py](FDcif2fdm.py) | ASE の CIF 読み取り → `Cif` の ASE 読み取り、`FdmStructure.render/render_xyz_molecule` | 原版は ASE 読み取り後に `bug version` と表示して停止。現行の Crystal/Molecule 出力は追加実装。ASE で読み取った元素と座標を比較し、現行の CIF→構造節も実行。 |
| [FDclean.py](FDclean.py) | `ReadFdmInp/ReadFdmFdmfile` と glob・削除 → `Fdmfile.select_input`、`FdmInp.get_filout`、`FdmResultFiles.clean` | Fe の一時ディレクトリで原版と現行の削除後のファイル一覧が一致。補助ファイルの探索先は現行では Filout のディレクトリ。 |
| [FDconv_e2photoe.py](FDconv_e2photoe.py) | `ReadFdmInp/ReadFdmTxt/ReadFdmConv` の軸を書き換えて出力 → `FdmInp/FdmTxt/FdmConv`、`AnalyzeFdmXas.photon_energy`、`FdmPhotoenergy.write` | 原版105行目が読取り専用 `txt.eng` への代入で停止。さらに原版の出力は生 XAS の軸を畳み込み強度に対応させる。現行は畳み込み自身の軸を変換し、実 Fe の131行で強度と桁幅を検証。 |
| [FDfdm2vasp.py](FDfdm2vasp.py) | `sae.structure.document.Read` と `cell.write` → `FdmStructure.fdm_to_atoms`、ASE の `write(format="vasp")` | Fe の結晶サンプルで原版・現行の元素順、格子、位置が一致。現行の分子経路は ASE で真空層を付け、座標の距離とセルをテスト。原版にある POSCAR 内容の標準出力は現行ではファイル保存と結果表示。 |
| [FDgetfermi.py](FDgetfermi.py) | `ReadFdmInp/ReadFdmFdmfile`、`ReadFdmTxt.E_Fermi/E_edge`、`ReadFdmBav.edge` → `Fdmfile.select_input`、`FdmInp`、`FdmTxt.get_efermi/get_eedge`、BAV の `get_edge()` | Fe の数値は両方 0.0、7112.0。表示ラベルは原版 `K1`、現行 `Iron K1 edge`。現行は v0.0.0 からの BAV 公開 API の完全ラベルを表示。 |
| [FDmakeCconvAllsite.py](FDmakeCconvAllsite.py) | `ReadFdmInp.get_filout`、glob と直接書き出し → `FdmInp.get_filout`、`FdmConvolutionInputs.write`、`Fdmfile.write` | Fe の2サイトで `fdmfile.txt`、`conv_1.inp`、`conv_2.inp` が原版とバイト一致。現行は出力ディレクトリに対してジョブの相対パスを計算。 |
| [FDmove.py](FDmove.py) | `ReadFdmInp/ReadFdmFdmfile`、`os.rename` 相当 → `Fdmfile.select_input`、`FdmInp`、`FdmResultFiles.rename/move` | `Fe New` で原版と移動後の名前が一致し、現行の各ファイル内容は移動前と同一。現行の衝突拒否と `--destination` のアーカイブ経路は追加。 |
| [FDpbd2fdm.py](FDpbd2fdm.py) | ASE の `read(format="pdb")`、`StructureExtraction.chk_pdb_cryst1`、`FdmnesStructureWriter.print_fdmnes0` → `Pdb`、`FdmStructure.render/render_xyz_molecule` | 検証環境の ASE で原版が `UnknownFileTypeError: pdb`。現行は `proteindatabank` で読み取り、CRYST1 有無による結晶・分子の選択を維持。形式名を補った原版処理と座標・セルを比較し、現行のコマンド出力も確認。 |
| [FDplot_LDOS.py](FDplot_LDOS.py) | `ReadFdmInp/ReadFdmSd/ReadFdmTxt/ReadFdmConv` と直接描画 → `DosPlotSample` 経由で `FdmInp/FdmSd/FdmTxt/FdmConv`、`PlotFdmDos.plot_composite` | 実 Fe で図を出力。回帰テストは全 DOS・積分・反転した下スピン・XAS の曲線を照合。磁性2020形式では実ファイルの共通 TDOS を1段に描く。 |
| [FDplot_PDOS.py](FDplot_PDOS.py) | `ReadFdmSd.get_pdos` と直接描画 → `DosPlotSample`、`FdmSd.get_pdos`、`PlotFdmDos.plot_composite` | 実 Fe で図を出力し、s/p/d のブロックおよび p の分割を回帰検証。2020形式には磁気量子数ごとの積分列がないため個別 PDOS 積分を作らない。 |
| [FDplot_XAS.py](FDplot_XAS.py) | `ReadFdmTxt/Conv/Sd`、`ReadAthenaNor` と直接描画 → `XasPlotSample`、各リーダー、`AnalyzeFdmAverage`、`AnalyzeFdmXas`、`PlotFdmXas.plot_composite` | 実 Fe で出力。サイト平均は系列内の格子一致を確認し、生・畳み込み・SD・実験データにはそれぞれの軸を使う。回帰テストで平均の書出し、吸収端・スピン、観測曲線を確認。 |
| [FDplot_XAS_LDOS.py](FDplot_XAS_LDOS.py) | `ReadFdmTxt/Conv/Sd` と直接描画 → `FdmTxt/FdmConv/FdmSd`、`AnalyzeFdmXas.energy_reference`、`PlotFdmXasLdos.plot` | 実 Fe の出力、原版処理と曲線・フェルミ線を照合。フェルミ基準を選ぶ場合は軸と縦線を同じ基準に置く。 |
| [FDplot_XASs.py](FDplot_XASs.py) | `ReadFdmInp/ReadFdmTxt/ReadFdmConv/ReadAthenaNor` → `FdmInp`、`AnalyzeFdmXas.site_spectra`、`AthenaNor`、`PlotFdmXas.plot_sites` | 現行は `-a` に指定したサイト番号をファイル名に使う。原版のループは指定された個数だけ1から順に読む。実 Fe のコピーで観測付き EPS・PDF・PNG を生成。 |
| [FDvasp2fdm.py](FDvasp2fdm.py) | ASE の POSCAR 読み取り、`AseInputOperations.write_fdmnes/write_fdmnes_inp` → 外部 `VaspPoscar`、`FdmStructure.write`、`FdmInp.write` | 同じ FeO POSCAR で原版と格子・原子番号・分率座標の出力欄が一致。統廃合前の現行版とも2出力がバイト一致。今回、移植時に落ちていた位置引数と `--ipput` を復元。 |
| [FDvasp2fdm_BUG.py](FDvasp2fdm_BUG.py) | 歴史版の停止分岐 → 停止分岐を維持 | `gug version` を出して終了し、変換ファイルなし。実行成功は変換成功を意味しない。 |
| [FDvasp2fdm_NEW_20151125_BUGversion.py](FDvasp2fdm_NEW_20151125_BUGversion.py) | 歴史版の停止分岐 → 停止分岐を維持 | `gug version` を出して終了し、変換ファイルなし。 |
| [FDxyz2fdm.py](FDxyz2fdm.py) | `ReadMd`、`AseInputOperations`、`ElementTable` → `Xyz(filename)`、`FdmStructure.render_xyz_molecule` と同クラス内の元素表利用 | 標準 XYZ の先頭フレームと Molecule 節の出力書式を原版処理と照合。現行コマンドは標準 XYZ 入力と構造節の出力を扱う。原版の OpenMX MD 探索、軌跡読取り、入力テンプレートの併記は現行 CLI に含まれない。 |
| [fdExp_comp_XAS.py](fdExp_comp_XAS.py) | `ReadFdmConv/ReadFdmTxt/ReadAthenaNor` と直接描画 → `FdmConv/FdmTxt/AthenaNor`、`PlotFdmXas.plot_experiment_comparison` | Fe の計算データを同一ファイル名の試料として与え、原版と配置・曲線・軸ラベル・線幅が一致。現行ではファイル名と表示範囲を指定できる。 |
| [fdLDOS.py](fdLDOS.py) | `ReadFdmInp.get_filout`、`ReadFdmSd.get_ldos` → `FdmInp/FdmSd`、`PlotFdmDos.plot_local` | 既定で `read_pdb.inp`、サイト1、p-LDOS、0 eV の縦線。Fe コピーで同じ軌道列と配置を確認。現行は図のファイル保存も行う。 |
| [fdLDOS0_specified.py](fdLDOS0_specified.py) | `ReadFdmSd(..., absorber=(1,2,3,4,5), weight=6.0)` → 各 `FdmSd`、`AnalyzeFdmAverage.average`、`PlotFdmDos.plot_single_orbital` | Pd6 の既定ファイル名・5サイトの和÷6を維持。Fe のコピーを同じファイル名で配置し、EPS・PDF・PNG を生成。実 Pd6 の数値比較は未実施。 |
| [fdLDOS_color.py](fdLDOS_color.py) | `ReadFdmInp/Conv/Txt/Sd` と `fill_between` → `DosPlotSample`、`PlotFdmDos.plot_composite` または SD 直接入力の `plot_occupied_ldos` | 計算入力経路で原版の多段構成とフェルミ準位より下の灰色塗りを使用。Fe の多段 XAS・TDOS・p-LDOS と積分付き PDF を生成。 |
| [fdLDOSmulti.py](fdLDOSmulti.py) | `ReadFdmTxt/ReadFdmSd` と3段描画 → `FdmTxt/FdmSd`、`PlotFdmDos.plot_multiple_sites/save_multiple_formats` | 3サイトの同じ図を3形式で保存。原版描画処理と Fe の曲線・フェルミ線を比較。原版既定の Ba/Ba/Ti ラベルを維持。 |
| [fdMulti_2_XAS+LDOS+EXP.py](fdMulti_2_XAS+LDOS+EXP.py) | `ReadFdmConv/ReadFdmTxt/ReadFdmSd/ReadAthenaNor` → 各現行リーダー、`PlotFdmXasLdos.plot_experiment_ldos` | 実験強度の 1/39 と +0.015、計算軸 +4.5 eV は原版既定。原版が生 XAS・LDOSにも畳み込み軸を使う箇所は各データ自身の軸に訂正。Fe コピーで PDF 生成。原版の `options()` は実行部で呼ばれていない。 |
| [fdMulti_3.py](fdMulti_3.py) | `ReadFdmSd/ReadFdmTxt`、固定3計算の直接描画 → `FdmSd/FdmTxt`、`PlotFdmDos.plot_three_calculations` | 原版の2番目の曲線は1番目の Fermi を使う。現行は各計算の Fermi でシフトし、同じ図を3形式で保存。Fe コピー3組で実行し、独立シフトを回帰テスト。 |
| [fdPDOS_XAS_av.py](fdPDOS_XAS_av.py) | `ReadFdmSd/ReadFdmTxt/ReadFdmConv`、固定3計算の平均・描画 → 各リーダー、`AnalyzeFdmAverage`、`PlotFdmAverage` | 既定の3計算と軌道ブロックを維持し、明示入力にも対応。系列ごとに格子を検査し、独立軸と表示基準のフェルミ線を使用。Fe コピーで既定経路の3形式を生成し、単一ブロックの原版処理と曲線を照合。 |
| [fdXAS.py](fdXAS.py) | `ReadFdmConv.eng/xas` と直接描画 → `FdmConv.get_eng/get_xas`、`PlotFdmXas.plot_convolved` | 実 Fe で原版と配置・軸ラベル・曲線・線幅が一致。入力探索と0 eVの縦線を維持。 |
| [fdXAS_specified.py](fdXAS_specified.py) | `ReadFdmConv/ReadFdmTxt`、`conv.eng - txt.E_Fermi` → `FdmConv/FdmTxt`、`AnalyzeFdmXas.fermi_relative_convolution`、`PlotFdmXas.plot_convolved(specified=True)` | 同じ Fe ファイルを既定の Au パスに置いて、原版と配置・軸ラベル・曲線・線幅が一致。現行では入力パスと保存先も指定できる。 |

## 確認範囲

- 配布ファイルと SAE 原本の同名ファイルの28組を照合。現在の各コマンドは個別の一時ディレクトリで実行し、ファイルを変更するコマンドも複製した入力だけを対象にした。模擬した試料名には保存済み Fe 実出力か、CIF・PDB・XYZ・POSCAR の小さな検証入力を使用した。
- オプション宣言は、共通の DOS パーサーと XAS のループ生成分を展開して照合した。現行側に宣言がない SAE の綴りは `fdMulti_2_XAS+LDOS+EXP.py` の `-i`／`--input` のみで、原版の実行部ではこのパーサーを呼んでいない。綴りの一致は意味の一致を保証しない。たとえば `fdPDOS_XAS_av.py` の SAE `-o` は出力接尾辞で、現行の `-o` は保存先、接尾辞は `--outsuffix`。
- 前表の原版比較に加え、原版メソッドまたは原版スクリプトの該当区間と現行実装を比較する28ケースを実行した。一部は旧 ASE API の形式名・関数、または原本で読取り専用の属性の代入を検証用に補っている。その結果は原版 CLI がそのまま完走したケースと区別した。
- 原版と現行の `FDplot_XAS.py`（既定）、`FDplot_LDOS.py` と `FDplot_PDOS.py`（`--xas --sp`）を同じ Fe 実データで実行。合計8パネルの配置、10本のスペクトル曲線、フェルミ準位の位置が一致した。PDOS の p 成分パネルで原版が同じ縦線を軌道ごとに重ねていたため、縦線の本数は原版が2本、現行が1本。
- pytest は134件通過。日英とサイトルートの Sphinx ビルドは3件成功。作図検証では非対話の Agg を使用したため、画面表示を呼ぶサンプルで表示不可の警告が出る。画像ファイルの保存は確認済み。
- 統廃合により外部 import が変わる名前は上表の通り。既存の CLI 名と28本の配布経路は維持した。実行確認と数値比較で示せる範囲は前表の通りで、全オプションの全組合せ、元の試料ファイルが手元にない例、対話 GUI と FDMNES の再実行は今回の確認に含まれない。
