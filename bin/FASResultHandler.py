#!/bin/env python

#######################################################################
# Copyright (C) 2023 Christian Bluemel
#
# This file is part of Spice.
#
#  FASResultHandler is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  FASResultHandler is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Spice.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import json
import os
from typing import Dict, Any, List

from Classes.PassPath.PassPath import PassPath
from Classes.ReduxArgParse.ReduxArgParse import ReduxArgParse
from Classes.SequenceHandling.GeneAssembler import GeneAssembler
from Classes.SequenceHandling.LibraryInfo import LibraryInfo
from Classes.WriteGuard.WriteGuard import WriteGuard


def main():
    """
    Multipurpose CLI for handling FAS-related gene annotations.

    Modes supported:
    - unpack: Extract a specific gene's pairing info from JSON and save to TSV
    - delete: Delete all FAS-related intermediate files for a gene
    - concat: Append gene-specific results into global annotation files
    - integrate: Integrate per-gene FAS scores into the full library assembly
    """
    argument_parser: ReduxArgParse = ReduxArgParse(
        ["--pairings_path", "--gene_id", "--out_dir", "--mode", "--anno_dir"],
        [str, str, str, str, str],
        ["store", "store", "store", "store", "store"],
        [None, None, None, None, None],
        [
            "Path to the pairings TSV.",
            "Gene ID to operate on.",
            "Directory where gene-specific FAS results are stored.",
            "Operation to perform: 'unpack', 'concat', 'delete', or 'integrate'.",
            "Annotation directory containing global FAS files (e.g., fas.phyloprofile)."
        ]
    )

    argument_parser.generate_parser()
    argument_parser.execute()
    argument_dict: Dict[str, Any] = argument_parser.get_args()

    mode = argument_dict['mode']

    if mode == "unpack":
        # Extract a specific gene's pairing from JSON and write to file
        with open(argument_dict["pairings_path"], "r") as f:
            json_data = json.load(f)

        gene_id = argument_dict['gene_id']
        if gene_id not in json_data:
            print(f"Gene ID '{gene_id}' not found in JSON. Skipping...")
        else:
            output_path = os.path.join(argument_dict["out_dir"], f"{gene_id}.tsv")
            with open(output_path, "w") as f:
                f.write(json_data[gene_id])

    elif mode == "delete":
        # Remove all temporary/intermediate FAS files for this gene
        gid = argument_dict['gene_id']
        out_dir = argument_dict["out_dir"]
        for suffix in [".tsv", "_forward.domains", "_reverse.domains", "_config.yml", ".phyloprofile"]:
            file_path = os.path.join(out_dir, gid + suffix)
            if os.path.exists(file_path):
                os.remove(file_path)

    elif mode == "concat":
        # Append gene-specific results to global files (requires WriteGuard for locking)
        gid = argument_dict['gene_id']
        out_dir = argument_dict["out_dir"]
        anno_dir = argument_dict["anno_dir"]

        # Append to fas.phyloprofile (excluding header line)
        with WriteGuard(os.path.join(anno_dir, "fas.phyloprofile"), anno_dir):
            with open(os.path.join(out_dir, f"{gid}.phyloprofile"), "r") as f_in:
                fas_scores = "\n".join(f_in.read().split("\n")[1:])
            with open(os.path.join(anno_dir, "fas.phyloprofile"), "a") as f_out:
                f_out.write(fas_scores)

        # Append forward domains
        with WriteGuard(os.path.join(anno_dir, "forward.domains"), anno_dir):
            with open(os.path.join(out_dir, f"{gid}_forward.domains"), "r") as f_in:
                forward_data = f_in.read()
            with open(os.path.join(anno_dir, "forward.domains"), "a") as f_out:
                f_out.write(forward_data)

        # Append reverse domains
        with WriteGuard(os.path.join(anno_dir, "reverse.domains"), anno_dir):
            with open(os.path.join(out_dir, f"{gid}_reverse.domains"), "r") as f_in:
                reverse_data = f_in.read()
            with open(os.path.join(anno_dir, "reverse.domains"), "a") as f_out:
                f_out.write(reverse_data)

    elif mode == "integrate":
        # Load gene library and inject FAS scores into its internal structure
        lib_path_dir = os.path.join("/".join(argument_dict["anno_dir"].split("/")[:-1]), "paths.json")
        with open(lib_path_dir, "r") as f:
            path_dict = json.load(f)

        pass_path = PassPath(path_dict)
        lib_info = LibraryInfo(pass_path["info"])
        gene_assembler = GeneAssembler(
            lib_info["info"]["species"],
            str(lib_info["info"]["taxon_id"])
        )
        gene_assembler.load(pass_path)

        # Read FAS scores into a nested dictionary
        fas_scores_dict: Dict[str, Dict[str, Dict[str, float]]] = {}
        with open(os.path.join(argument_dict["anno_dir"], "fas.phyloprofile")) as f_in:
            fas_score_lines = f_in.read().split("\n")[1:]

        for line in fas_score_lines:
            if not line.strip():
                continue
            split_line = line.split("\t")
            seed = split_line[0]
            query = split_line[2]
            fas_1 = float(split_line[3])
            fas_2 = float(split_line[4])

            gene_id = seed.split("|")[0]
            seed_prot = seed.split("|")[1]
            query_prot = query.split("|")[1]

            fas_scores_dict.setdefault(gene_id, {})
            fas_scores_dict[gene_id].setdefault(seed_prot, {})
            fas_scores_dict[gene_id].setdefault(query_prot, {})

            fas_scores_dict[gene_id][seed_prot][query_prot] = fas_2
            fas_scores_dict[gene_id][query_prot][seed_prot] = fas_1

        # Inject scores into gene objects
        for gene in gene_assembler.get_genes():
            gid = gene.get_id()
            if gid in fas_scores_dict:
                for prot1 in fas_scores_dict[gid]:
                    for prot2 in fas_scores_dict[gid][prot1]:
                        gene.get_fas_dict()[prot1][prot2] = fas_scores_dict[gid][prot1][prot2]

        # Save updated FAS annotations
        gene_assembler.save_fas(pass_path)


if __name__ == "__main__":
    main()
