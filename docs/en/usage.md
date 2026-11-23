# Installation and usage

Python 3.10 or newer is required. Readers and numerical analysis use NumPy. Plotting requires Matplotlib, ASE-backed conversions require ASE, and POSCAR reading requires the external `vasp-util` package.

```console
python -m pip install 'fdmnes-util[plot]'
```

To install from a checkout, run the following at the repository root. Use `.[plot,structure]` if you also need structure conversion.

```console
python -m pip install '.[plot]'
```

`fdmnes_util install` and `fdmnes_util install script` both copy all scripts to the current directory. `fdmnes_util install FDplot_XAS` copies only `FDplot_XAS.py`. `fdmnes_util install list` prints one script name and description per line. Use the script name without `.py`. Existing files are skipped unless you pass `--force`. `--directory` allows an existing alternate destination.

```console
mkdir -p analysis
fdmnes_util install script --directory analysis
cd analysis
python FDplot_XAS.py --help
```

Place the calculation outputs in your analysis directory. Install FDMNES separately to run the calculations. Many samples resolve output names using `Filout` from the input. If you omit `-i` in scripts such as `FDplot_XAS.py`, they use the first job listed in `fdmfile.txt`, falling back to `read_pdb.inp` in the working directory.

## Run a calculation from Python

```python
from fdmnes_util.fdm_run import FdmRun

log = FdmRun().run("Cu.inp")
print(log)
```

`FdmRun()` uses `fdmnes` on PATH or an explicit executable path. `run()` runs the default `inp.txt` and `run("Cu.inp")` runs the specified input. A missing input raises an error before launch. The runner writes a temporary one-entry `fdmfile.txt` and restores its prior state afterward. Call `run_fdmfile()` to use the existing job list as written. The command-line equivalents are `python FDrun.py Cu.inp` and `python FDrun.py --fdmfile`.


## Build and update calculation inputs

`FdmInp` writes the guide's keyword blocks in order. To start from a POSCAR, call `FdmInp.from_poscar("POSCAR")`. It uses `vasp_util` to read the structure and `FdmStructure` to render the FDMNES block. Set calculation options in Python.

```python
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_run import FdmRun

model = FdmInp("cu.inp", format_year=2026)
model.set_block("Filout", "Cu_radius_scan")
model.set_block("Range", (-2, 0.2, 5, 0.5, 10, 1, 40))
model.set_radius(4.0, (15, 3.5), (30, 3.0))
model.set_block("Green")
model.set_block("Convolution")
job = model.save("cu_radius.inp")
log = FdmRun().run(job, directory=".", timeout=120)
print(log)
```

The first value passed to `set_radius()` is the radius in Å. Additional pairs specify a transition energy in eV and the radius above that energy. Pass data rows in order to `set_block()`. When changing a variable-length block such as `Calculation`, specify the number of old data rows with `old_rows`. For example, use `model.set_block("Calculation", "Cu.txt", (1.0, 0.2), old_rows=2)`. Use the guide's layout with each keyword on its own line. FDMNES interprets the keyword combinations and calculation settings. Pass `overwrite=True` to replace a file explicitly.

`run_inputs()` launches FDMNES once per input in Python order and returns the log paths in the same order. Each launch uses a one-entry job list. Relative input and resource paths are resolved from the calculation directory. The timeout applies to the batch.

### Guide examples

```console
python FDmanual_examples.py all --directory manual_calculations
python FDmanual_examples.py poscar --poscar POSCAR --directory poscar_calculation
```

`all` runs the guide's fcc copper crystal, the magnetite first-calculation example, and the FeO₆ molecule example in order. The FeO₆ model uses a short Fe K-edge calculation. Use `--write-only` to generate inputs.

## Preview the documentation locally

Run these commands at the repository root. The generated site is in `docs/_build/html/`.

```console
python -m pip install . -r docs/requirements.txt
bash docs/build.sh
python -m http.server 8000 --directory docs/_build/html
```

Open `http://localhost:8000/` in your browser. The English edition is at `/en/` and the Japanese edition is at `/ja/`.
