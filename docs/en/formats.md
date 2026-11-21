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

The 2016 SD layout is interpreted by column order and the configured spin count. The 2020 reader uses named columns and the verified layout has one spin channel. Many samples accept a `--year` argument. Automatic layout selection from a 2022 or later BAV log is unsupported.

For the calculation keywords themselves, consult the FDMNES manual distributed with the application. This documentation covers the files and operations supported by the Python library.
