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
from unittest.mock import patch
from Classes.API.ensembl_mod.LocalEnsembl import LocalEnsembl

class TestLocalEnsembl(unittest.TestCase):

    # === General logic ===

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

    # === Division-specific FTP tests ===

    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_species_info")
    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_id_taxon")
    def test_ftp_url_fungi(self, mock_get_taxon, mock_get_species_info):
        mock_get_species_info.return_value = {
            "name": "Saccharomyces cerevisiae",
            "url_name": "saccharomyces_cerevisiae",
            "assembly_default": "R64-1-1",
            "division": "EnsemblFungi"
        }
        mock_get_taxon.return_value = "4932"

        le = LocalEnsembl(
            raw_species="saccharomyces_cerevisiae",
            goal_directory="/tmp",
            release="58",
            metadata_mode="auto"
        )

        gtf_url = le.build_ftp_url("gtf")
        self.assertIn("fungi/release-58/gtf/saccharomyces_cerevisiae", gtf_url)
        self.assertIn("Saccharomyces_cerevisiae.R64-1-1.58.gtf.gz", gtf_url)

    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_species_info")
    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_id_taxon")
    def test_ftp_url_metazoa(self, mock_get_taxon, mock_get_species_info):
        mock_get_species_info.return_value = {
            "name": "Drosophila melanogaster",
            "url_name": "drosophila_melanogaster",
            "assembly_default": "BDGP6.46",
            "division": "EnsemblMetazoa"
        }
        mock_get_taxon.return_value = "7227"

        le = LocalEnsembl(
            raw_species="drosophila_melanogaster",
            goal_directory="/tmp",
            release="58",
            metadata_mode="auto"
        )

        gtf_url = le.build_ftp_url("gtf")
        self.assertIn("metazoa/release-58/gtf/drosophila_melanogaster", gtf_url)
        self.assertRegex(gtf_url, r"Drosophila_melanogaster\.BDGP6\..*\.58\.gtf\.gz")


    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_species_info")
    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_id_taxon")
    def test_ftp_url_ensembl(self, mock_get_taxon, mock_get_species_info):
        mock_get_species_info.return_value = {
            "name": "Homo sapiens",
            "url_name": "homo_sapiens",
            "assembly_default": "GRCh38",
            "division": "Ensembl"
        }
        mock_get_taxon.return_value = "9606"

        le = LocalEnsembl(
            raw_species="homo_sapiens",
            goal_directory="/tmp",
            release="113",
            metadata_mode="auto"
        )

        gtf_url = le.build_ftp_url("gtf")
        self.assertIn("ensembl.org/pub/release-113/gtf/homo_sapiens", gtf_url)
        self.assertIn("Homo_sapiens.GRCh38.113.gtf.gz", gtf_url)

    # === Release logic ===

    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_species_info")
    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_id_taxon")
    def test_current_release_fallback(self, mock_get_taxon, mock_get_species_info):
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
            release=-1,
            metadata_mode="auto"
        )

        gtf_url = le.build_ftp_url("gtf")
        self.assertIn("/plants/release-", gtf_url)
        self.assertIn("/gtf/arabidopsis_thaliana/", gtf_url)
        self.assertRegex(gtf_url, r"Arabidopsis_thaliana\.TAIR10\.\d+\.gtf\.gz")

    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_species_info")
    @patch("Classes.API.ensembl_mod.EnsemblUtils.get_id_taxon")
    def test_latest_human_gtf_url(self, mock_get_taxon, mock_get_species_info):
        mock_get_species_info.return_value = {
            "name": "Homo sapiens",
            "url_name": "homo_sapiens",
            "assembly_default": "GRCh38",
            "division": "Ensembl"
        }
        mock_get_taxon.return_value = "9606"

        le = LocalEnsembl(
            raw_species="homo_sapiens",
            goal_directory="/tmp",
            release=-1,
            metadata_mode="auto"
        )

        gtf_url = le.ftp_address

        self.assertIn("ensembl.org/pub/current_gtf/homo_sapiens/", gtf_url)
        self.assertRegex(gtf_url, r"Homo_sapiens\.GRCh38\.\d+\.gtf\.gz$")





if __name__ == "__main__":
    unittest.main()
