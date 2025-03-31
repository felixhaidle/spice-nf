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

def remove_incorrect_entries(gene_assembler, pass_path, prefix_mapping):
    """
    Remove incorrect entries from the library based on taxon-specific filtering logic.

    Args:
    - gene_assembler (GeneAssembler): The gene assembler object containing the gene data.
    - pass_path (str): Path to save the filtered output.
    - taxon_prefix_mapping (dict): Dictionary mapping taxon IDs to their Ensembl prefixes.
    """
    gene_list = gene_assembler.get_genes()

    with open(prefix_mapping, "r", encoding="utf-8") as file:
        taxon_prefix_mapping = json.load(file)

    # Convert keys to strings to avoid mismatches
    taxon_prefix_mapping = {str(k): v for k, v in taxon_prefix_mapping.items()}
    for gene in tqdm(gene_list, ncols=100, total=len(gene_list), desc="Incorrect entry removal progress"):
        transcript_list = gene.get_transcripts()
        for transcript in transcript_list:
            transcript_id = transcript.get_id()
            gene_id = gene.get_id()
            taxon_id = str(transcript.get_id_taxon())

            print(f"Checking transcript {transcript_id} from gene {gene_id} (Taxon: {taxon_id})")

            if transcript.get_biotype() == "protein_coding":
                print("  - Biotype is protein_coding")

                if str(taxon_id) in taxon_prefix_mapping:
                    species_prefix = taxon_prefix_mapping[taxon_id]
                    prefix_length = len(species_prefix)

                    print(f"  - Found species prefix '{species_prefix}' (Length: {prefix_length})")

                    # Check if the character at the correct index is "T"
                    char_at_index = transcript_id[prefix_length] if len(transcript_id) > prefix_length else "N/A"
                    print(f"  - Character at index {prefix_length} is: {char_at_index}")

                    if char_at_index == "T":
                        if "NOVEL" not in transcript.get_tags():
                            print(f"  - 'NOVEL' tag not found in tags {transcript.get_tags()}, deleting transcript {transcript_id}")
                            gene.delete_transcript(transcript.get_id())
                        else:
                            print(f"  - 'NOVEL' tag found in tags {transcript.get_tags()}, keeping transcript {transcript_id}")
                    else:
                        print(f"  - Character at index {prefix_length} is not 'T', skipping transcript {transcript_id}")
                else:
                    print(f"  - Taxon ID {taxon_id} not found in prefix mapping, skipping transcript {transcript_id}")
            else:
                print(f"  - Biotype is not protein_coding (found {transcript.get_biotype()}), skipping transcript {transcript_id}")

    gene_assembler.clear_empty_genes()
    gene_assembler.save_seq(pass_path)
    gene_assembler.save_fas(pass_path)
    gene_assembler.save_info(pass_path)


def filter_gene_library(library_dir,taxon_prefixes):
    """
    Filter the gene library by removing incorrect entries.

    Args:
    - library_dir (str): The root directory of the gene library.
    -
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
    remove_incorrect_entries(gene_assembler,pass_path,taxon_prefixes)

    # Save the filtered library
    print("Saving the filtered gene library...")
    gene_assembler.save_seq(pass_path)
    library_info_object = LibraryInfo(library_info_path)
    library_info_object.save()

    print("Filtering complete.")

def main():
    parser = argparse.ArgumentParser(description="Filter gene library by removing incorrect entries.")
    parser.add_argument('--library_dir', type=str, required=True, help='Root directory of the gene library.')
    parser.add_argument('--taxon_prefixes', type=str, required=True, help='JSON file with the stable identifier prefixes for the ENSEMBL species')

    args = parser.parse_args()

    # Perform filtering on the provided library directory
    filter_gene_library(args.library_dir,args.taxon_prefixes)

if __name__ == "__main__":
    main()
