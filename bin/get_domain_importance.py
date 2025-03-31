#!/bin/env python

#######################################################################
# Portions Copyright (C) 2022 Julian Dosch
# Copyright (C) 2025 Felix Haidle
#
# This file is part of spice_library_pipeline and includes adapted
# code originally from the SPICE project (get_domain_importance.py).
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
#   - Adapted by Felix Haidle in 2025 from SPICE's get_domain_importance.py.
#######################################################################


import argparse
import json
import os
from pathlib import Path


def option_parse():
    """
    Parses command-line arguments and triggers the main processing function.

    Required Arguments:
    -i / --inPath: Path to the input JSON file (contains isoform annotations).
    -o / --outPath: Output directory for the resulting JSON.

    Optional Arguments:
    -l / --isoformList: Optional TSV file containing isoforms of interest (filtered by condition).
    """
    parser = argparse.ArgumentParser(
        epilog="This script uses the annotation file of the different protein isoforms of each gene "
               "in a proteome to generate a dictionary of features that have presence/absence changes due to AS."
    )
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    required.add_argument("-i", "--inPath", type=str, required=True,
                          help="Path to input JSON containing isoform annotations.")
    required.add_argument("-o", "--outPath", type=str, required=True,
                          help="Output directory. Result file will be named important_features.json.")
    optional.add_argument("-l", "--isoformList", default=None, type=str, required=False,
                          help="Optional: TSV file listing relevant (expressed) isoforms for comparison.")

    args = parser.parse_args()
    main(args.inPath, args.outPath, args.isoformList)


def main(inpath, outpath, isoformlist):
    """
    Main processing logic.

    Args:
        inpath (str): Path to isoform annotation JSON.
        outpath (str): Directory to write output.
        isoformlist (str | None): Optional path to isoform list file.
    """
    rel_isoforms = None
    if isoformlist:
        rel_isoforms = read_isoformlist(isoformlist)

    genes = read_input(inpath, rel_isoforms)
    output = get_fdict(genes)
    save2json(output, outpath)


def read_isoformlist(path):
    """
    Parses a TSV file containing relevant isoforms per gene.

    Args:
        path (str): Path to the TSV file.

    Returns:
        dict: {gene_id: [isoform1, isoform2, ...]}
    """
    isoformdict = {}
    with open(path, 'r') as infile:
        for line in infile:
            cells = line.rstrip('\n').split('\t')
            if not (cells[0] == 'gene_id' or line[0] == '!'):
                isoformdict[cells[0]] = cells[1].split(';')
    return isoformdict


def save2json(dict2save, directory):
    """
    Saves a dictionary to a JSON file named 'important_features.json' in the given directory.

    Args:
        dict2save (dict): Data to be written.
        directory (str): Output directory path.
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    jsonOut = json.dumps(dict2save, ensure_ascii=False)
    with open(f"{directory}/important_features.json", 'w') as out:
        out.write(jsonOut)


def get_fdict(genes):
    """
    Generates a dictionary of features/clans that are alternatively spliced (variable across isoforms).

    Returns:
        dict: {feature_or_clan: [gene1, gene2, ...]}
    """
    f_dict = {}
    for gene in genes:
        f_list = []

        # Collect features/clans that vary across isoforms
        for isoform in genes[gene]['isoforms']:
            iso = genes[gene]['isoforms'][isoform]

            # Check domain features
            for feature in iso['types']:
                if feature not in f_list and iso['types'][feature] < genes[gene]['max'][feature]:
                    f_list.append(feature)

            # Check clans (higher-level domain families)
            for clan in iso['clans']:
                if clan not in f_list and iso['clans'][clan] < genes[gene]['max'][clan]:
                    f_list.append(clan)

        # Add features/clans to the global feature dictionary
        for feature in f_list:
            if feature not in f_dict:
                f_dict[feature] = []
            f_dict[feature].append(gene)

    return f_dict


def read_input(inpath, isoformlist):
    """
    Reads isoform annotation data and structures it by gene, isoform, and features/clans.

    Args:
        inpath (str): Path to input annotation JSON.
        isoformlist (dict | None): Optional filter to include only relevant isoforms.

    Returns:
        dict: Structured annotation data:
              {
                  gene_id: {
                      'max': {feature/clan: max_count},
                      'isoforms': {
                          isoform_id: {
                              'types': {feature: count},
                              'clans': {clan: count}
                          }
                      }
                  }
              }
    """
    with open(inpath, 'r') as infile:
        in_dict = json.loads(infile.read())
        features, clans = in_dict['feature'], in_dict['clan']

    genes = {}

    for protein in features:
        gid, pid, tid = protein.split('|')  # Extract gene ID and protein isoform ID
        gtmp = True

        if isoformlist and gid not in isoformlist:
            gtmp = False

        if gtmp:
            if gid not in genes:
                genes[gid] = {'max': {}, 'isoforms': {}}

            isotmp = True
            if isoformlist and pid not in isoformlist[gid]:
                isotmp = False

            if isotmp:
                genes[gid]['isoforms'][pid] = {'types': {}, 'clans': {}}

                for tool in features[protein]:
                    if tool != "length":
                        for ftype in features[protein][tool]:
                            count = len(features[protein][tool][ftype]["instance"])

                            # Update max observed count for this feature
                            if ftype not in genes[gid]['max'] or count > genes[gid]['max'][ftype]:
                                genes[gid]['max'][ftype] = count

                            genes[gid]['isoforms'][pid]['types'][ftype] = count

                            # Handle clan aggregation
                            if ftype in clans:
                                clan = clans[ftype]
                                genes[gid]['isoforms'][pid]['clans'].setdefault(clan, 0)
                                genes[gid]['isoforms'][pid]['clans'][clan] += count

                # Update max observed count for each clan
                for clan, count in genes[gid]['isoforms'][pid]['clans'].items():
                    if clan not in genes[gid]['max'] or count > genes[gid]['max'][clan]:
                        genes[gid]['max'][clan] = count

    return genes


if __name__ == '__main__':
    option_parse()
