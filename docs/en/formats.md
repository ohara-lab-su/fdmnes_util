# File formats and energy references

| File | Contents | Python class |
| --- | --- | --- |
| `*.inp` | `Filout`, `Absorber`, `Energpho`, structure sections, and other supported keywords | `FdmInp` |
| `fdmfile.txt` | Job count and ordered list of input files | `Fdmfile` |
| `<Filout>.txt` | Raw XAS with absorption-edge and Fermi-energy metadata | `FdmTxt` |
| `<Filout>_conv.txt` | Convolved energy grid and intensities | `FdmConv` |
| `<Filout>_bav.txt` | Revision, calculation settings, cluster coordinates, and SCF log | `FdmBav` |
| `<Filout>_sdN.txt` | Orbital densities and integrals for site N | `FdmSd` |
| `*.nor` | Experimental XAS normalized in Athena | `AthenaNor` |

Raw XAS, convolved XAS, and SD have independent energy grids. Use the energy column that belongs to each intensity array. Averaging calculations requires matching grids within each file family.

The table shows the rules used by `AnalyzeFdmXas.energy_reference()`. `E` is the energy in the file. `E_edge` and `E_Fermi` come from the raw XAS header.

| Calculation input | Photon energy | Fermi-relative energy |
| --- | --- | --- |
| Without `Energpho` | `E + E_edge` | `E − E_Fermi` |
| With `Energpho` | `E` | `E − E_edge − E_Fermi` |

The 2016 SD reader uses column order and the configured spin count. The 2020 reader uses column names and handles nonmagnetic output and the 31-column magnetic layout verified on 2021 and 2026 Ni output. The magnetic layout stores one `total` and one `Int(total)` column for both spins. Many samples accept `--year` to select the layout explicitly.

For the calculation keywords themselves, consult the FDMNES manual distributed with the application. This documentation covers the files and operations supported by the Python library.
