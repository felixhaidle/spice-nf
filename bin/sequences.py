#!/bin/env python

#######################################################################
# Portions Copyright (C) 2023 Christian Bluemel
# Copyright (C) 2025 Felix Haidle
#
# This file is part of spice_library_pipeline and includes adapted
# code originally from the SPICE project (spice_library.py).
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Modifications:
#   - Adapted by Felix Haidle in 2025 from SPICE's spice_library.py.
#######################################################################


import argparse
import os
from Classes.API.ensembl_mod.LocalEnsembl import LocalEnsembl

def download_gtf_and_peptides(outdir: str, species: str, release: str) -> (str, str):
    """
    Downloads GTF and peptide FASTA files for a specified species and Ensembl release.

    Args:
        outdir (str): Directory where the files will be downloaded.
        species (str): Species name (e.g., "homo_sapiens").
        release (str): Ensembl release version (e.g., "109").

    Returns:
        tuple: Paths to the downloaded GTF and peptide FASTA files.
    """
    os.makedirs(outdir, exist_ok=True)
    local_ensembl = LocalEnsembl(species, outdir, release)

    print("Downloading GTF and peptide FASTA datasets from Ensembl...")

    gtf_path = local_ensembl.download()       # Download GTF file
    pep_path = local_ensembl.download_pep()   # Download peptide FASTA

    print(f"GTF_PATH={gtf_path}")
    print(f"PEP_PATH={pep_path}")
    return gtf_path, pep_path


def main():
    """
    CLI entry point. Parses arguments and triggers GTF and peptide download.

    Outputs:
        GTF_PATH and PEP_PATH to stdout (for capturing by Nextflow or similar tools).
    """
    parser = argparse.ArgumentParser(
        description="Download GTF and peptide FASTA files from Ensembl."
    )
    parser.add_argument('--outdir', type=str, required=True,
                        help='Output directory for the downloaded files.')
    parser.add_argument('--species', type=str, required=True,
                        help='Species name (e.g., homo_sapiens).')
    parser.add_argument('--release', type=str, required=True,
                        help='Ensembl release version (e.g., 109).')

    args = parser.parse_args()

    gtf_path, pep_path = download_gtf_and_peptides(
        args.outdir, args.species, args.release
    )

    # Print again so Nextflow or other pipeline tools can easily parse the paths
    print(f"GTF_PATH={gtf_path}")
    print(f"PEP_PATH={pep_path}")


if __name__ == "__main__":
    main()
