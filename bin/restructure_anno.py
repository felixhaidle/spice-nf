#!/bin/env python

#######################################################################
# Copyright (C) 2022 Julian Dosch
#
# This file is part of main.
#
#  get_domain_importance is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  get_domain_importance is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PathwayTrace.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import argparse
import json
import os
from pathlib import Path

def option_parse():
    """
    Parses command-line arguments and triggers the main process.

    Required Arguments:
    -i / --inPath: Path to the input JSON file.
    -o / --outPath: Path to the output directory.

    Optional Arguments:
    -c / --genesPerFile: Number of genes to include in each output file. Default is 100.
    """
    parser = argparse.ArgumentParser(
        epilog="This script restructures the annotation file format into a mapped version where each feature instance "
               "of a protein gets an ID. This is to make saving linearized architectures less data heavy."
    )
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument("-i", "--inPath", default='.', type=str, required=True,
                          help="Path to input JSON file containing feature annotations.")
    required.add_argument("-o", "--outPath", default='.', type=str, required=True,
                          help="Path to output directory. Output filenames are based on the input.")
    optional.add_argument("-c", "--genesPerFile", default=100, type=int, required=False,
                          help="Number of genes per output file. Larger number results in fewer, larger files.")

    args = parser.parse_args()
    main(args.inPath, args.outPath, args.genesPerFile)


def main(inpath, outpath, filesize):
    """
    Reads the input file, restructures the annotation data by gene,
    splits it into smaller JSON files, and creates an index file.

    Args:
        inpath (str): Path to the input JSON file.
        outpath (str): Directory where output files will be saved.
        filesize (int): Number of genes per output file.
    """
    arc = read_input(inpath)
    index = 0  # File index counter
    count = 0  # Gene counter
    output = {}  # Temp dictionary for batch output
    indexout = {'genes': {}}  # Mapping from gene ID to output file index

    for gene in arc:
        output[gene] = arc[gene]
        indexout['genes'][gene] = index
        count += 1

        # Save current batch if it hits the file size limit
        if count > filesize:
            name = str(index).rjust(9, '0')  # Padded file name
            save2json(output, name, outpath)
            output = {}
            index += 1
            count = 0

    # Save any remaining genes
    name = str(index).rjust(9, '0')
    save2json(output, name, outpath)

    # Save the index file mapping genes to their output files
    indexout['#files'] = index
    save2json(indexout, 'index', outpath)


def save2json(dict2save, name, directory):
    """
    Serializes a dictionary to JSON and writes it to a file.

    Args:
        dict2save (dict): Dictionary to be saved.
        name (str): Output filename (without extension).
        directory (str): Output directory path.
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    jsonOut = json.dumps(dict2save, ensure_ascii=False)
    with open(f"{directory}/{name}.json", 'w') as out:
        out.write(jsonOut)


def read_input(inpath):
    """
    Reads and restructures the input JSON file into a nested gene-centric dictionary.

    Args:
        inpath (str): Path to the input JSON file.

    Returns:
        dict: Nested dictionary of structure:
              {gene_id: {protein_id: {'length': int, 'fmap': {int: (feature_type, start, end)}}}}
    """
    fa_map = {}
    with open(inpath, 'r') as infile:
        features = json.loads(infile.read())['feature']

        for protid in features:
            gid, pid, tid = protid.split('|')  # Extract gene, protein, and transcript IDs

            if gid not in fa_map:
                fa_map[gid] = {}

            fa_map[gid][pid] = {'fmap': {}}
            i = 0  # Instance index

            for tool in features[protid]:
                if tool == 'length':
                    fa_map[gid][pid]['length'] = features[protid]['length']
                else:
                    for feature in features[protid][tool]:
                        for instance in features[protid][tool][feature]['instance']:
                            fa_map[gid][pid]['fmap'][i] = (feature, instance[0], instance[1])
                            i += 1
    return fa_map


if __name__ == '__main__':
    option_parse()
