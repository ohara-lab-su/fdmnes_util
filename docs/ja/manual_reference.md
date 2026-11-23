# 手書き API リファレンス

`src/fdmnes_util` のクラスを、Python から直接呼び出すための手書きリファレンスです。各クラスの import 文、全公開メソッドの引数・既定値・戻り値と、各クラスの短い使用例を記載しています。全シグネチャと docstring は [Sphinx 自動生成 API](api/index.md)、コマンドとしての実行例は [スクリプトガイド](scripts.md) を参照してください。

`=` のある引数は既定値付きです。`*` の後はキーワード専用です。`__init__` は初期化メソッドで、クラス名で呼び出した式はインスタンスを返します。`ndarray` は NumPy の配列、`Path` は `pathlib.Path` です。例のファイル名は手元の計算・実験データに置き換えてください。

## 計算入力とジョブ一覧

### `FdmInp`

`from fdmnes_util.fdm_inp import FdmInp`

計算入力を読み込み、計算条件の取得や新しい入力の生成を行います。

入力には改訂行がないため、`FdmInp(filename, format_year=2026)` で拡張形式を選びます。既定は2016です。`get_absorbers()` はサイト番号のリスト、`get_calculations()` は（ファイル名、重み、シフト、カットオフ）のリストを返します。`FdmInp.write(..., format_year=2026)` では `absorber=[1, 2]`、`density_complex=True`、`lmax_dosout=3` を指定できます。`FdmInp.write_convolution(filename, calculations, *, output, format_year=2026, header=False, energy_step=None, per_atom=False)` で複数サイトの畳み込み入力を作れます。`calculations` は生 XAS のファイル名・重み・シフト（eV）の組です。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename='read_pdb.inp', *, format_year=2016)` | filename は計算入力ファイル。 | None |
| `from_text(text)` | Python で組み立てた入力本文。 | 編集可能な `FdmInp`。 |
| `from_poscar(filename, *, molecule=False)` | POSCAR のパス。`molecule=True` で分子構造節を作る。読み込みには `vasp_util` が必要。 | 編集可能な `FdmInp`。 |
| `set_block(keyword, *rows, old_rows=None)` | キーワードとデータ行。可変長ブロックを置換するときは、元のデータ行数を `old_rows` に指定。 | 更新した `FdmInp`。 |
| `remove_block(keyword, *, old_rows=None)` | 削除するキーワード。可変長ブロックでは元のデータ行数を指定。 | 更新した `FdmInp`。 |
| `set_radius(radius, *changes)` | 半径（Å）。追加の組は切替エネルギー（eV）と切替後の半径（Å）。 | 更新した `FdmInp`。 |
| `render_input()` | — | str。編集中の入力本文。 |
| `save(filename, *, overwrite=False)` | 保存先。既存ファイルを置き換える場合は `overwrite=True`。 | Path。そのまま `FdmRun.run()` に渡せる保存先。 |
| `get_filout()` | — | str。最後の `Filout` または `File_out` の値。未指定なら空文字列。 |
| `get_absorber()` | — | int。最後の `Absorber` で指定した1始まりの吸収原子番号。未指定なら 1。不正な番号は ValueError。 |
| `get_ispin()` | — | int。`Spin` または `Magnetism` があれば 2、なければ 1。 |
| `get_allsite()` | — | bool。`Allsite` の有無。 |
| `get_energygpho()` | — | bool。`Energpho` または `Energygpho` の有無。 |
| `get_nonexc()` | — | bool。`Nonexc` の有無。 |
| `get_convolution()` | — | bool。`Convolution` の有無。 |
| `get_conv_out()` | — | str。`Conv_out` の値。未指定なら空文字列。 |
| `get_calculation()` | — | str。最後の `Calculation` ブロックの先頭ファイル名。未指定なら空文字列。 |
| `get_cellparam()` | — | list[float] または None。結晶の格子長 3 個と角度 3 個。 |
| `get_crystal_atoms()` | — | ase.Atoms。周期構造。 |
| `get_molecule_atoms()` | — | ase.Atoms。非周期構造。分率・円筒・球座標の入力に対応。 |
| `render(absorber: int=1, fileout: str='Cu', energy_range: str='-15. 0.2  0. 0.5 10. 1. 45.', edge: str='K', radius: float=5, molecule: bool=False, structure_writer=None)` (静的) | absorber は吸収原子番号、fileout は結果の接頭辞、energy_range は eV 単位の格子指定、edge は吸収端名、radius は半径（Å）、molecule は分子指定、structure_writer は構造節を生成するオブジェクト。structure_writer を省くと ValueError。 | str。構造節を含む計算入力。 |
| `write(filename: str \| Path='read_pdb.inp', **kwargs)` (静的) | filename は保存先。kwargs は render() に渡す引数で、既定値も共通。 | Path。保存先。 |

**使用例**

```python
from fdmnes_util.fdm_inp import FdmInp
inp = FdmInp("read_pdb.inp")
prefix = inp.get_filout()
absorber = inp.get_absorber()
```

### `Fdmfile`

`from fdmnes_util.fdmfile import Fdmfile`

FDMNES のジョブ一覧を読み書きし、計算入力を選びます。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename='fdmfile.txt')` | filename はジョブ一覧ファイル。 | None |
| `get_filout()` | — | str。先頭ジョブの入力ファイル名。空の一覧では空文字列。 |
| `select_input(filename: str \| Path \| None=None)` (クラスメソッド) | filename は明示する計算入力。None なら作業ディレクトリの fdmfile.txt の先頭ジョブ、一覧がなければ read_pdb.inp。 | Path。選択された入力ファイル。 |
| `write(filenames, filename='fdmfile.txt')` (静的) | filenames は入力ファイル名の並び、filename は一覧の保存先。 | Path。保存先。 |

**使用例**

```python
from fdmnes_util.fdmfile import Fdmfile
jobs = Fdmfile("fdmfile.txt")
first_input = jobs.get_filout()
```

### `FdmRun`

`from fdmnes_util.fdm_run import FdmRun`

作業ディレクトリの `fdmfile.txt` を使って FDMNES 本体を起動します。標準出力は画面と `fdmnes-*.log` に流し、計算結果ファイルは本体が `Filout` に従って書き出します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(executable='fdmnes', *, echo=True)` | 実行ファイルのパスまたはコマンド名。`echo` は既存の呼び出しとの互換用。 | None |
| `run(input_file=None, *, directory=None, timeout=None)` | 入力を指定すると一覧に1件だけ登録して実行。省略時は既存一覧を使う。作業ディレクトリの既定はカレント。制限時間は秒。 | subprocess.CompletedProcess |
| `run_fdmfile(*, directory=None, timeout=None)` | 指定先またはカレントの `fdmfile.txt` をそのまま使う。制限時間は秒。 | subprocess.CompletedProcess |
| `run_inputs(input_files, *, directory, timeout=None)` | Python で並べた入力を1件ずつ実行。制限時間は全件に適用。 | list[subprocess.CompletedProcess]。指定順の終了結果。 |

入力の準備から計算までの例は[使い方](usage.md)を参照してください。

## XAS・実験スペクトル

### `FdmTxt`

`from fdmnes_util.fdm_txt import FdmTxt`

生 XAS とヘッダにある吸収端・フェルミ値を扱います。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename)` | filename は生 XAS ファイル。 | None |
| `get_eng()` | — | ndarray。ファイルに記録されたエネルギー軸。 |
| `get_xas(spin=0)` | spin は 0 始まりの吸収列番号。 | ndarray。吸収強度。 |
| `get_xas_all()` | — | ndarray。エネルギー点×吸収列の行列。 |
| `get_edge_xas(edge, spin=0)` | edge はヘッダの吸収端ラベル（例 L3）、spin はその吸収端内の 0 始まりの列番号。 | ndarray。指定列の吸収強度。列がなければ ValueError。 |
| `get_eedge()` | — | float または None。吸収端エネルギー（eV）。 |
| `get_efermi()` | — | float。フェルミエネルギー（eV）。ヘッダに値がなければ 0.0。 |
| `write_spectrum(filename, metadata, spectrum)` (静的) | filename は保存先、metadata は生 XAS のヘッダ先頭行、spectrum は元のエネルギー基準での (energy, intensity)。 | None。ヘッダ付き二列ファイルを保存。 |

**使用例**

```python
from fdmnes_util.fdm_txt import FdmTxt
raw = FdmTxt("Fe.txt")
energy, intensity = raw.get_eng(), raw.get_xas()
edge = raw.get_eedge()
```

### `FdmConv`

`from fdmnes_util.fdm_conv import FdmConv`

畳み込み後の XAS を読み書きします。

畳み込み出力は `FdmConv(filename, format_year=None)` で読みます。2026年11月5日版の `Header` 改訂行を検出した場合は2026、それ以外の通常形式は2016を使います。`format_year=2016` または `2026` で明示できます。2026形式では `preamble`、`parameters`、`shifts` に付加情報を保持します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename, *, format_year=None)` | filename は畳み込み XAS ファイル。 | None |
| `get_eng()` | — | ndarray。ファイルに記録されたエネルギー軸。 |
| `get_xas(spin=0)` | spin は 0 始まりの吸収列番号。 | ndarray。吸収強度。 |
| `write_spectrum(filename, spectrum)` (静的) | filename は保存先、spectrum は元のエネルギー基準での (energy, intensity)。 | None。二列ファイルを保存。 |

**使用例**

```python
from fdmnes_util.fdm_conv import FdmConv
conv = FdmConv("Fe_conv.txt")
energy, intensity = conv.get_eng(), conv.get_xas()
```

### `AthenaNor`

`from fdmnes_util.athena_nor import AthenaNor`

Athena の正規化済み実験スペクトルを読みます。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename)` | filename は Athena の正規化済み .nor ファイル。 | None |
| `get_eng()` | — | ndarray。光子エネルギー。 |
| `get_nor()` | — | ndarray。正規化吸収強度。 |

**使用例**

```python
from fdmnes_util.athena_nor import AthenaNor
measured = AthenaNor("Fe_obs.txt.nor")
photon_energy, normalized = measured.get_eng(), measured.get_nor()
```

### `FdmPhotoenergy`

`from fdmnes_util.fdm_photoenergy import FdmPhotoenergy`

変換済みの吸収スペクトルを光子エネルギーの二列表として保存します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `write(energy, intensity, filename)` | energy は光子エネルギー（eV）、intensity は吸収強度。両方とも同じ長さの一次元配列。filename は保存先。 | Path。二列ファイルの保存先。 |

**使用例**

```python
from fdmnes_util.fdm_photoenergy import FdmPhotoenergy
output = FdmPhotoenergy().write([7112.0, 7113.0], [0.2, 0.5], "Fe_conv_photoe.txt")
```

## SD と BAV の形式選択

### `FdmSd`

`from fdmnes_util.fdm_sd import FdmSd`

SD ファイルの形式を選択し、対応するリーダーを作ります。2019年Cuのように改訂年とSDの列構成が対応しない場合があります。ファイルを判定するには `format_year=None` を指定します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename, *, format_year, ispin=1, weight=None)` | filename は SD ファイル、format_year は 2016、2020、2026、または列名で判定する場合は None、ispin は 2016 形式のスピン数、weight は密度・積分列の除数（None なら除算なし）。 | None |
| `select_reader()` | — | FdmSd2016、FdmSd2020、または FdmSd2026。 |
| `format_from_bav(filename)` (静的) | filename は同じ計算の BAV ファイル。改訂年から推定する従来のメソッド。 | int。2016 または 2020。未検証のリビジョンでは ValueError。 |
| `write_table(filename, columns, grid, densities)` (静的) | filename は保存先、columns はエネルギー列から始まる列名、grid は一次元のエネルギー軸、densities はエネルギー列を除く二次元の値。 | None。SD 表を保存。 |

**使用例**

```python
from fdmnes_util.fdm_sd import FdmSd
sd = FdmSd("Fe_sd0.txt", format_year=None).select_reader()
energy, p_ldos = sd.get_eng(), sd.get_ldos("p")
```

### `FdmSd2016`

`from fdmnes_util.fdm_sd_2016 import FdmSd2016`

2016 年形式の SD から、スピン・軌道ごとの状態密度を読みます。

`spin` は 0 または 1（2 スピンの場合）です。0 には `up`・`non`・`nonmag`、1 には `dn`・`down` も使えます。軌道群名は s・p・d・f です。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename, *, ispin=1, weight=None)` | filename は 2016 形式の SD、ispin は 1 または 2、weight は密度・積分列の除数（None なら除算なし）。 | None |
| `get_densities()` | — | ndarray。エネルギー列を除いた密度・積分値の行列。列順はファイルと同じ。 |
| `get_eng()` | — | ndarray。エネルギー軸（eV）。 |
| `get_lmax()` | — | int。最大軌道角運動量番号。 |
| `get_ispin()` | — | int。スピンチャネル数。 |
| `get_ldos(l=0, spin=0)` | l は軌道群名または角運動量番号、spin はスピン指定。 | ndarray。軌道群の密度。 |
| `get_intldos(l=0, spin=0)` | l は軌道群名または角運動量番号、spin はスピン指定。 | ndarray。軌道群の積分値。 |
| `get_pdos(l=0, m=0, lm=None, spin=0)` | l、m は軌道の量子数。lm に軌道名（例 p_z）を渡すと l、m を上書き。spin はスピン指定。 | ndarray。個別軌道への射影密度。 |
| `get_tdos(spin=0)` | spin はスピン指定。 | ndarray。軌道群の密度の合計。 |
| `get_inttdos(spin=0)` | spin はスピン指定。 | ndarray。先頭の積分列と軌道群の積分値の合計。 |

**使用例**

```python
from fdmnes_util.fdm_sd_2016 import FdmSd2016
sd = FdmSd2016("Fe_2016_sd0.txt", ispin=1)
energy, s_ldos = sd.get_eng(), sd.get_ldos("s")
```

### `FdmSd2020`

`from fdmnes_util.fdm_sd_2020 import FdmSd2020`

2020 年形式の SD から、軌道ごとの状態密度を読みます。

非磁性の列形式と、2021年・2026年の Ni 実出力で確認した磁性の31列形式に対応します。`spin` は 0（`up`・`non`・`nonmag`）、磁性では 1（`dn`・`down`）も指定できます。`total` と `Int(total)` は全スピン共通です。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename, *, weight=None)` | filename は 2020 形式の SD、weight は密度・積分列の除数（None なら除算なし）。 | None |
| `get_densities()` | — | ndarray。エネルギー列を除いた密度・積分値の行列。列順はファイルと同じ。 |
| `get_eng()` | — | ndarray。エネルギー軸（eV）。 |
| `get_lmax()` | — | int。最大軌道角運動量番号。 |
| `get_ispin()` | — | int。スピンチャネル数。 |
| `get_ldos(l=0, spin=0)` | l は軌道群名または角運動量番号、spin はスピン指定。 | ndarray。軌道群の密度。 |
| `get_intldos(l=0, spin=0)` | l は軌道群名または角運動量番号、spin はスピン指定。 | ndarray。軌道群の積分値。 |
| `get_pdos(l=0, m=0, lm=None, spin=0)` | l、m は軌道の量子数。lm に軌道名（例 p_z）を渡すと l、m を上書き。spin はスピン指定。 | ndarray。個別軌道への射影密度。 |
| `get_tdos(spin=0)` | spin は指定の有効性の検査に使います。全スピン共通の列を返します。 | ndarray。ファイルに格納された全 DOS。 |
| `get_inttdos(spin=0)` | spin は指定の有効性の検査に使います。全スピン共通の列を返します。 | ndarray。ファイルに格納された全 DOS の積分値。 |

**使用例**

```python
from fdmnes_util.fdm_sd_2020 import FdmSd2020
sd = FdmSd2020("Fe_sd0.txt")
energy, pz_pdos = sd.get_eng(), sd.get_pdos(lm="p_z")
```

### `FdmSd2026`

複素基底または f 軌道列を含む SD を読みます。共通の入口では `FdmSd(filename, format_year=None)` で列名を判定し、`format_year=2026` でも指定できます。複素射影は `get_pdos(l=3, m=0)`、実 f 軌道は `get_pdos(lm="fxyz")`、f 軌道群は `get_ldos(l=3)` で取得します。通常の s・p・d 列は2026年版の出力でも従来のリーダーを使います。

### `FdmBav`

`from fdmnes_util.fdm_bav import FdmBav`

BAV のリビジョンを読み、対応するリーダーを選びます。

BAV レコードは年別リーダーが解析します。`FdmBav` は改訂行からリーダーを選び、`get_edge()` などの共通13メソッドを同名のメソッドへ委譲します。入口から直接呼ぶ場合は、最初の呼び出しで選んだリーダーを再利用します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename)` | filename は BAV ログ。revision と year を取得。 | None |
| `select_reader()` | — | 2016年以前は FdmBav2016、2017〜2021年は FdmBav2020、2026年11月5日版は FdmBav2026。その他の2022年以降の版は ValueError。 |
| `get_scf_history()` | — | list[tuple[int, float \| None]]。2026年版のサイクル番号と全エネルギー（eV）。計算途中の未記録値は None。対応する履歴を読めない場合は空リスト。 |

**使用例**

```python
from fdmnes_util.fdm_bav import FdmBav
bav = FdmBav("Fe_bav.txt")
print(bav.year, bav.get_edge())
```

### `FdmBav2016`

`from fdmnes_util.fdm_bav_2016 import FdmBav2016`

2016 年形式の BAV ログから計算条件やクラスタ情報を取り出します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename)` | filename は対象年形式の BAV ログ。 | None |
| `get_edge()` | — | str。吸収端ラベル。記録がなければ空文字列。 |
| `get_nspin()` | — | int。スピン数（1 または 2）。 |
| `is_self_consistent()` | — | bool。自己無撞着計算の記録の有無。 |
| `get_max_scf_iterations()` | — | int または None。SCF 反復上限。 |
| `get_n_scf_loop()` | — | int。ログの最後の SCF サイクル番号。記録がなければ 0。 |
| `get_scf_toten()` | — | list[float]。SCF 記録ごとの単位胞エネルギー。 |
| `get_position()` | — | ndarray。クラスタの直交座標。 |
| `get_atoms_index_j()` | — | list[str]。クラスタの原子順の元素記号。 |
| `get_natom()` | — | int。クラスタの原子数。 |
| `get_e_edge()` | — | float または None。吸収端エネルギー。 |
| `get_ngroup()` | — | int または None。原子グループの数。 |
| `get_t()` | — | ndarray または None。結晶基底の 3×3 変換行列。 |
| `get_lmax()` | — | int または None。原子リスト中の最大軌道角運動量番号。 |

**使用例**

```python
from fdmnes_util.fdm_bav_2016 import FdmBav2016
log = FdmBav2016("Fe_2016_bav.txt")
edge, last_cycle = log.get_edge(), log.get_n_scf_loop()
```

### `FdmBav2020`

`from fdmnes_util.fdm_bav_2020 import FdmBav2020`

2020 年形式の BAV ログから計算条件やクラスタ情報を取り出します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename)` | filename は対象年形式の BAV ログ。 | None |
| `get_edge()` | — | str。吸収端ラベル。記録がなければ空文字列。 |
| `get_nspin()` | — | int。スピン数（1 または 2）。 |
| `is_self_consistent()` | — | bool。自己無撞着計算の記録の有無。 |
| `get_max_scf_iterations()` | — | int または None。SCF 反復上限。 |
| `get_n_scf_loop()` | — | int。ログの最後の SCF サイクル番号。記録がなければ 0。 |
| `get_scf_toten()` | — | list[float]。SCF 記録ごとの単位胞エネルギー。 |
| `get_position()` | — | ndarray。クラスタの直交座標。 |
| `get_atoms_index_j()` | — | list[str]。クラスタの原子順の元素記号。 |
| `get_natom()` | — | int。クラスタの原子数。 |
| `get_e_edge()` | — | float または None。吸収端エネルギー。 |
| `get_ngroup()` | — | int または None。原子グループの数。 |
| `get_t()` | — | ndarray または None。結晶基底の 3×3 変換行列。 |
| `get_lmax()` | — | int または None。原子リスト中の最大軌道角運動量番号。 |

**使用例**

```python
from fdmnes_util.fdm_bav_2020 import FdmBav2020
log = FdmBav2020("Fe_bav.txt")
symbols, positions = log.get_atoms_index_j(), log.get_position()
```

### `FdmBav2026`

`from fdmnes_util.fdm_bav_2026 import FdmBav2026`

2026年11月5日版の BAV を読みます。公開読み取りメソッドは `FdmBav2016`・`FdmBav2020` と同じです。サイクル別の全エネルギー履歴は共通の入口 `FdmBav` から取得します。

```python
from fdmnes_util.fdm_bav import FdmBav
log = FdmBav("Fe_SCF_bav.txt")
history = log.get_scf_history()
```

## 構造の入出力

### `Cif`

`from fdmnes_util.cif import Cif`

CIF の格子と原子座標を ASE 経由で読みます。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(path: str \| Path)` | path は構造ファイルのパス。ASE が必要。 | None |
| `get_symbols()` | — | list[str]。原子順の元素記号。 |
| `get_lattice_vectors()` | — | ndarray。行に格子ベクトルを並べた 3×3 配列（Å）。 |
| `get_direct_positions()` | — | ndarray。原子順の分率座標。 |
| `get_cartesian_positions()` | — | ndarray。原子順の直交座標（Å）。 |

**使用例**

```python
from fdmnes_util.cif import Cif
cell = Cif("Fe.cif")
symbols, lattice = cell.get_symbols(), cell.get_lattice_vectors()
```

### `Pdb`

`from fdmnes_util.pdb import Pdb`

PDB の格子と原子座標を ASE 経由で読みます。

`CRYST1` がないと `molecule` が真になります。格子ベクトルと分率座標は周期構造用です。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(path: str \| Path)` | path は構造ファイルのパス。ASE が必要。 | None |
| `get_symbols()` | — | list[str]。原子順の元素記号。 |
| `get_cartesian_positions()` | — | list[tuple[float, float, float]]。原子順の直交座標（Å）。 |
| `get_lattice_vectors()` | — | ndarray。行に格子ベクトルを並べた 3×3 配列（Å）。 |
| `get_direct_positions()` | — | ndarray。原子順の分率座標。 |

**使用例**

```python
from fdmnes_util.pdb import Pdb
pdb = Pdb("Fe.pdb")
symbols, coordinates = pdb.get_symbols(), pdb.get_cartesian_positions()
```

### `Xyz`

`from fdmnes_util.xyz import Xyz`

標準 XYZ の元素記号と直交座標を読み書きします。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filename: str \| Path)` | filename は標準 XYZ。symbols と positions に元素記号と直交座標を格納。 | None |
| `read()` | インスタンスに設定した filename を再読み込みし、symbols と positions を更新。 | None |
| `render(symbols, positions)` (静的) | symbols は元素記号の並び、positions は対応する直交座標（Å）。 | str。末尾改行を含む XYZ。 |
| `write(symbols, positions, filename)` (クラスメソッド) | symbols と positions は render() と共通。filename は保存先。 | Path。XYZ の保存先。 |

**使用例**

```python
from fdmnes_util.xyz import Xyz
cluster = Xyz("cluster.xyz")
symbols, positions = cluster.symbols, cluster.positions
```

### `ElementTable`

`from fdmnes_util.fdm_structure import ElementTable`

構造データに含まれる原子番号と元素記号を相互に引きます。

| メソッド | 引数 | 戻り値 |
| --- | --- | --- |
| `get_atomic_symbol0(num)` | 原子番号。 | str。元素記号。 |
| `get_atomic_number1(atom)` | 元素記号。 | int。原子番号。 |

### `FdmStructure`

`from fdmnes_util.fdm_structure import FdmStructure`

格子と原子座標を FDMNES の構造節に変換します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(structure)` | structure は `vasp_util.vasp_poscar.VaspPoscar`、または元素記号・格子ベクトル・分率座標を取得できる `Cif`・`Pdb` などのリーダー。 | None |
| `fdm_to_atoms(filename, *, vacuum=10.0)` (静的) | FDMNES 入力パス。vacuum は分子の各側に設ける真空層の厚さ（Å）。 | ase.Atoms。POSCAR 書き出し用の構造。 |
| `poscar_to_atoms(filename)` (静的) | vasp_util で読む POSCAR のパス。 | ase.Atoms。元の格子と原子順を持つ周期構造。 |
| `crystal_atoms(cell_values, atom_lines)` (静的) | 格子の長さ・角度6要素と、原子番号・分率座標の各行。 | ase.Atoms。周期境界を持つ結晶構造。 |
| `molecule_atoms(lines)` (静的) | 分子のスケールと原子座標の行。 | ase.Atoms。直交座標を Å で持つ孤立分子。 |
| `render(molecule: bool=False)` | molecule が True のとき Molecule、False のとき Crystal を選択。 | str。FDMNES 構造節。 |
| `render_xyz_molecule(symbols: list[str], positions: list[tuple[float, float, float]])` (静的) | symbols は元素記号の並び、positions は対応する直交座標（Å）。 | str。XYZ 座標から生成した Molecule 節。 |
| `write(filename: str \| Path, molecule: bool=False)` | filename は保存先、molecule は Molecule の選択。 | Path。構造節の保存先。 |

**使用例**

```python
from fdmnes_util.fdm_structure import FdmStructure
from vasp_util.vasp_poscar import VaspPoscar

structure = FdmStructure(VaspPoscar("POSCAR"))
output = structure.write("Fe.fdmnes")
```

## 数値解析

### `AnalyzeFdmAverage`

`from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage`

共通のエネルギー格子上で複数計算の結果を平均します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `energy_reference(input_file, spectrum, fermi=False)` | input_file は FdmInp、spectrum はヘッダを持つ FdmTxt、fermi はフェルミ基準の指定（False なら光子エネルギー基準）。 | tuple[float, float]。軸の移動量と光子エネルギー基準のフェルミ位置（eV）。 |
| `average(readers, value_method, *, divisor=None, **kwargs)` | readers は空でないリーダーの並び、value_method は取得メソッド名、divisor は正の除数（None ならリーダー数）、kwargs は取得メソッドへの引数。エネルギー格子の許容誤差は 1e-8 eV。 | tuple[ndarray, ndarray]。共通格子と指定値の合計を除数で割った配列。 |

**使用例**

```python
from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage
from fdmnes_util.fdm_conv import FdmConv

readers = [FdmConv("Fe_1_conv.txt"), FdmConv("Fe_2_conv.txt")]
energy, mean_xas = AnalyzeFdmAverage().average(readers, "get_xas")
```

### `AnalyzeFdmXas`

`from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas`

生・畳み込み XAS の平均、軸変換、サイト別の読み出しを行います。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `average(spectra, weights=None)` (静的) | spectra は同一格子の生または畳み込みリーダー、weights はスペクトルごとの相対重み（None なら等重み）。 | tuple[ndarray, ndarray]。エネルギー軸と第 1 吸収列の平均。 |
| `photon_energy(convolution, raw_xas, *, subtract_fermi=False, fermi_energy=None)` (静的) | convolution は FdmConv、raw_xas は吸収端を持つ FdmTxt。subtract_fermi が True の場合は fermi_energy（eV）も指定。 | tuple[ndarray, ndarray]。変換後の格子と畳み込み強度。 |
| `fermi_relative_convolution(convolution, raw_xas)` (静的) | convolution は FdmConv、raw_xas はフェルミ値の取得元となる FdmTxt。 | tuple[ndarray, ndarray]。フェルミ値を引いた格子と強度。 |
| `energy_reference(energy, raw_xas, *, input_is_photon, fermi)` (静的) | energy は変換前の格子、raw_xas は FdmTxt、input_is_photon は元の軸が光子エネルギーか、fermi は出力をフェルミ基準にするか。 | ndarray。変換後の格子（eV）。 |
| `site_spectra(base_name, site_indices, *, convolved=True, input_is_photon=None, fermi=None)` (クラスメソッド) | base_name は Filout、site_indices は重複しない 1 始まりのサイト番号、convolved は畳み込み選択。軸を変換する場合は input_is_photon と fermi を両方指定。 | list[tuple]。指定順の (energy, intensity, label)。 |

**使用例**

```python
from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_txt import FdmTxt

conv, raw = FdmConv("Fe_conv.txt"), FdmTxt("Fe.txt")
energy, intensity = AnalyzeFdmXas.photon_energy(conv, raw)
```

## 描画

描画には Matplotlib が必要です。スペクトルを配列で渡す API では、各曲線のエネルギーと値の長さをそろえ、比較する曲線を同じエネルギー基準に変換します。作図メソッドは保存先の `Path` を返し、複数形式へ保存する `save_multiple_formats()` は `Path` のリストを返します。

### `PlotFdmXas`

`from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas`

計算 XAS を描画し、実験やサイト別のデータと比較します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `plot_convolved(eng, xas, output, *, specified=False)` | eng はフェルミ準位基準のエネルギー、xas は畳み込み強度、output は保存先。specified は SAE の `fdXAS_specified.py` の目盛りと凡例の指定。 | Path。図の保存先。 |
| `plot(spectra, output, *, title=None, xlabel='Energy (eV)', ylabel='XAS', xmin=None, xmax=None, ymax=None, fermi_position=None)` | spectra は (energy, intensity, label) の並び、output は保存先。title は見出し、xlabel と ylabel は軸ラベル、xmin・xmax・ymax は軸の範囲、fermi_position は縦線の位置（eV）。 | Path。図の保存先。 |
| `plot_sites(spectra, output, *, observed=None, xmin=None, xmax=None, ymax=None, fermi=False, fermi_position=None, extra_formats=False)` | spectra と observed は計算・実験それぞれの (energy, intensity, label) の並び。output は保存先、xmin・xmax・ymax は軸の範囲、fermi は軸がフェルミ基準か、fermi_position は縦線の位置、extra_formats は EPS・PDF・PNG の追加保存。 | Path。サイト比較図の保存先。 |
| `plot_experiment_comparison(calculated_energy, calculated_absorption, observed_energy, observed_absorption, output, *, xmin=None, xmax=None, ymin=0.0, ymax=None)` | calculated_energy と calculated_absorption は計算の軸と強度、observed_energy と observed_absorption は実験の軸と強度。output は保存先、xmin・xmax・ymin・ymax は表示範囲。 | Path。計算と実験を重ねた図の保存先。 |
| `plot_composite(spectra, output, *, observed=None, dos=(), xlabel='Photon Energy [eV]', ylabel='Absorption [arb. unit]', xmin=None, xmax=None, ymax=None, dmax=None, fermi_position=None, extra_formats=False, show=False)` | spectra は計算曲線の並び、observed は実験曲線 1 本、dos は LDOS 曲線の並び。各曲線は (energy, value, label)。output は保存先、xlabel・ylabel はラベル、xmin・xmax・ymax・dmax は軸の範囲、fermi_position は縦線。extra_formats は PDF・EPS・PNG の追加保存、show は画面表示、shade_occupied はフェルミ準位より下の LDOS を塗り分けます。 | Path。主図の保存先。 |

**使用例**

```python
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
from fdmnes_util.fdm_conv import FdmConv

conv = FdmConv("Fe_conv.txt")
output = PlotFdmXas().plot([(conv.get_eng(), conv.get_xas(), "Fe")], "Fe_XAS.pdf")
```

### `PlotFdmDos`

`from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos`

軌道群や個別軌道の状態密度を描画します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `plot_local(reader, output, *, orbit=1, integrated=False)` | reader は SD リーダー、output は保存先、orbit は軌道角運動量の番号、integrated は積分 LDOS を選択。SAE の `fdLDOS.py` と同じ配置で描きます。 | Path。図の保存先。 |
| `plot_single_orbital(reader, output, *, orbital='p', emin=None, emax=None, dmax=None, edge_offset=0.0, fermi_position=0.0, divisor=None, extra_outputs=())` | reader は SD リーダーまたは複数サイトのリーダーの並び、output は保存先、orbital は軌道群、emin・emax・dmax は軸の範囲、edge_offset は軸に加える値、fermi_position は縦線の位置、divisor は複数サイトの和の除数、extra_outputs は追加の保存先。 | Path。図の保存先。 |
| `plot_occupied_ldos(reader, output, *, orbital='p', edge_offset=0.0, fermi_position=0.0, emin=None, emax=None, dmax=None)` | reader は SD リーダー、output は保存先、orbital は軌道群、edge_offset は軸に加える値、fermi_position は塗り分けの境界、emin・emax・dmax は軸の範囲。 | Path。占有側を塗った図の保存先。 |
| `plot(reader, output, orbitals=('s', 'p', 'd'), *, integrated=False)` | reader は SD リーダー、output は保存先、orbitals は軌道群の並び、integrated は積分列を選択。 | Path。図の保存先。 |
| `save_multiple_formats(readers, labels, output_prefix, *, formats=('eps', 'pdf', 'png'), edge_energy, fermi_energy, orbital='p', emin=None, emax=None)` | readers と labels は 3 サイト分の SD リーダーとラベル、output_prefix は保存名、formats は拡張子の並び。edge_energy と fermi_energy は吸収端とフェルミ値（eV）、orbital は軌道群、emin・emax は軸の範囲。 | list[Path]。指定形式の保存先。 |
| `plot_multiple_sites(readers, labels, output, *, edge_energy, fermi_energy, orbital='p', emin=None, emax=None)` | readers と labels は 3 サイト分の SD リーダーとラベル、output は保存先。edge_energy と fermi_energy は吸収端とフェルミ値（eV）、orbital は軌道群、emin・emax は軸の範囲。 | Path。3 サイトの図の保存先。 |
| `plot_three_calculations(readers, fermi_energies, labels, output, *, orbital='p', emin=None, emax=None, density_max=5.0, extra_outputs=())` | readers・fermi_energies・labels は 3 計算分のリーダー・フェルミ値・ラベル。output は保存先、orbital は軌道群、emin・emax・density_max は軸の範囲、extra_outputs は追加の保存先。 | Path。フェルミ基準で比較する図の保存先。 |
| `plot_composite(reader, output, *, groups, spins=(0,), spin_labels=('', ''), projected=False, integrated=False, xas=(), shift=0.0, fermi_position=0.0, xlabel='Photon Energy [eV]', limits=(None, None), density_max=None, orbital_max=None, xas_max=None, label='0', extra_formats=False, show=False, shade_occupied=False)` | reader は SD リーダー、output は保存先。groups は下から並べる軌道名のグループ、spins は各群のスピン順、spin_labels はスピン別の接尾辞。projected は PDOS の選択、integrated は LDOS の積分軸、xas は (energy, intensity, label) の並び。shift は SD 軸だけの移動量、fermi_position は縦線、xlabel は軸ラベル。limits はエネルギー範囲、density_max は DOS 上限、orbital_max は軌道群別上限の辞書、xas_max は XAS 上限、label は曲線ラベル。extra_formats は PDF・EPS・PNG の追加保存、show は画面表示、shade_occupied はフェルミ準位より下の LDOS を塗り分けます。 | Path。主図の保存先。 |

**使用例**

```python
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos
from fdmnes_util.fdm_sd_2020 import FdmSd2020

sd = FdmSd2020("Fe_sd0.txt")
output = PlotFdmDos().plot_single_orbital(sd, "Fe_LDOS.pdf", orbital="p")
```

### `PlotFdmXasLdos`

`from fdmnes_util.plot.plot_fdm_xas_ldos import PlotFdmXasLdos`

XAS と軌道別 LDOS を組み合わせて表示します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `plot(xas, orbital_spectra, output, *, fermi_position=None, fermi=False)` | xas は (energy, intensity)、orbital_spectra は (orbital, energy, LDOS) の並び、output は保存先。fermi_position は縦線、fermi は軸がフェルミ基準かを指定。 | Path。XAS と軌道別 LDOS の図の保存先。 |
| `plot_experiment_ldos(*, calculated_energy, calculated_absorption, raw_energy, raw_absorption, observed_energy, observed_absorption, ldos_energy, ldos_density, fermi_energy, output, xmin=None, xmax=None)` | calculated_energy・calculated_absorption は畳み込み XAS の軸と強度、raw_energy・raw_absorption は生 XAS、observed_energy・observed_absorption は実験、ldos_energy・ldos_density は LDOS の軸と値。fermi_energy は図に用いるフェルミ位置、output は保存先、xmin・xmax はエネルギー範囲。 | Path。XAS・実験・LDOS の二段図の保存先。 |

**使用例**

```python
from fdmnes_util.plot.plot_fdm_xas_ldos import PlotFdmXasLdos
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_sd_2020 import FdmSd2020

conv, sd = FdmConv("Fe_conv.txt"), FdmSd2020("Fe_sd0.txt")
xas = (conv.get_eng(), conv.get_xas())
ldos = [("p", sd.get_eng(), sd.get_ldos("p"))]
output = PlotFdmXasLdos().plot(xas, ldos, "Fe_XAS_LDOS.pdf")
```

### `PlotFdmAverage`

`from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage`

平均 PDOS と任意の XAS を多段の図に描きます。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `plot(orbital_data, output, *, xas_data=None, raw_xas_data=None, emin=None, emax=None, dmax=None, ymax=None, energy_offset=0.0, orbital_groups=None, fermi_position=None, xlabel='Photon Energy [eV]', extra_formats=False, show=False)` | orbital_data は (label, energy, DOS) の並び、output は保存先。xas_data・raw_xas_data は畳み込み・生 XAS の (energy, intensity) で、生 XAS には畳み込み XAS も必要。emin・emax・dmax・ymax は各軸の範囲。energy_offset は全系列への軸の移動量（eV）、orbital_groups は同じ段に描く軌道名のグループ。fermi_position は表示軸上のフェルミ準位（eV）。指定すると全パネルに縦線を描きます。xlabel は軸ラベル、extra_formats は EPS・PDF・PNG の追加保存、show は画面表示。 | Path。平均 PDOS と任意の XAS を含む図の保存先。 |

**使用例**

```python
from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage
from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage
from fdmnes_util.fdm_sd_2020 import FdmSd2020

readers = [FdmSd2020("Fe_1_sd0.txt"), FdmSd2020("Fe_2_sd0.txt")]
energy, density = AnalyzeFdmAverage().average(readers, "get_pdos", lm="p_z")
output = PlotFdmAverage().plot([("p_z", energy, density)], "Fe_PDOS_mean.pdf")
```

## 計算結果の整理と畳み込みジョブの準備

### `SiteConvolutionJobPreparer`

`from fdmnes_util.util.site_convolution_job_preparer import SiteConvolutionJobPreparer`

番号付きの生 XAS をファイル名順に選び、サイト別の畳み込み入力とジョブ一覧をまとめて生成します。`FDmakeCconvAllsite.py` が使う処理です。

入力に `Fe_1.txt`、`Fe_2.txt` がある場合、例は `convolution_jobs/` に `conv_1.inp`、`conv_2.inp` と `fdmfile.txt` を書きます。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `write(filout, output_dir='.')` | filout は番号付き生 XAS の接頭辞、output_dir はジョブの書き出し先兼 FDMNES の実行ディレクトリ。 | list[str]。元スペクトルのファイル名順に生成された入力名。`fdmfile.txt` も保存。 |

**使用例**

```python
from fdmnes_util.util.site_convolution_job_preparer import SiteConvolutionJobPreparer
jobs = SiteConvolutionJobPreparer().write("Fe", output_dir="convolution_jobs")
print(jobs)
```

### `ResultFileOperations`

`from fdmnes_util.util.result_file_operations import ResultFileOperations`

一つの `Filout` に対応する結果ファイルを検索、移動、改名、削除します。

| メソッドと引数の既定値 | 引数の意味 | 戻り値 |
| --- | --- | --- |
| `__init__(filout: str \| Path)` | filout は結果の接頭辞。ディレクトリ付きでも指定可能。 | None |
| `outputs()` | — | list[Path]。移動対象と `fdmnes_error.txt`、`fdm.out`、`PBS_log` のうち存在するもの。 |
| `move_outputs()` | — | list[Path]。存在する生 XAS、BAV、畳み込み XAS、SD の移動対象。 |
| `clean()` | — | list[Path]。削除したファイルのパス。 |
| `move(destination: str \| Path)` | destination は移動先ディレクトリ。 | list[Path]。元のファイル名のまま移動した先のパス。 |
| `rename(destination: str \| Path)` | destination は新しい接頭辞。ディレクトリも指定可能。 | list[Path]。改名先。衝突時は FileExistsError。 |

**使用例**

```python
from fdmnes_util.util.result_file_operations import ResultFileOperations
results = ResultFileOperations("Fe")
print(results.outputs())
```

## Python での使用例

### SD から軌道別の密度を取得する

```python
from fdmnes_util.fdm_sd import FdmSd

sd = FdmSd("Fe_sd0.txt", format_year=None).select_reader()
energy = sd.get_eng()
p_ldos = sd.get_ldos("p")
pz_pdos = sd.get_pdos(lm="p_z")
```

### BAV から計算クラスタを XYZ に書き出す

```python
from fdmnes_util.fdm_bav import FdmBav
from fdmnes_util.xyz import Xyz

bav = FdmBav("Fe_bav.txt").select_reader()
symbols = bav.get_atoms_index_j()
positions = bav.get_position()
Xyz.write(symbols, positions, "Fe_cluster.xyz")
```

### サイト平均 XAS を描画する

```python
from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas

spectra = [FdmConv("Fe_1_conv.txt"), FdmConv("Fe_2_conv.txt")]
energy, intensity = AnalyzeFdmAverage().average(spectra, "get_xas")
PlotFdmXas().plot([(energy, intensity, "Fe mean")], "Fe_mean.pdf")
```
