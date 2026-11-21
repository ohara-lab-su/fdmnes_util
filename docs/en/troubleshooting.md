# Troubleshooting

| Symptom | What to check |
| --- | --- |
| `fdmnes_util` is unavailable | Activate the virtual environment used for installation. |
| The input file cannot be found | Check the working directory and `-i`. If `fdmfile.txt` exists, check its first job. |
| `*_conv.txt` or `*_sd0.txt` is missing | Check `Filout`, the site number, and calculation output settings. The plot scripts do not run FDMNES. |
| The BAV revision is unverified | If you know the SD column layout, pass `--year 2016` or `--year 2020` explicitly. |
| The SD reader rejects the spin selection | The verified 2020 SD layout has one spin channel. For the 2016 format, match the configured spin count to the file. |
| Averaging fails because grids differ | Compare the energy columns within the same file family. If needed, explicitly interpolate onto a physically appropriate common grid before averaging. |
| Edge or Fermi energies look wrong | Check the raw XAS header and the combination of `Energpho`, `--fermi`, and `--nonsubtract`. |
| A plot window is unavailable | Use `--nw` where supported and set `MPLBACKEND=Agg` when needed. |
| A POSCAR conversion fails to import | Check that `vasp-util` and ASE are installed in the current environment. |
| Sphinx cannot import Python modules | Install the project and `docs/requirements.txt` in the Python environment used for the build. |

When reporting an issue, include the command, the FDMNES revision, the relevant input keywords, the output column header, and the error message.
