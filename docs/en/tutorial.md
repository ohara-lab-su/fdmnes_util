# Tutorials

## Plot Fe XAS and LDOS

Try post-processing with the Fe outputs included in the repository. Install the plotting dependencies, then run these commands from the repository root.

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

`FDgetfermi.py` reports the Fermi and absorption-edge energies. The files `XAS.pdf`, `XAS.eps`, and `XAS.png` show raw XAS, convolved XAS, and LDOS. `LDOS0_fermi.pdf` shows Fermi-relative p-orbital LDOS and its integral. `PDOS0.pdf` groups the magnetic-sublevel projections. Use `--nw` to suppress the plot window after saving.

To include experimental data, pass an Athena file containing photon energy and normalized absorption.

```console
python FDplot_XAS.py -i read_pdb.inp --obs measured.nor --dos --year 2020 --nw
```

## Extract the curve in Python

```python
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_sd import FdmSd

calculation = FdmInp("read_pdb.inp")
prefix = calculation.get_filout()
sd = FdmSd(f"{prefix}_sd0.txt", format_year=2020).select_reader()
for energy, density in list(zip(sd.get_eng(), sd.get_ldos("p")))[:3]:
    print(energy, density)
```

## Create per-site convolution jobs

If you have numbered raw spectra such as `Fe_1.txt` and `Fe_2.txt`, run `python FDmakeCconvAllsite.py -i read_pdb.inp` to generate `conv_1.inp` and the remaining jobs, together with `fdmfile.txt`. Preserve the existing job list before running the script. Run FDMNES from that directory to produce the `*_conv.txt` files specified in the inputs.
