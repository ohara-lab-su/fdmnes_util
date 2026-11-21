# チュートリアル

## FeのXASとLDOSを描画する

リポジトリに含まれるFeの出力例で後処理を試します。描画用の追加依存を入れた環境で、リポジトリのトップから次を実行します。

```console
mkdir -p work/fe
cp tests/fixtures/Fe*.txt work/fe/
cd work/fe
printf 'Filout Fe\nEnd\n' > read_pdb.inp
fdmnes_util install script
python FDgetfermi.py -i read_pdb.inp
python FDplot_XAS.py -i read_pdb.inp --dos --year 2020 --pdf --nw
python FDplot_LDOS.py -i read_pdb.inp --year 2020 --p --xas --intdos --fermi --nw
python FDplot_PDOS.py -i read_pdb.inp --year 2020 --spd --broad --nw
```

`FDgetfermi.py` がフェルミ準位と吸収端を表示します。`XAS.pdf`・`XAS.eps`・`XAS.png` には生XAS、畳み込み後XAS、LDOSが描かれます。`LDOS0_fermi.pdf` はFermi基準のp軌道LDOSと積分を示し、`PDOS0.pdf` は磁気量子数別の成分をまとめます。`--nw` は保存後のGUI表示を抑止します。

実験も重ねるには、光子エネルギーと規格化吸収強度を持つAthenaのファイルを指定します。

```console
python FDplot_XAS.py -i read_pdb.inp --obs measured.nor --dos --year 2020 --nw
```

## Pythonで同じ曲線を取り出す

```python
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_sd import FdmSd

calculation = FdmInp("read_pdb.inp")
prefix = calculation.get_filout()
sd = FdmSd(f"{prefix}_sd0.txt", format_year=2020).select_reader()
for energy, density in list(zip(sd.get_eng(), sd.get_ldos("p")))[:3]:
    print(energy, density)
```

## サイト別畳み込みジョブを作る

`Fe_1.txt`、`Fe_2.txt` のような番号付き生スペクトルがある場合、`python FDmakeCconvAllsite.py -i read_pdb.inp` で `conv_1.inp` などと `fdmfile.txt` が生成されます。既存のジョブ一覧を保管してから実行してください。そのディレクトリでFDMNESを実行すると、入力に記載された `*_conv.txt` が出力されます。
