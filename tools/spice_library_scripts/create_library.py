# create_library.py

import argparse
import os
import sys
import json
from typing import Any, Dict
from tqdm import tqdm
from datetime import date

# Add SPICE to path
SPICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SPICE'))
if SPICE_DIR not in sys.path:
    sys.path.insert(0, SPICE_DIR)

# Import necessary classes from the SPICE library
from Classes.SequenceHandling.GeneAssembler import GeneAssembler
from Classes.SequenceHandling.LibraryInfo import LibraryInfo
from Classes.PassPath.PassPath import PassPath
from Classes.TreeGrow.TreeGrow import TreeGrow
from Classes.API.ensembl_mod.LocalEnsembl import LocalEnsembl
from Classes.FastaBoy.FastaBoy import EnsemblFastaBoy
from Classes.SequenceHandling.Gene import Gene
from Classes.SequenceHandling.Protein import Protein
from Classes.FASTools.FASModeHex import FASModeHex

def classify_gene_size(gene) -> str:
    """
    Classify a gene based on the combined length of all its transcript sequences.

    Args:
    - gene (Gene): A gene object containing transcripts.

    Returns:
    - str: The size category ('small', 'medium', 'large').
    """
    # Compute the total transcript sequence length
    total_length = sum(len(protein.get_sequence()) for protein in gene.get_proteins() if isinstance(protein, Protein))
    print(total_length)
    # Define thresholds (adjust based on empirical data)
    if total_length < 5000:
        return "small"
    elif total_length < 50000:
        return "medium"
    else:
        return "large"

def write_gene_ids_to_file(gene_assembler: GeneAssembler, transcript_data_dir: str) -> None:
    """
    Write all gene IDs and their size classification in the library to a file in the transcript_data directory.

    Args:
    - gene_assembler (GeneAssembler): The gene assembler object containing the gene data.
    - transcript_data_dir (str): Path to the transcript_data directory where genes.txt will be saved.
    """
    # Construct the full path for genes.txt
    output_file = os.path.join(transcript_data_dir, "genes.txt")

    gene_list = gene_assembler.get_genes()
    with open(output_file, "w") as f:
        for gene in gene_list:
            size_category = classify_gene_size(gene)
            f.write(f"{gene.get_id()} {size_category}\n")  # Write gene ID with size classification
            print(f"{gene.get_id()} {size_category}\n")

    print(f"Gene IDs with size classification written to {output_file}.")



def setup_library(outdir, species, release, fas_mode_hex):
    """
    Set up the directory structure and create initial files for the gene library.

    Args:
    - outdir (str): The output directory for the gene library.
    - species (str): The species name.
    - release (str): The Ensembl release version.
    - fas_mode_hex (str): Hex value representing the FAS mode.
    """
    library_name = f"spice_lib_{species}_{release}_{fas_mode_hex}"
    library_root = os.path.join(outdir, library_name)

    # Define all the paths as needed by the original script
    path_dict = {
        "root": library_root,
        "info": "info.yaml",
        "fas_data": "fas_data",
        "fas_scores": "fas_data/fas_scores",
        "fas_index": "fas_data/fas_index.json",
        "fas_temp": "fas_data/tmp",
        "fas_annotation": "fas_data/annotation",
        "fas_annoTools": "fas_data/annoTools.txt",
        "fas_architectures": "fas_data/architectures/",
        "transcript_data": "transcript_data",
        "transcript_info": "transcript_data/transcript_info.json",
        "transcript_seq": "transcript_data/sequences.json",
        "transcript_fasta": "transcript_data/transcript_set.fasta",
        "transcript_pairings": "transcript_data/transcript_pairings.json",
        "transcript_ids": "transcript_data/phyloprofile_ids.tsv"
    }

    # Create directories and initial files as per the path_dict
    print("Setting up library structure...")
    pass_path = PassPath(path_dict)
    tree_grow = TreeGrow(path_dict)
    tree_grow.create_folders()  # Creates all necessary directories

    # Create initial placeholder files
    with open(pass_path["fas_annoTools"], "w") as f:
        f.write(str(fas_mode_hex))
    with open(pass_path["transcript_pairings"], "w") as f:
        json.dump({}, f, indent=4)
    with open(pass_path["transcript_seq"], "w") as f:
        json.dump({}, f, indent=4)
    with open(pass_path["fas_index"], "w") as f:
        json.dump({}, f, indent=4)
    with open(pass_path["transcript_info"], "w") as f:
        json.dump({}, f, indent=4)

    # Save path.json to store all paths in a single file
    path_json_path = os.path.join(library_root, "paths.json")
    with open(path_json_path, "w") as f:
        json.dump(path_dict, f, indent=4)

    print(f"Library setup complete at {library_root}. Paths have been saved to {path_json_path}.")
    return pass_path

def collect_sequences(gene_assembler: GeneAssembler, fasta_path: str, pass_path: PassPath, library_info: LibraryInfo) -> None:
    """
    Collect sequences from a given FASTA file and save results.

    Args:
    - gene_assembler (GeneAssembler): The gene assembler object to collect sequences into.
    - fasta_path (str): Path to the peptide FASTA file.
    - pass_path (PassPath): PassPath object containing paths for saving data.
    - library_info (LibraryInfo): LibraryInfo object to update and save library information.
    """
    # Use EnsemblFastaBoy to parse the peptide FASTA file and apply filters
    fasta_iterator = EnsemblFastaBoy(fasta_path)
    fasta_iterator.set_filter("transcript_biotype", "protein_coding")
    fasta_iterator.set_filter("gene_biotype", "protein_coding")
    fasta_iterator.parse_fasta()
    fasta_dict = fasta_iterator.get_fasta_dict()

    gene_list = gene_assembler.get_genes()
    missing_proteins = []

    # Iterate through genes and proteins, and set sequences for proteins if found in FASTA
    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Sequence collection progress"):
        protein_list = gene.get_proteins()
        for protein in protein_list:
            gene_id = gene.get_id()  # Normalize gene ID
            protein_id = protein.get_id() # Normalize protein ID

            # Check if sequence exists in the FASTA dictionary and set it if present
            if gene_id in fasta_dict and protein_id in fasta_dict[gene_id]:
                protein.set_sequence(fasta_dict[gene_id][protein_id])
            else:
                missing_proteins.append((gene_id, protein_id))
                print(f"Missing sequence for Gene ID: {gene_id}, Protein ID: {protein_id}")

    # Log all missing proteins at the end for easier inspection
    if missing_proteins:
        print("Missing proteins (not found in FASTA):")
        for gene_id, protein_id in missing_proteins:
            print(f"  Gene ID: {gene_id}, Protein ID: {protein_id}")

    # Clear genes that do not have any valid proteins left
    gene_assembler.clear_empty_genes()

    # Save the updated sequences and FAS data
    gene_assembler.save_seq(pass_path)
    gene_assembler.save_fas(pass_path)
    gene_assembler.save_info(pass_path)

    # Update library_info with new counts and save it
    info: Dict[str, Any] = library_info["info"]
    library_info["info"]["collected_sequences_count"] = gene_assembler.get_collected_sequences_count()
    sequence_collection_flag: bool = info["protein_count"] == info["collected_sequences_count"]
    library_info["status"]["02_sequence_collection"] = sequence_collection_flag
    library_info["info"]["gene_count"] = gene_assembler.get_gene_count()
    library_info.save()


def remove_small_proteins(gene_assembler: GeneAssembler, library_info: LibraryInfo, pass_path: PassPath, min_length=11):
    """
    Remove proteins below a certain length and update LibraryInfo.

    Args:
    - gene_assembler (GeneAssembler): The gene assembler object containing the gene data.
    - library_info (LibraryInfo): LibraryInfo object to update and save library information.
    - pass_path (PassPath): PassPath object containing paths for saving data.
    - min_length (int): Minimum length of proteins to retain.
    """
    gene_list = gene_assembler.get_genes()
    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Small protein removal progress"):
        protein_list = gene.get_proteins()
        for protein in protein_list:
            if len(protein) < min_length:
                gene.delete_transcript(protein.get_id())

    # Clear genes that have no valid transcripts left
    gene_assembler.clear_empty_genes()

    # Save updated sequence data
    gene_assembler.save_seq(pass_path)
    gene_assembler.save_fas(pass_path)
    gene_assembler.save_info(pass_path)

    # Update LibraryInfo with the new counts and save it
    library_info["last_edit"] = str(date.today())
    library_info["info"]["gene_count"] = gene_assembler.get_gene_count()
    library_info["info"]["transcript_count"] = gene_assembler.get_transcript_count()
    library_info["info"]["protein_count"] = gene_assembler.get_protein_count()
    library_info["info"]["collected_sequences_count"] = gene_assembler.get_collected_sequences_count()
    library_info["info"]["fas_scored_sequences_count"] = gene_assembler.get_fas_scored_count()
    library_info["status"]["03_small_protein_removing"] = True
    library_info.save()


def main():
    parser = argparse.ArgumentParser(description="Create a gene library by collecting sequences and removing small proteins.")
    parser.add_argument('--outdir', type=str, required=True, help='Output directory for the gene library.')
    parser.add_argument('--gtf_path', type=str, required=True, help='Path to the transcript GTF file.')
    parser.add_argument('--fasta_path', type=str, required=True, help='Path to the peptide FASTA file.')
    parser.add_argument('--species', type=str, required=True, help='Species name.')
    parser.add_argument('--release', type=str, required=True, help='Ensembl release version.')
    parser.add_argument('--min_protein_length', type=int, default=11, help='Minimum protein length to retain.')
    parser.add_argument('--modefas', type=str, default=None, help='Path to a FAS mode file to configure FAS in this library.')

    args = parser.parse_args()

    # Initialize LocalEnsembl instance
    local_ensembl = LocalEnsembl(args.species, args.outdir, args.release)
    taxon_id = local_ensembl.get_taxon_id()

    # Set up FAS mode hex
    fas_mode_hex = FASModeHex()
    if args.modefas is None:
        # Activate all modes if no FAS mode file is provided
        fas_mode_hex.activate_all()
    else:
        # Load modes from a file if provided
        with open(args.modefas, "r") as f:
            fas_mode_list = f.read().split("\n")
        fas_mode_list += ["#linearized", "#normal", "#checked"]
        fas_mode_hex.activate_modes(fas_mode_list)

    mode_hex_value = fas_mode_hex.get_mode_hex()  # Obtain the FAS mode hex value for use

    # Create library structure and write initial files
    pass_path = setup_library(args.outdir, args.species, args.release, mode_hex_value)

    # Save FAS mode configuration to a file for future reference
    with open(pass_path["fas_annoTools"], "w") as f:
        f.write(str(fas_mode_hex))

    # Create a GeneAssembler object and load GTF
    gene_assembler = GeneAssembler(args.species, taxon_id)
    gene_assembler.update_inclusion_filter("gene_biotype", ["protein_coding"])
    gene_assembler.update_inclusion_filter("transcript_biotype", ["protein_coding", "nonsense_mediated_decay"])

    # Extract information from GTF
    print("Extracting information from GTF file...")
    gene_assembler.extract(args.gtf_path)
    gene_assembler.clear_empty_genes()

    # Initialize and Save LibraryInfo with initial metadata
    library_info = LibraryInfo(pass_path["info"])
    library_info["spice_version"] = "0.1"
    library_info["init_date"] = str(date.today())
    library_info["last_edit"] = str(date.today())
    library_info["commandline_args"] = vars(args)
    library_info["info"] = {
        "species": args.species,
        "taxon_id": taxon_id,
        "release": args.release,
        "fas_mode": mode_hex_value,
        "gene_count": gene_assembler.get_gene_count(),
        "transcript_count": gene_assembler.get_transcript_count(),
        "protein_count": gene_assembler.get_protein_count(),
        "collected_sequences_count": 0,  # Initially 0 before sequence collection
        "fas_scored_sequences_count": 0
    }
    library_info["status"] = {
        "01_id_collection": True,
        "02_sequence_collection": False,
        "03_small_protein_removing": False,
        "04_incorrect_entry_removing": False,
        "05_implicit_fas_scoring": False,
        "06_fasta_generation": False,
        "07_pairing_generation": False,
        "08_id_tsv_generation": False
    }
    library_info.save()

    # Collect sequences from the FASTA file
    print("Collecting sequences from FASTA...")
    collect_sequences(gene_assembler, args.fasta_path, pass_path, library_info)

    # Remove small proteins
    print("Removing small proteins...")
    remove_small_proteins(gene_assembler, library_info, pass_path, args.min_protein_length)

    # Write gene IDs to a file in the transcript_data directory
    write_gene_ids_to_file(gene_assembler, pass_path["transcript_data"])

    print(f"Library information saved at {pass_path['info']}.")

if __name__ == "__main__":
    main()
