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
import yaml
from tqdm import tqdm



# Import necessary classes from SPICE library
from Classes.SequenceHandling.GeneAssembler import GeneAssembler
from Classes.SequenceHandling.LibraryInfo import LibraryInfo
from Classes.PassPath.PassPath import PassPath

def calculate_implicit_fas_scores(gene_assembler: GeneAssembler, library_info: LibraryInfo, pass_path: PassPath):
    """
    Step 5: Calculate implicit FAS scores for all genes.

    Iterates through each gene to compute its Functional Annotation Score (FAS), which assesses
    the diversity and completeness of annotated features. Scores are saved and library status is updated.

    Args:
        gene_assembler (GeneAssembler): Contains all loaded gene data.
        library_info (LibraryInfo): Stores metadata and processing status.
        pass_path (PassPath): File paths used for saving results.
    """
    gene_list = gene_assembler.get_genes()
    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Implicit FAS score collection progress"):
        gene.calculate_implicit_fas_scores()

    gene_assembler.save_fas(pass_path)
    library_info["status"]["05_implicit_fas_scoring"] = True
    library_info.save()


def generate_fasta_file(gene_assembler: GeneAssembler, library_info: LibraryInfo, pass_path: PassPath):
    """
    Step 6: Generate a FASTA file for all gene transcripts.

    Collates sequences into a single FASTA file. Required for tools relying on raw sequences.

    Args:
        gene_assembler (GeneAssembler): Contains gene and sequence data.
        library_info (LibraryInfo): Tracks pipeline progress.
        pass_path (PassPath): Destination path for FASTA output.
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
    Step 7: Generate pairings (relationships) between isoforms of each gene.

    Useful for comparative studies and understanding alternative splicing.

    Args:
        gene_assembler (GeneAssembler): Contains gene objects with transcript structures.
        library_info (LibraryInfo): Tracks progress and saves metadata.
        pass_path (PassPath): Path to store the pairing results in JSON format.
    """
    gene_list = gene_assembler.get_genes(False,True)
    pairings_dict = {}

    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Pairing generation process"):
        pairings_dict[gene.get_id()] = gene.make_pairings()

    with open(pass_path["transcript_pairings"], "w") as f:
        json.dump(pairings_dict, f, indent=4)

    library_info["status"]["07_pairing_generation"] = True
    library_info.save()


def generate_ids_tsv(gene_assembler: GeneAssembler, library_info: LibraryInfo, pass_path: PassPath):
    """
    Step 8: Generate a TSV file containing unique protein IDs with taxonomic information.

    Args:
        gene_assembler (GeneAssembler): Contains protein sequences and metadata.
        library_info (LibraryInfo): Tracks status and stores info.yaml.
        pass_path (PassPath): Target file path for the output TSV.
    """
    gene_list = gene_assembler.get_genes()
    output_list = []

    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Generating phyloprofile ids"):
        protein_list = gene.get_proteins(False, True)
        for protein in protein_list:
            line = protein.make_header() + "\tncbi" + str(protein.get_id_taxon())
            output_list.append(line)

    with open(pass_path["transcript_ids"], "w") as f:
        f.write("\n".join(output_list))

    library_info["status"]["08_id_tsv_generation"] = True
    library_info.save()


def main():
    """
    Entry point for running steps 5–8 of the annotation pipeline.

    Loads gene data and metadata, then executes:
    - Implicit FAS score calculation
    - FASTA file generation
    - Isoform pairing extraction
    - Phyloprofile ID TSV creation
    """
    parser = argparse.ArgumentParser(
        description="Process gene library to generate implicit FAS scores, FASTA, pairings, and IDs."
    )
    parser.add_argument('--library_dir', type=str, required=True,
                        help='Root directory of the gene library containing paths.json and info.yaml.')

    args = parser.parse_args()

    # Validate required files
    paths_json_path = os.path.join(args.library_dir, "paths.json")
    if not os.path.exists(paths_json_path):
        raise FileNotFoundError(f"paths.json not found at: {paths_json_path}")

    info_yaml_path = os.path.join(args.library_dir, "info.yaml")
    if not os.path.exists(info_yaml_path):
        raise FileNotFoundError(f"info.yaml not found at: {info_yaml_path}")

    # Load configuration and metadata
    with open(paths_json_path, "r") as f:
        paths_dict = json.load(f)
    pass_path = PassPath(paths_dict)

    with open(info_yaml_path, "r") as f:
        library_info_data = yaml.safe_load(f)
    library_info = LibraryInfo(info_yaml_path)

    species = library_info_data["info"]["species"]
    taxon_id = library_info_data["info"]["taxon_id"]

    # Initialize and load gene data
    gene_assembler = GeneAssembler(species, taxon_id)
    gene_assembler.load(pass_path)

    # Pipeline steps
    calculate_implicit_fas_scores(gene_assembler, library_info, pass_path)
    generate_fasta_file(gene_assembler, library_info, pass_path)
    generate_pairings(gene_assembler, library_info, pass_path)
    generate_ids_tsv(gene_assembler, library_info, pass_path)


if __name__ == "__main__":
    main()
