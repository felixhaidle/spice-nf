# download_gtf_and_peptides.py

import argparse
import os
import shutil
import sys
# Add SPICE to path
SPICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SPICE'))
if SPICE_DIR not in sys.path:
    sys.path.insert(0, SPICE_DIR)

from Classes.API.ensembl_mod.LocalEnsembl import LocalEnsembl

import shutil  # Import shutil for copying files

def download_gtf_and_peptides(outdir: str, species: str, release: str, custom_gtf: str = None, custom_pep: str = None, test_mode: bool = False) -> (str, str):
    """
    Downloads the GTF and peptide FASTA files or uses provided custom files.

    Args:
    - outdir (str): Directory to save the downloaded files.
    - species (str): Species for which the GTF and peptide FASTA files are required.
    - release (str): Ensembl release version.
    - custom_gtf (str, optional): Path to a custom GTF file.
    - custom_pep (str, optional): Path to a custom peptide FASTA file.
    - test_mode (bool): If True, run using a minimal dataset for testing.

    Returns:
    - (gtf_path, pep_path) (tuple): Paths to the GTF and peptide FASTA files.
    """
    os.makedirs(outdir, exist_ok=True)  # Ensure the output directory exists

    if custom_gtf:
        # If a custom GTF file is provided, copy it to the output directory
        if os.path.exists(custom_gtf):
            print(f"Using provided custom GTF file: {custom_gtf}")
            gtf_dest_path = os.path.join(outdir, os.path.basename(custom_gtf))
            shutil.copy(custom_gtf, gtf_dest_path)
            gtf_path = gtf_dest_path
            print(f"Custom GTF file copied to: {gtf_path}")
        else:
            raise FileNotFoundError(f"Provided custom GTF file '{custom_gtf}' does not exist.")
    else:
        # Set up LocalEnsembl to download the GTF file
        local_ensembl = LocalEnsembl(species, outdir, release)
        if test_mode:
            # URLs for a minimal test dataset if running in test mode
            test_gtf_url = "http://ftp.ensembl.org/pub/release-113/gtf/saccharomyces_cerevisiae/Saccharomyces_cerevisiae.R64-1-1.113.gtf.gz"
            print("Running in test mode. Downloading minimal test GTF dataset.")
            gtf_path = local_ensembl.download(test_url=test_gtf_url)
        else:
            # Normal download of the full dataset
            print("Running in normal mode. Downloading GTF dataset.")
            gtf_path = local_ensembl.download()

    if custom_pep:
        # If a custom peptide FASTA file is provided, copy it to the output directory
        if os.path.exists(custom_pep):
            print(f"Using provided custom peptide FASTA file: {custom_pep}")
            pep_dest_path = os.path.join(outdir, os.path.basename(custom_pep))
            shutil.copy(custom_pep, pep_dest_path)
            pep_path = pep_dest_path
            print(f"Custom peptide FASTA file copied to: {pep_path}")
        else:
            raise FileNotFoundError(f"Provided custom peptide FASTA file '{custom_pep}' does not exist.")
    else:
        # Download peptide FASTA using LocalEnsembl
        local_ensembl = LocalEnsembl(species, outdir, release)
        if test_mode:
            # URLs for a minimal test dataset if running in test mode
            test_pep_url = "http://ftp.ensembl.org/pub/release-113/fasta/saccharomyces_cerevisiae/pep/Saccharomyces_cerevisiae.R64-1-1.pep.all.fa.gz"
            print("Running in test mode. Downloading minimal test peptide FASTA dataset.")
            pep_path = local_ensembl.download_pep(test_url=test_pep_url)
        else:
            # Normal download of the full dataset
            print("Running in normal mode. Downloading peptide FASTA dataset.")
            pep_path = local_ensembl.download_pep()

    print(f"GTF file path: {gtf_path}")
    print(f"Peptide FASTA file path: {pep_path}")
    return gtf_path, pep_path


def main():
    parser = argparse.ArgumentParser(description="Download or specify GTF and peptide FASTA files for further processing.")
    parser.add_argument('--outdir', type=str, required=True, help='Output directory for the files.')
    parser.add_argument('--species', type=str, required=True, help='Species for which the GTF and peptide FASTA files are required.')
    parser.add_argument('--release', type=str, required=True, help='Ensembl release version for the files.')
    parser.add_argument('--custom_gtf', type=str, help='Path to a custom GTF file if available.')
    parser.add_argument('--custom_pep', type=str, help='Path to a custom peptide FASTA file if available.')
    parser.add_argument('--test', action='store_true', help='Use a minimal dataset for testing.')

    args = parser.parse_args()

    
    # Download the GTF and peptide FASTA files or use custom ones
    gtf_path, pep_path = download_gtf_and_peptides(args.outdir, args.species, args.release, args.custom_gtf, args.custom_pep, args.test)
    
    # Output the paths for Nextflow to capture
    print(f"GTF_PATH={gtf_path}")
    print(f"PEP_PATH={pep_path}")

if __name__ == "__main__":
    main()
