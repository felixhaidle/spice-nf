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
import json

from Classes.API.ensembl_mod.LocalEnsembl import LocalEnsembl


def download_gtf_and_peptides(outdir: str, species: str, release: int):
    """
    Downloads GTF and peptide FASTA files for a specified species and Ensembl release.
    Returns: (gtf_path, pep_path, species_name, taxon_id, resolved_release)
    """
    os.makedirs(outdir, exist_ok=True)

    local_ensembl = LocalEnsembl(
        raw_species=species,
        goal_directory=outdir,
        release=release
    )

    print("Downloading GTF and peptide FASTA datasets from Ensembl...")
    gtf_path = local_ensembl.download()
    pep_path = local_ensembl.download_pep()

    # Get metadata
    species_name = local_ensembl.get_species_name()
    taxon_id = local_ensembl.get_taxon_id()
    resolved_release = local_ensembl.get_release_num()

    return gtf_path, pep_path, species_name, taxon_id, resolved_release


def main():
    parser = argparse.ArgumentParser(
        description="Download GTF and peptide FASTA files from Ensembl."
    )
    parser.add_argument('--outdir', type=str, required=True, help='Download directory')
    parser.add_argument('--species', type=str, required=True, help='Species name (e.g., homo_sapiens)')
    parser.add_argument('--release', type=int, default=-1, help='Ensembl release version, or -1 for latest')

    args = parser.parse_args()

    gtf_path, pep_path, species_name, taxon_id, release = download_gtf_and_peptides(
        args.outdir, args.species, args.release
    )


    print(f"{species_name}\t{taxon_id}\t{release}")


if __name__ == "__main__":
    main()

