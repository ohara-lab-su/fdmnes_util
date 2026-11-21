#!/usr/bin/env python3
# Original SAE source: FDmakeCconvAllsite.py
# SAE: K.NAKADA, kengo.nakada@gmail.com
# SAE: 2018.08.17 - Python2/3 両対応
# SAE: 2015.06.30 startup
"""Generate FDMNES convolution inputs for all calculated sites."""

from pathlib import Path
import re

from .fdmfile import Fdmfile


class FdmConvolutionInputs:
    """Create one convolution input per numbered all-site XAS spectrum."""

    def write(self, filout, output_dir="."):
        """Generate site-specific convolution jobs and a job-list file.

        The source spectra must follow ``<Filout>_<number>.txt``. Other
        matching files, including already convolved results, are excluded.

        Args:
            filout: FDMNES output prefix, optionally including a directory.
            output_dir: Directory receiving convolution inputs and fdmfile.txt.

        Returns:
            list[str]: Generated convolution input filenames, in sorted order.
        """
        prefix_path = Path(filout)
        source_directory = prefix_path.parent
        prefix_name = prefix_path.name
        output_directory = Path(output_dir)
        output_directory.mkdir(parents=True, exist_ok=True)

        # Accept only numbered spectra. Do not include *_conv.txt files.
        spectrum_pattern = re.compile(re.escape(prefix_name) + r"_\d+\.txt")
        source_spectra = []
        for candidate in sorted(source_directory.glob(prefix_name + "_*.txt")):
            if spectrum_pattern.fullmatch(candidate.name):
                source_spectra.append(candidate)

        input_names = []
        for site_number, spectrum in enumerate(source_spectra, start=1):
            input_name = f"conv_{site_number}.inp"
            convolution_name = spectrum.stem + "_conv.txt"
            input_lines = [
                "",
                " Filout",
                "   " + prefix_name,
                "",
                " Calculation",
                "   " + spectrum.name,
                "",
                " Conv_out",
                "   " + convolution_name,
                "",
                " Convolution",
                "",
                "END",
            ]
            input_text = "\n".join(input_lines) + "\n"
            input_path = output_directory / input_name
            input_path.write_text(input_text, encoding="utf-8")
            input_names.append(input_name)

        job_list_path = output_directory / "fdmfile.txt"
        Fdmfile.write(input_names, job_list_path)
        return input_names
