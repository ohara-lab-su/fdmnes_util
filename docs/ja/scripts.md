# スクリプトガイド

各サンプルの引数は `python <ファイル名> --help` で確認できます。ファイル名の大文字・小文字を区別してください。

## SAE での位置づけ

SAE の命名では、大文字の `FD*.py` は汎用コマンド、小文字の `fd*.py` は試料や解析条件に合わせて編集する研究用の例です。本パッケージでは両方を編集可能なサンプルとして `fdmnes_util install script` で配布します。SAE 本体は実行時の依存ではありません。[SAE 日本語 README の FDMNES 節](https://github.com/ohara-lab-su/sae/blob/main/README.ja.md#for-fdmnes)

下表の原本は提供された `sae_original.zip` 内の `sae/commands/<同名ファイル>` です。引数、既定値、図の見た目まで同じとは限りません。原本と共通しないオプションや検証範囲は [コマンド監査](https://github.com/ohara-lab-su/fdmnes_util/blob/main/.PROGRESS/COMMAND_AUDIT.md) を参照してください。

## POSCAR 読み込みと vasp_util 原本

SAE の `FDvasp2fdm.py` は ASE で POSCAR を読み、`AseInputOperations` で FDMNES 用の構造を整えていました。現行の `FDvasp2fdm.py` では 外部ライブラリの `vasp_util.vasp_poscar.VaspPoscar` を直接使い、`get_lattice_vectors()`、`get_coords_direct()`、`get_atom_indices()` で格子・分率座標・原子順の元素記号を取得します。これらの読み取りメソッドは `vasp_util_original.zip` 内の `vasp_util/vasp_poscar.py` で確認できます。FDMNES の構造節と入力の生成は現行の `FdmStructure` と `FdmInp` が担当します。逆方向の `FDfdm2vasp.py` は FDMNES 入力の構造を ASE に渡し、ASE で POSCAR を書き出します。

## 複合描画の選び方

- `FDplot_XAS.py` はXASを中心に、実験データを上段、LDOSを下段に追加できます。`--xas` は生XASのみ、`--broad` は畳み込み後XASのみです。
- `FDplot_LDOS.py` と `FDplot_PDOS.py` はDOSが中心です。`--xas` は下段に畳み込み後XASを置き、`--broad` は生XASも重ねます。
- この3本は既定でPDFを保存します。`--pdf` でEPSとPNGを追加し、`--nw` でGUI表示を省略します。入力ファイルとSD形式を確認してから実行してください。
- `FDplot_XAS.py -a 1 2 -w 4` はサイト1・2のXASの和を4で割ります。除数省略時はサイト数で割ります。選択したデータに応じて `*_0.txt`、`*_0_conv.txt`、`*_0_sd0.txt` を書きます。

## スクリプト別リファレンス

実行例は、`fdmnes_util install script` でサンプルを展開し、入力データを置いた作業ディレクトリで実行します。例の `Fe` は計算結果の接頭辞、`--year 2020` は SD ファイルの形式年です。各スクリプトの原本は `sae_original.zip` の `sae/commands/` に同名で収録されています。描画には Matplotlib、CIF・PDB の読み込みと POSCAR の書き出しには ASE、POSCAR の読み込みには `vasp_util` が必要です。[インストール方法](usage.md)

### `FDbav2xyz.py`

**原本の用途**
計算半径で切り出されたクラスタを BAV ログから取り出し、VESTA などで形状や近接原子を確認するためのツールです。

**現行版の入出力**
接頭辞 `Fe` または `Fe_bav.txt` を指定すると `Fe.xyz` を作ります。`--std` を付けると同じ XYZ データを標準出力に出します。

**実行例**

```bash
python FDbav2xyz.py -i Fe
```

**原本からの変更点**
原本の小数点以下10桁の座標を継承しました。引数省略時は `Cu_bav.txt`、次に唯一の BAV ファイルを探します。候補が複数なら明示指定が必要です。

### `FDcif2fdm.py`

**原本の用途**
SAE の README では CIF から XANES 計算入力を作る用途が紹介されています。ZIP 原本は ASE で CIF を読み、`bug version` と表示して終了します。

**現行版の入出力**
CIF を読み、`Crystal` 構造節を `Fe.fdmnes` に書きます。`--mol` で `Molecule` 節を選べます。

**実行例**

```bash
python FDcif2fdm.py Fe.cif --output Fe.fdmnes
```

**原本からの変更点**
現行版は構造出力を実装しました。出力は構造節なので、計算条件を含む入力へ組み込んで使います。

### `FDclean.py`

**原本の用途**
`Filout` に対応する生成物をまとめて消して、同じ条件で再計算できる状態に戻すツールです。

**現行版の入出力**
計算入力から `Filout` を読み、生 XAS、畳み込み XAS、BAV、SD と、同じディレクトリの補助ログを削除します。削除したファイルのパスを表示します。下の例は出力のコピーを置いたディレクトリで試せます。

**実行例**

```bash
python FDclean.py -i read_pdb.inp
```

**原本からの変更点**
削除対象は `Filout` のディレクトリ内です。引数省略時は `fdmfile.txt` の先頭ジョブを使い、ジョブ一覧がなければ `read_pdb.inp` を使います。

### `FDconv_e2photoe.py`

**原本の用途**
SAE では、`Energpho` を使わずに計算した畳み込み結果を、実験と比較しやすい光子エネルギー軸に換算するために使いました。

**現行版の入出力**
計算入力、生 XAS のヘッダ、畳み込み結果を読み、`Fe_conv_photoe.txt` にエネルギーと強度を書きます。光子エネルギー設定済みの入力はエラーになり、`--fermi` を付けると吸収端を足した後にフェルミ値を引きます。

**実行例**

```bash
python FDconv_e2photoe.py -i read_pdb.inp -t Fe.txt -c Fe_conv.txt
```

**原本からの変更点**
現行版は畳み込みファイル自身のエネルギー格子と強度を組にして出力するため、生 XAS と畳み込み結果の点数が違う場合にも対応します。

### `FDfdm2vasp.py`

**原本の用途**
FDMNES 入力に手で記述した構造などを VASP の POSCAR として再利用するためのツールです。

**現行版の入出力**
`Crystal` または `Molecule` 節を含む `*.inp` を読み、POSCAR 形式で保存します。例の `--vacuum 12` は分子の各側に12 Åの余白を設けます。`-o` 省略時は入力名に `.vasp` を足します。

**実行例**

```bash
python FDfdm2vasp.py -i read_pdb.inp -o POSCAR --vacuum 12
```

**原本からの変更点**
構造の解釈を `FdmInp`、POSCAR の保存を ASE が担当します。分子用の真空幅を指定できるようになりました。

### `FDgetfermi.py`

**原本の用途**
SAE では XAS の軸合わせや結果確認のため、フェルミ準位と吸収端を素早く参照するのに使いました。

**現行版の入出力**
`Fe.txt` と `Fe_bav.txt` を読み、フェルミ準位、吸収端記号、吸収端エネルギーを表示します。`-i read_pdb.inp` で計算入力の `Filout` を使うこともできます。

**実行例**

```bash
python FDgetfermi.py --name Fe
```

**原本からの変更点**
年別の BAV リーダーで吸収端記号を読みます。`--name` を使えば入力ファイルなしで結果ファイルを選べます。

### `FDmakeCconvAllsite.py`

**原本の用途**
複数の吸収サイトを計算した後、サイトごとの畳み込みを FDMNES で連続実行するための入力を準備します。

**現行版の入出力**
入力の `Filout` から `Fe_1.txt` などの番号付き生 XAS を探し、作業ディレクトリに `conv_1.inp` などと `fdmfile.txt` を書きます。既存のジョブ一覧は上書きされます。

**実行例**

```bash
python FDmakeCconvAllsite.py -i read_pdb.inp
```

**原本からの変更点**
原本のファイル名順を継承し、現行版はジョブの実行ディレクトリからの相対パスを記述します。生成した一覧は FDMNES で実行します。

### `FDmove.py`

**原本の用途**
同じ `Filout` 配下の結果を一括改名し、再計算前の結果を別名で残すためのツールです。

**現行版の入出力**
例は `Fe.txt`、`Fe_bav.txt`、`Fe_conv.txt`、`Fe_sd*.txt` の接頭辞を `Fe_saved` に変更し、移動先を表示します。接頭辞を一つだけ指定した場合は計算入力の `Filout` が移動元です。

**実行例**

```bash
python FDmove.py Fe Fe_saved
```

**原本からの変更点**
改名前に移動先の衝突を確認します。`python FDmove.py -i read_pdb.inp -d archive` なら元のファイル名のまま別ディレクトリへ移動できます。

### `FDpbd2fdm.py`

**原本の用途**
PDB の原子座標と格子を直接 FDMNES の構造節に書き、計算入力内で構造を確認できるようにするツールです。

**現行版の入出力**
PDB の原子レコードと `CRYST1` を読み、周期構造は `Crystal`、分子は `Molecule` として `Fe.fdmnes` に書きます。

**実行例**

```bash
python FDpbd2fdm.py Fe.pdb --output Fe.fdmnes
```

**原本からの変更点**
原本の綴り `pbd` を維持しています。現行版はパッケージの `Pdb` と `FdmStructure` を使います。

### `FDplot_LDOS.py`

**原本の用途**
選択した原子の軌道群別 LDOS を多段で表示し、全 DOS、積分、XANES を合わせて調べるためのツールです。

**現行版の入出力**
`Filout=Fe` の入力、`Fe.txt`、`Fe_sd0.txt`、`--xas` 用の `Fe_conv.txt` から `LDOS0.pdf` を作ります。`--intdos` はファイルに格納された積分値を描きます。

**実行例**

```bash
python FDplot_LDOS.py -i read_pdb.inp -a 0 --year 2020 --sp --total --intdos --xas --nw
```

**原本からの変更点**
現行版は SD の列名で形式を選びます。`--year` で形式を明示できます。光子エネルギー軸をフェルミ基準に戻すときは吸収端とフェルミ値の両方を引きます。

### `FDplot_PDOS.py`

**原本の用途**
LDOS の軌道群をさらに磁気量子数で分け、たとえば `p_z` と面内の `p_x`・`p_y` を見比べます。

**現行版の入出力**
`Filout=Fe` の計算入力、`Fe.txt`、`Fe_sd0.txt`、`Fe_conv.txt` から `PDOS0.pdf` を作ります。`--sp` は s と p、`--spd` は d も表示します。

**実行例**

```bash
python FDplot_PDOS.py -i read_pdb.inp -a 0 --year 2020 --sp --xas --nw
```

**原本からの変更点**
SD 形式を明示でき、`--total` で全 DOS の段を追加できます。原本と同様、`--intdos` の指定で軌道成分ごとの積分線は描きません。

### `FDplot_XAS.py`

**原本の用途**
生 XANES と畳み込みを中心に実験・LDOS を並べ、吸収サイト別の曲線を平均して比較する汎用描画ツールです。

**現行版の入出力**
`Filout=Fe` の入力、`Fe.txt`、`Fe_conv.txt`、実験の `Fe_obs.txt.nor`、LDOS の `Fe_sd0.txt` から `Fe_XAS.pdf` を作ります。`--nw` は画面表示を省きます。

**実行例**

```bash
python FDplot_XAS.py -i read_pdb.inp --obs Fe_obs.txt.nor --dos --year 2020 --nw --output Fe_XAS.pdf
```

**原本からの変更点**
サイト平均は系列ごとにエネルギー格子を確認します。`-a 1 2 -w 4` ならサイト1・2の和を4で割ります。平均を `Fe_0.txt` と `Fe_0_conv.txt` に書き、`--dos` 指定時は `Fe_0_sd0.txt` も作ります。原本コードと同様、EPS と PNG の追加保存は `--pdf` です。

### `FDplot_XAS_LDOS.py`

**原本の用途**
畳み込み XAS と原子一つの軌道群別 LDOS を縦に並べる、特定サイトの軌道解析用の図です。

**現行版の入出力**
`Filout=Fe` の入力、`Fe.txt`、`Fe_conv.txt`、`Fe_sd0.txt` から `XAS_LDOS0.pdf` を作ります。`--fermi` でフェルミ基準を選べます。

**実行例**

```bash
python FDplot_XAS_LDOS.py -i read_pdb.inp -a 0
```

**原本からの変更点**
現行版は SD の列名で形式を判定し、利用できる s・p・d 群を描きます。`--year` で形式を明示することもできます。軌道指定の `--orbit` と `-l` は原本にあります。

### `FDplot_XASs.py`

**原本の用途**
原本コードは複数の吸収サイトの畳み込み XAS を同じ図で比較し、実験曲線も併記できます。

**現行版の入出力**
`Filout=Fe` の入力に加え、サイト1・2の `Fe_N.txt` と `Fe_N_conv.txt` を読みます。`--obs` を付けた例は `Fe_N_obs.txt.nor` も読み、`Fe_sites.pdf` を作ります。

**実行例**

```bash
python FDplot_XASs.py -i read_pdb.inp -a 1 2 --obs --output Fe_sites.pdf
```

**原本からの変更点**
原本に合わせて `-a` で曲線を選び、サイトごとの曲線を指定順に描きます。出力先の指定には現行版の `--output` を使います。

### `FDvasp2fdm.py`

**原本の用途**
VASP の構造を引き継ぎ、FDMNES で基本的な XANES 計算を始めるための入力ひな形を用意します。

**現行版の入出力**
POSCAR から `Fe.fdmnes` に構造節、作業ディレクトリの `read_pdb.inp` に条件例付き入力を書きます。`--mol` で分子節を選べます。

**実行例**

```bash
python FDvasp2fdm.py -i POSCAR -o Fe.fdmnes
```

**原本からの変更点**
原本は ASE で POSCAR を読みます。現行版は外部の `vasp_util` で格子、座標、元素を取得し、`-o` は構造節の保存先に使います。

### `FDvasp2fdm_BUG.py`

**原本の用途**
ASE を置き換えて SAE 独自の POSCAR 読み込みを使った旧試作です。重大な不具合が見つかり、原本では変換呼び出しを無効にして凍結しています。

**現行版の入出力**
POSCAR の候補パスを確認し、`gug version` と表示して終了します。生成ファイルはありません。

**実行例**

```bash
python FDvasp2fdm_BUG.py -i POSCAR
```

**原本からの変更点**
現行版もファイルの存在確認とメッセージだけを再現します。実際の構造変換には `FDvasp2fdm.py` を使います。

### `FDvasp2fdm_NEW_20151125_BUGversion.py`

**原本の用途**
2015年11月25日版の別試作です。こちらも原本に変換処理の跡が残っていますが、実行する呼び出しは無効化されています。

**現行版の入出力**
POSCAR の候補パスを確認し、`gug version` と表示して終了します。生成ファイルはありません。

**実行例**

```bash
python FDvasp2fdm_NEW_20151125_BUGversion.py -i POSCAR
```

**原本からの変更点**
現行版は別名の履歴サンプルとして保存され、変換無効の挙動を継承しています。

### `FDxyz2fdm.py`

**原本の用途**
原本は SAE の OpenMX 用 `ReadMd` で XYZ 系の MD データを読み、FDMNES の分子構造を含む入力に変換します。

**現行版の入出力**
原子数、コメント、元素記号と直交座標を含む標準 XYZ を読み、`cluster.fdmnes` に `Molecule` 節を書きます。

**実行例**

```bash
python FDxyz2fdm.py cluster.xyz --output cluster.fdmnes
```

**原本からの変更点**
入力は標準 XYZ、出力は構造節です。原本で生成していた別の計算入力ファイルは、必要な計算条件を加えて用意します。

### `fdExp_comp_XAS.py`

**原本の用途**
Athena の正規化データと計算 XAS を同じ軸に重ね、試料に合わせて書き換えるための小さな例です。

**現行版の入出力**
畳み込み結果、生 XAS、Athena の `.nor` ファイルを読み、光子エネルギー軸の `Fe_compare.pdf` を作ります。

**実行例**

```bash
python fdExp_comp_XAS.py -i Fe_conv.txt --txt Fe.txt --experiment Fe_obs.txt.nor --xmin 7100 --xmax 7200 --output Fe_compare.pdf
```

**原本からの変更点**
吸収端を足して軸を合わせる処理を継承し、データファイル、表示範囲、出力名を引数にしました。エネルギー範囲の既定値は Au 用です。

### `fdLDOS.py`

**原本の用途**
指定サイトの SD ファイルから LDOS を取り出して描くための最小限の例です。

**現行版の入出力**
`read_pdb.inp` の `Filout` を使い、既定ではサイト 1 の p-LDOS を描きます。`-i` で計算入力、`-a` でサイト番号、`-l` で軌道角運動量の番号を指定できます。積分列を描く場合は `--intdos` を付けます。

**実行例**

```bash
python fdLDOS.py -i read_pdb.inp -a 0 -l 1 --year 2020 -o Fe_LDOS.pdf
```

**原本からの変更点**
SD ファイルも直接指定できます。`--year` で SD の形式を明示でき、`-o` で図の保存先を選べます。

### `fdLDOS0_specified.py`

**原本の用途**
原本は Pd6 の結果を題材に、表示範囲を指定して p-LDOS を図にするための例です。

**現行版の入出力**
計算入力の `Filout` が `Fe` なら `Fe_sd0.txt` を読み、範囲を絞って `LDOS.pdf` を保存します。`--formats` を省略すると EPS・PDF・PNG を保存します。

**実行例**

```bash
python fdLDOS0_specified.py -i read_pdb.inp --year 2020 --emin -10 --emax 10 --dmax 5 --formats pdf
```

**原本からの変更点**
入力を省略すると、原本と同じ Pd6 の5サイトの p-LDOS の和を6で割ります。計算入力を指定すると、その計算の `_sd0.txt` を描きます。

### `fdLDOS_color.py`

**原本の用途**
DOS 曲線の占有側を塗り、フェルミ準位より下の状態を読み取りやすくする描画例です。

**現行版の入出力**
SD を直接読み、指定の軌道群の `--fermi` より下を塗った `Fe_occupied.pdf` を作ります。`--fermi 0` は描画軸の 0 eV を境界にします。`--edge-offset` はエネルギー軸に加える量です。

**実行例**

```bash
python fdLDOS_color.py Fe_sd0.txt --year 2020 --orbital p --fermi 0 --output Fe_occupied.pdf
```

**原本からの変更点**
計算入力から描く場合は、原本と同じ多段 LDOS・TDOS・XAS を組み合わせられます。たとえば `-i read_pdb.inp --p --total --xas --nw` で p-LDOS、TDOS、XAS を描きます。

### `fdLDOSmulti.py`

**原本の用途**
原本は `BaTiO3_R3m` の3サイトを並べ、Ba と Ti の p-LDOS を見比べるための例です。

**現行版の入出力**
`Fe.txt` と `Fe_sd0.txt` から `Fe_sd2.txt` までを読み、3サイトの図を作ります。出力先を省略すると、原本同様に `LDOSmulti` の EPS・PDF・PNG を保存します。

**実行例**

```bash
python fdLDOSmulti.py --input Fe --year 2020 --orbital p --all-formats
```

**原本からの変更点**
計算名、軌道、表示範囲を引数で選べます。既定の `BaTiO3_R3m` には原本の Ba、Ba、Ti のサイトラベルを使います。

### `fdMulti_2_XAS+LDOS+EXP.py`

**原本の用途**
Cu の計算 XAS と実験を上段、p-LDOS を下段に置き、吸収構造と軌道の関係を確認するための例です。

**現行版の入出力**
畳み込み XAS、生 XAS のヘッダ、SD、Athena の実験データを読み、二段の `Cu_compare.pdf` を保存します。

**実行例**

```bash
python fdMulti_2_XAS+LDOS+EXP.py --conv Cu_conv.txt --txt Cu.txt --sd Cu_sd0.txt --experiment Cu_obs.txt.nor --year 2020 --output Cu_compare.pdf
```

**原本からの変更点**
原本の Cu 用補正値を既定値とし、`--energy-offset`、`--experiment-scale`、`--experiment-offset` と表示範囲を指定できるようにしました。

### `fdMulti_3.py`

**原本の用途**
原本は Pd55 の二計算と `FCC/Pd` を対比し、計算ごとのフェルミ準位を基準に p-LDOS を並べます。

**現行版の入出力**
各接頭辞の `.txt` と `_sd0.txt` の組を読み、`Fe_three.eps`、`Fe_three.pdf`、`Fe_three.png` を保存します。`--site` で別の SD 番号を選べます。

**実行例**

```bash
python fdMulti_3.py run1/Fe run2/Fe run3/Fe --year 2020 --site 0 --output Fe_three
```

**原本からの変更点**
三つの接頭辞を省略すると原本の Pd の計算を使います。計算、軌道、サイト、表示範囲を指定できます。

### `fdPDOS_XAS_av.py`

**原本の用途**
原本は `R5_fdm_ad_on_*` の三計算について PDOS と XAS を平均し、共通するスペクトル構造を比較する用途でした。

**現行版の入出力**
複数の SD ファイルと必要に応じて同数の畳み込み XAS を読み、平均図 `Fe_average.pdf` を保存します。各系列の内部で格子が一致する必要があります。

**実行例**

```bash
python fdPDOS_XAS_av.py Fe_1_sd0.txt Fe_2_sd0.txt --year 2020 --sp --xas-files Fe_1_conv.txt Fe_2_conv.txt -o Fe_average.pdf
```

**原本からの変更点**
SD ファイルを省略すると原本の三計算を使用し、`--xas` で畳み込み、`--broad` で生 XAS も重ねます。SD ファイルを明示する場合は対応する `--xas-files`・`--raw-xas-files` を指定できます。フェルミ基準は `--fermi` で選び、明示指定のときはエネルギー基準を判定するための `--input` も渡します。

### `fdXAS.py`

**原本の用途**
畳み込み XAS を単独で描く簡単な例です。図のスタイルや曲線を追加する際の出発点になります。

**現行版の入出力**
`Fe_conv.txt` 内のエネルギーと第1吸収列を SAE 原版の配置で描き、0 eV にフェルミ準位の縦線を表示します。入力は位置引数または `-i` で指定できます。省略時は `POSCAR_conv.txt`、または作業ディレクトリ内の唯一の `*_conv.txt` を読みます。`-o` を省くと `XAS.pdf` です。

**実行例**

```bash
python fdXAS.py -i Fe_conv.txt -o Fe_XAS.pdf
```

**原本からの変更点**
入力の `-i` は原本を継承し、出力名の `-o` を追加しました。読み込みと作図は `FdmConv` と `PlotFdmXas` が担当します。

### `fdXAS_specified.py`

**原本の用途**
原本は Au の畳み込みスペクトルを題材に、生 XAS ヘッダのフェルミ値で横軸の原点を合わせます。

**現行版の入出力**
接頭辞 `Fe` から `Fe.txt` と `Fe_conv.txt` を読み、畳み込みのエネルギーから `E_Fermi` を引いて `Fe_fermi.pdf` に描きます。

**実行例**

```bash
python fdXAS_specified.py -i Fe -o Fe_fermi.pdf
```

**原本からの変更点**
フェルミ値だけを引く原本の軸変換を継承しました。現行版では対象の接頭辞と図の保存先を指定できます。
