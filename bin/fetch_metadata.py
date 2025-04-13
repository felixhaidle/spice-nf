#!/bin/env python

#######################################################################
# Copyright (C) 2025 Felix Haidle
#
# This file is part of spice_library_pipeline.
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
#######################################################################

import sys
import argparse
from Classes.API.ensembl_mod.EnsemblUtils import get_species_info, get_id_taxon

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--species', required=True)
    parser.add_argument('--use_placeholder', action='store_true')
    args = parser.parse_args()

    if args.use_placeholder:
        species_name = args.species
        taxon_id = "99999999"
        release = "custom"
    else:
        try:
            metadata = get_species_info(args.species)
            species_name = metadata["name"]
            taxon_id = get_id_taxon(species_name)
            release = "custom"
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            exit(1)

    print(f"{species_name}\t{taxon_id}\t{release}")


if __name__ == "__main__":
    main()
