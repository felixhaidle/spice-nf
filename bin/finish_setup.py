#!/bin/env python

import argparse
import os
import json
import yaml
from tqdm import tqdm



# Import necessary classes from SPICE library
from Classes.SequenceHandling.GeneAssembler import GeneAssembler
from Classes.SequenceHandling.LibraryInfo import LibraryInfo
from Classes.PassPath.PassPath import PassPath

def calculate_implicit_fas_scores(gene_assembler: GeneAssembler, library_info: LibraryInfo, pass_path: PassPath):
    """
    Step 5: Calculate implicit FAS scores for all genes.

    This function iterates through all genes in the gene assembler and calculates the implicit FAS (Functional Annotation Scores)
    for each gene. This score is used to evaluate the quality of annotations in a consistent manner. The calculated scores
    are saved in the FAS file using the provided `pass_path`, and the library information is updated accordingly.

    Parameters:
        gene_assembler (GeneAssembler): An instance of GeneAssembler containing gene data.
        library_info (LibraryInfo): An instance of LibraryInfo to store metadata and status information.
        pass_path (PassPath): An instance of PassPath containing the paths for saving FAS data.
    """
    gene_list = gene_assembler.get_genes()
    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Implicit FAS score collection progress"):
        gene.calculate_implicit_fas_scores()

    gene_assembler.save_fas(pass_path)
    library_info["status"]["05_implicit_fas_scoring"] = True
    library_info.save()


def generate_fasta_file(gene_assembler: GeneAssembler, library_info: LibraryInfo, pass_path: PassPath):
    """
    Step 6: Generate a FASTA file for all sequences.

    This function generates a FASTA file containing all sequences for the genes in the gene assembler.
    The sequences are written to the specified file path in `pass_path`. This step is essential for downstream
    applications that require sequence information in FASTA format.

    Parameters:
        gene_assembler (GeneAssembler): An instance of GeneAssembler containing gene data.
        library_info (LibraryInfo): An instance of LibraryInfo to store metadata and status information.
        pass_path (PassPath): An instance of PassPath containing the paths for saving the FASTA file.
    """
    gene_list = gene_assembler.get_genes()
    output_list = []
    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Fasta generation process"):
        output_list.append(gene.fasta)

    with open(pass_path["transcript_fasta"], "w") as f:
        f.write("\n".join(output_list))

    library_info["status"]["06_fasta_generation"] = True
    library_info.save()


def generate_pairings(gene_assembler: GeneAssembler, library_info: LibraryInfo, pass_path: PassPath):
    """
    Step 7: Generate pairings for all genes.

    This function generates pairings for all genes in the gene assembler. Pairings are used to establish relationships
    between different transcripts or proteins of the same gene. The generated pairings are saved in a JSON file specified
    by `pass_path`. This step is crucial for understanding the gene structure and the relationships between its components.

    Parameters:
        gene_assembler (GeneAssembler): An instance of GeneAssembler containing gene data.
        library_info (LibraryInfo): An instance of LibraryInfo to store metadata and status information.
        pass_path (PassPath): An instance of PassPath containing the paths for saving the pairings file.
    """
    gene_list = gene_assembler.get_genes(False, True)
    pairings_dict = {}
    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Pairing generation process"):
        pairings_dict[gene.get_id()] = gene.make_pairings()

    with open(pass_path["transcript_pairings"], "w") as f:
        json.dump(pairings_dict, f, indent=4)

    library_info["status"]["07_pairing_generation"] = True
    library_info.save()


def generate_ids_tsv(gene_assembler: GeneAssembler, library_info: LibraryInfo, pass_path: PassPath):
    """
    Step 8: Generate phyloprofile IDs for all proteins.

    This function generates a TSV (Tab-Separated Values) file containing the IDs for all proteins in the gene assembler.
    These IDs are used for phylogenetic profiling, allowing researchers to analyze evolutionary relationships.
    The output is written to a TSV file specified by `pass_path`.

    Parameters:
        gene_assembler (GeneAssembler): An instance of GeneAssembler containing gene data.
        library_info (LibraryInfo): An instance of LibraryInfo to store metadata and status information.
        pass_path (PassPath): An instance of PassPath containing the paths for saving the IDs TSV file.
    """
    gene_list = gene_assembler.get_genes()
    output_list = []
    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Generating phyloprofile ids"):
        protein_list = gene.get_proteins(False, True)
        for protein in protein_list:
            output_list.append(protein.make_header() + "\tncbi" + str(protein.get_id_taxon()))

    with open(pass_path["transcript_ids"], "w") as f:
        f.write("\n".join(output_list))

    library_info["status"]["08_id_tsv_generation"] = True
    library_info.save()


def main():
    parser = argparse.ArgumentParser(description="Process gene library to generate implicit FAS scores, FASTA, pairings, and IDs.")
    parser.add_argument('--library_dir', type=str, required=True, help='Root directory of the gene library.')

    args = parser.parse_args()

    # Automatically read paths.json and info.yaml from the provided output directory
    paths_json_path = os.path.join(args.library_dir, "paths.json")
    if not os.path.exists(paths_json_path):
        raise FileNotFoundError(f"The paths.json file was not found at the specified location: {paths_json_path}")

    with open(paths_json_path, "r") as f:
        paths_dict = json.load(f)

    pass_path = PassPath(paths_dict)

    info_yaml_path = os.path.join(args.library_dir, "info.yaml")
    if not os.path.exists(info_yaml_path):
        raise FileNotFoundError(f"The info.yaml file was not found at the specified location: {info_yaml_path}")

    with open(info_yaml_path, "r") as f:
        library_info_data = yaml.safe_load(f)

    library_info = LibraryInfo(info_yaml_path)
    species = library_info_data["info"]["species"]
    taxon_id = library_info_data["info"]["taxon_id"]

    gene_assembler = GeneAssembler(species, taxon_id)
    gene_assembler.load(pass_path)

    # Step 5: Calculate implicit FAS scores
    calculate_implicit_fas_scores(gene_assembler, library_info, pass_path)

    # Step 6: Generate FASTA file
    generate_fasta_file(gene_assembler, library_info, pass_path)

    # Step 7: Generate Pairings
    generate_pairings(gene_assembler, library_info, pass_path)

    # Step 8: Generate IDs TSV
    generate_ids_tsv(gene_assembler, library_info, pass_path)


if __name__ == "__main__":
    main()
