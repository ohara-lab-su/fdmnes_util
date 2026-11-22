# Installation and usage

Python 3.10 or newer is required. Readers and numerical analysis use NumPy. Plotting requires Matplotlib, ASE-backed conversions require ASE, and POSCAR reading requires the external `vasp-util` package.

```console
python -m pip install 'fdmnes-util[plot]'
```

To install from a checkout, run the following at the repository root. Use `.[plot,structure]` if you also need structure conversion.

```console
python -m pip install '.[plot]'
```

Run `fdmnes_util install script` in your analysis directory to copy the editable Python examples. Existing files are skipped unless you pass `--force`. The directory passed to `--directory` must already exist.

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

log = FdmRun().run("read_pdb.inp")
print(log)
```

`FdmRun()` uses `fdmnes` on PATH. You can also pass the executable path. A single specified input runs in its own directory. When no input is specified, the runner uses all jobs in `fdmfile.txt`.

## Preview the documentation locally

Run these commands at the repository root. The generated site is in `docs/_build/html/`.

```console
python -m pip install . -r docs/requirements.txt
bash docs/build.sh
python -m http.server 8000 --directory docs/_build/html
```

Open `http://localhost:8000/` in your browser. The English edition is at `/en/` and the Japanese edition is at `/ja/`.
