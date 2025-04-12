#!/bin/env python

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
