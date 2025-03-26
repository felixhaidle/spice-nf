#!/bin/env python

import argparse
import os
from Classes.API.ensembl_mod.LocalEnsembl import LocalEnsembl

def download_gtf_and_peptides(outdir: str, species: str, release: str) -> (str, str):
    """
    Downloads the GTF and peptide FASTA files from Ensembl.

    Args:
    - outdir (str): Directory to save the downloaded files.
    - species (str): Species for which the GTF and peptide FASTA files are required.
    - release (str): Ensembl release version.

    Returns:
    - (gtf_path, pep_path) (tuple): Paths to the GTF and peptide FASTA files.
    """
    os.makedirs(outdir, exist_ok=True)
    local_ensembl = LocalEnsembl(species, outdir, release)

    print("Downloading GTF and peptide FASTA datasets from Ensembl...")
    gtf_path = local_ensembl.download()
    pep_path = local_ensembl.download_pep()

    print(f"GTF_PATH={gtf_path}")
    print(f"PEP_PATH={pep_path}")
    return gtf_path, pep_path

def main():
    parser = argparse.ArgumentParser(description="Download GTF and peptide FASTA files from Ensembl.")
    parser.add_argument('--outdir', type=str, required=True, help='Output directory for the files.')
    parser.add_argument('--species', type=str, required=True, help='Species name.')
    parser.add_argument('--release', type=str, required=True, help='Ensembl release version.')

    args = parser.parse_args()

    gtf_path, pep_path = download_gtf_and_peptides(args.outdir, args.species, args.release)

    # Output paths for Nextflow to capture
    print(f"GTF_PATH={gtf_path}")
    print(f"PEP_PATH={pep_path}")

if __name__ == "__main__":
    main()
