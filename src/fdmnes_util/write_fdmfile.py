#!/usr/bin/env python3
# Original SAE source: fdmfile_writer.py
# SAE: Copyright Kengo NAKADA; SAE class library.
# SAE: The original class writes the FDMNES fdmfile.txt job list.
"""Write a FDMNES job-list file (``fdmfile.txt``)."""

from pathlib import Path


class WriteFdmfile:
    """Serialize an ordered list of input files for FDMNES."""

    def write(self, filenames, filename="fdmfile.txt"):
        """Write the job count and each input filename.

        Args:
            filenames: Iterable of FDMNES input filenames.
            filename: Destination path for the job-list file.

        Returns:
            Path: Path of the generated job-list file.
        """
        input_names = list(filenames)
        output_path = Path(filename)
        output_lines = ["", str(len(input_names))]

        for input_name in input_names:
            output_lines.append(str(input_name))

        output_text = "\n".join(output_lines) + "\n"
        output_path.write_text(output_text, encoding="utf-8")
        return output_path
