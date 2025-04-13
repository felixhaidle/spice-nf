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

import unittest
from unittest.mock import patch, MagicMock
from Classes.API.ensembl_mod.EnsemblUtils import (
    chunks, make_request_data, get_species_info, get_id_taxon
)

class TestEnsemblUtils(unittest.TestCase):

    def test_chunks(self):
        data = ['a', 'b', 'c', 'd', 'e']
        result = list(chunks(data, 2))
        self.assertEqual(result, [['a', 'b'], ['c', 'd'], ['e']])

    def test_make_request_data(self):
        ids = ['ENSG0001', 'ENSG0002']
        expected = '{ "ids" : ["ENSG0001", "ENSG0002" ] }'
        self.assertEqual(make_request_data(ids), expected)

    @patch('Classes.API.ensembl_mod.EnsemblUtils.requests.get')
    def test_get_species_info(self, mock_get):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "name": "Arabidopsis thaliana",
            "url_name": "arabidopsis_thaliana",
            "assembly_default": "TAIR10",
            "division": "EnsemblPlants"
        }
        mock_get.return_value = mock_response

        result = get_species_info("arabidopsis_thaliana")
        self.assertEqual(result["name"], "Arabidopsis thaliana")
        self.assertEqual(result["division"], "EnsemblPlants")

    @patch('Classes.API.ensembl_mod.EnsemblUtils.requests.get')
    def test_get_id_taxon(self, mock_get):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = [
            {"species_taxonomy_id": "3702"}
        ]
        mock_get.return_value = mock_response

        taxon_id = get_id_taxon("arabidopsis_thaliana")
        self.assertEqual(taxon_id, "3702")


if __name__ == '__main__':
    unittest.main()
