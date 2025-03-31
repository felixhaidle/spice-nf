#!/bin/env python

#######################################################################
# Portions Copyright (C) 2022 Julian Dosch
# Copyright (C) 2025 Felix Haidle
#
# This file is part of spice_library_pipeline and includes adapted
# code originally from the get_domain_importance module in the main project.
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
#   - Adapted by Felix Haidle in 2025 for spice_library_pipeline.
#######################################################################



import argparse
import json
import os
from pathlib import Path


def option_parse():
    """
    Parses command-line arguments and calls the main processing function.

    Required Arguments:
    -f / --forwardPath: Path to _forward.domains file.
    -r / --reversePath: Path to _reverse.domains file.
    -m / --mapPath: Path to the feature mapping JSON directory.
    -o / --outPath: Output directory for processed JSON output.
    """
    parser = argparse.ArgumentParser(
        epilog="This script restructures the annotation file format into a mapped version "
               "where each feature instance of a protein gets an ID. This is to make saving "
               "linearized architectures less data heavy."
    )
    required = parser.add_argument_group('required arguments')

    required.add_argument("-f", "--forwardPath", type=str, required=True,
                          help="Path to _forward.domains file.")
    required.add_argument("-r", "--reversePath", type=str, required=True,
                          help="Path to _reverse.domains file.")
    required.add_argument("-m", "--mapPath", type=str, required=True,
                          help="Path to feature mapping JSON directory.")
    required.add_argument("-o", "--outPath", type=str, required=True,
                          help="Path to output directory.")

    args = parser.parse_args()
    main(args.forwardPath, args.reversePath, args.mapPath, args.outPath)


def main(forwardpath, reversepath, mappath, outpath):
    """
    Loads the index from the mapping directory and calls the input reader.

    Args:
        forwardpath (str): Path to _forward.domains file.
        reversepath (str): Path to _reverse.domains file.
        mappath (str): Path to directory containing index.json and mapping files.
        outpath (str): Output directory for resulting JSON files.
    """
    with open(f"{mappath}/index.json", 'r') as infile:
        files = json.loads(infile.read())['#files']
    read_input((forwardpath, reversepath), mappath, files, outpath)


def save2json(dict2save, name, directory):
    """
    Saves a dictionary to a JSON file in the specified directory.

    Args:
        dict2save (dict): Data to save.
        name (str): Name of the output file (without extension).
        directory (str): Output directory.
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    jsonOut = json.dumps(dict2save, ensure_ascii=False)
    with open(f"{directory}/{name}.json", 'w') as out:
        out.write(jsonOut)


def read_input(inpaths, mappath, files, outpath):
    """
    Processes the forward and reverse domain files to create feature path mappings
    for each gene using the provided mapping files.

    Args:
        inpaths (tuple): Tuple of paths to (forward.domains, reverse.domains).
        mappath (str): Directory containing mapping JSON files.
        files (int): Number of mapping files to iterate through.
        outpath (str): Directory to write the output JSON files.
    """
    for i in [0, 1]:  # 0 = forward, 1 = reverse
        with open(inpaths[i], 'r') as infile:
            lines = infile.readlines()

        index2 = {}     # Maps gene ID to (start, end) line indices in the domains file
        y = 0
        current = None

        # Parse domain lines to find ranges for each gene
        for line in lines:
            if line == '\n' or line.startswith('#'):
                y += 1
                continue

            gid = line.split('|')[0]

            if gid not in index2:
                index2[gid] = [y]

            if current and gid != current:
                index2[current].append(y)
                current = gid

            if not current:
                current = gid

            y += 1

        index2[current].append(y)

        # Process each mapping file
        for index in range(files + 1):
            mapfile_path = f"{mappath}/{str(index).rjust(9, '0')}.json"
            with open(mapfile_path, 'r') as infile2:
                mapfile = json.loads(infile2.read())

            if i == 0:
                lin = {}  # Initialize new output
            else:
                # Load existing forward results to extend them with reverse data
                with open(f"{outpath}/{str(index).rjust(9, '0')}_paths.json", 'r') as pathfile:
                    lin = json.loads(pathfile.read())

            for gene in mapfile:
                if gene in index2:
                    start, end = index2[gene]
                    for z in range(start, end):
                        line = lines[z]
                        cells = line.rstrip('\n').split('\t')

                        if line == '\n' or line.startswith('#'):
                            continue

                        # Get protein IDs depending on direction
                        if i == 0:
                            p1, p2 = cells[0].split('#')
                        else:
                            p2, p1 = cells[0].split('#')

                        if p1 == p2:
                            continue

                        gid, p1, tax = p1.split('|')
                        p2 = p2.split('|')[1]

                        if gid not in lin:
                            lin[gid] = {}

                        pkey = '@'.join((p1, p2))

                        if pkey not in lin[gid]:
                            lin[gid][pkey] = [[], []]

                        rp = cells[1].split('|')[1]

                        if cells[7] == 'Y':
                            fid = None
                            x = 0
                            # Look up feature ID by matching attributes
                            while fid is None:
                                fmap_entry = mapfile[gid][rp]['fmap'][str(x)]
                                if (
                                    fmap_entry[0] == cells[3] and
                                    fmap_entry[1] == int(cells[4]) and
                                    fmap_entry[2] == int(cells[5])
                                ):
                                    fid = str(x)
                                x += 1

                            # Assign feature ID to correct direction
                            if rp == p1:
                                lin[gid][pkey][0].append(fid)
                            elif rp == p2:
                                lin[gid][pkey][1].append(fid)

            # Save result for this file
            save2json(lin, f"{str(index).rjust(9, '0')}_paths", outpath)


if __name__ == '__main__':
    option_parse()
