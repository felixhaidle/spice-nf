# filter_library.py

import argparse
import os
import sys
import json
import yaml
from tqdm import tqdm

# Add SPICE to path
SPICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SPICE'))
if SPICE_DIR not in sys.path:
    sys.path.insert(0, SPICE_DIR)

# Import necessary classes from SPICE library
from Classes.SequenceHandling.GeneAssembler import GeneAssembler
from Classes.SequenceHandling.LibraryInfo import LibraryInfo
from Classes.PassPath.PassPath import PassPath

def remove_incorrect_entries(gene_assembler):
    """
    Remove incorrect entries from the library based on the original filtering logic.

    Args:
    - gene_assembler (GeneAssembler): The gene assembler object containing the gene data.
    """
    gene_list = gene_assembler.get_genes()
    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Incorrect entry removal progress"):
        transcript_list = gene.get_transcripts()
        for transcript in transcript_list:
            if transcript.get_biotype() == "protein_coding":
                if transcript.get_id_taxon() == 9606:
                    if transcript.get_id()[3] == "T" and "NOVEL" not in transcript.get_tags():
                        gene.delete_transcript(transcript.get_id())
    gene_assembler.clear_empty_genes()

def filter_gene_library(library_dir):
    """
    Filter the gene library by removing incorrect entries.

    Args:
    - library_dir (str): The root directory of the gene library.
    """
    # Load paths from paths.json
    path_json_path = os.path.join(library_dir, "paths.json")
    with open(path_json_path, "r") as f:
        path_dict = json.load(f)

    # Create PassPath object to handle paths
    pass_path = PassPath(path_dict)

    # Load LibraryInfo object to get metadata
    library_info_path = pass_path["info"]
    with open(library_info_path, "r") as f:
        library_info = yaml.safe_load(f)

    # Extract species and taxon_id from library_info
    species = library_info["info"]["species"]
    taxon_id = library_info["info"]["taxon_id"]

    # Load the GeneAssembler object
    print("Loading existing gene library...")
    gene_assembler = GeneAssembler(species, taxon_id)
    gene_assembler.load(pass_path)

    # Perform filtering to remove incorrect entries
    print("Removing incorrect entries from the gene library...")
    remove_incorrect_entries(gene_assembler)

    # Save the filtered library
    print("Saving the filtered gene library...")
    gene_assembler.save_seq(pass_path)
    library_info_object = LibraryInfo(library_info_path)
    library_info_object.save()

    print("Filtering complete.")

def main():
    parser = argparse.ArgumentParser(description="Filter gene library by removing incorrect entries.")
    parser.add_argument('--library_dir', type=str, required=True, help='Root directory of the gene library.')

    args = parser.parse_args()

    # Perform filtering on the provided library directory
    filter_gene_library(args.library_dir)

if __name__ == "__main__":
    main()
