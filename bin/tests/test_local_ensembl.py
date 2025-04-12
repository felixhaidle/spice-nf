#!/bin/env python

import unittest
from unittest.mock import patch
from Classes.API.ensembl_mod.LocalEnsembl import LocalEnsembl

class TestLocalEnsembl(unittest.TestCase):

    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_species_info")
    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_id_taxon")
    def test_mocked_ftp_url_generation(self, mock_get_taxon, mock_get_species_info):
        mock_get_species_info.return_value = {
            "name": "Arabidopsis thaliana",
            "url_name": "arabidopsis_thaliana",
            "assembly_default": "TAIR10",
            "division": "EnsemblPlants"
        }
        mock_get_taxon.return_value = "3702"

        le = LocalEnsembl(
            raw_species="arabidopsis_thaliana",
            goal_directory="/tmp",
            release="58",
            metadata_mode="auto"
        )

        gtf_url = le.build_ftp_url("gtf")
        pep_url = le.build_ftp_url("pep")

        self.assertIn("plants/release-58/gtf/arabidopsis_thaliana", gtf_url)
        self.assertIn("Arabidopsis_thaliana.TAIR10.58.gtf.gz", gtf_url)
        self.assertIn("plants/release-58/fasta/arabidopsis_thaliana/pep", pep_url)
        self.assertIn("Arabidopsis_thaliana.TAIR10.pep.all.fa.gz", pep_url)

    def test_placeholder_metadata(self):
        le = LocalEnsembl(
            raw_species="arabidopsis_thaliana",
            goal_directory="/tmp",
            metadata_mode="placeholder"
        )

        self.assertEqual(le.species_name, "custom_species")
        self.assertEqual(le.taxon_id, "999999")

    def test_placeholder_ftp_url_generation(self):
        le = LocalEnsembl(
            raw_species="arabidopsis_thaliana",
            goal_directory="/tmp",
            release="58",
            metadata_mode="placeholder",
            division="EnsemblPlants"
        )

        gtf_url = le.build_ftp_url("gtf")
        pep_url = le.build_ftp_url("pep")

        self.assertIn("plants/release-58/gtf/custom_species", gtf_url)
        self.assertIn("custom_species.custom_assembly.58.gtf.gz", gtf_url)
        self.assertIn("plants/release-58/fasta/custom_species/pep", pep_url)
        self.assertIn("custom_species.custom_assembly.pep.all.fa.gz", pep_url)

    def test_invalid_file_type(self):
        le = LocalEnsembl(
            raw_species="anything",
            goal_directory="/tmp",
            metadata_mode="placeholder"
        )

        with self.assertRaises(ValueError):
            le.build_ftp_url("cds")  # Invalid file type


if __name__ == "__main__":
    unittest.main()
