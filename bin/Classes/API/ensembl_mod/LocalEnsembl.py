#!/bin/env python

#######################################################################
# Copyright (C) 2023 Christian Bluemel
#
# This file is part of Spice.
#
#  LocalEnsembl is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  LocalEnsembl is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Spice.  If not, see <http://www.gnu.org/licenses/>.
#
# Modifications:
#   - Adapted by Felix Haidle in 2025 for integration into spice_library_pipeline.
#######################################################################


import gzip
import os
import shutil
from contextlib import closing
from urllib import request

from Classes.API.ensembl_mod.EnsemblUtils import (
    ping_ensembl,
    get_id_taxon,
    get_species_info,
    resolve_ensembl_current_filename
)

class LocalEnsembl:
    def __init__(
        self,
        raw_species: str,
        goal_directory: str,
        release: str = None,
        division: str = "Ensembl",
        metadata_mode: str = "auto",  # or "placeholder"
    ) -> None:
        self.goal_directory = goal_directory
        self.raw_species_name = raw_species
        self.division = division
        self.release = release
        self.metadata_mode = metadata_mode

        # Metadata population
        if self.metadata_mode == "auto":
            metadata = get_species_info(raw_species)  # Adjust this to return a dict or tuple with division
            if isinstance(metadata, dict):
                self.species_name = metadata["name"]
                self.url_species_name = metadata["url_name"]
                self.assembly_default_species_name = metadata["assembly_default"]
                self.division = metadata.get("division", division)  # fallback to passed division if needed
            else:
                self.species_name, self.url_species_name, self.assembly_default_species_name = metadata
                self.division = division  # fallback if no division in tuple response

            self.taxon_id = get_id_taxon(self.species_name)
        elif self.metadata_mode == "placeholder":
            self.species_name = "custom_species"
            self.url_species_name = "custom_species"
            self.assembly_default_species_name = "custom_assembly"
            self.division = division or "Ensembl"
            self.taxon_id = "999999"
            # ⛔ Skip FTP setup
            self.ftp_address = None
            self.ftp_pep_address = None
            self.local_zipname = ""
            self.local_pep_zipname = ""
            self.local_filename = ""
            self.local_pep_filename = ""

            return
        else:
            raise ValueError(f"Invalid metadata_mode: {metadata_mode}")

        # Filename templates
        self.local_zipname = f"{self.url_species_name}.{self.assembly_default_species_name}.{self.release or 'latest'}.gtf.gz"
        self.local_pep_zipname = f"{self.url_species_name}.{self.assembly_default_species_name}.pep.all.fa.gz"
        self.local_filename = self.local_zipname[:-3]
        self.local_pep_filename = self.local_pep_zipname[:-3]

        # FTP logic
        self.ftp_address = self.build_ftp_url(file_type="gtf")
        self.ftp_pep_address = self.build_ftp_url(file_type="pep")

    def build_ftp_url(self, file_type: str) -> str:
        ftp_base = {
            "Ensembl": "https://ftp.ensembl.org/pub/",
            "EnsemblVertebrates": "https://ftp.ensembl.org/pub/",
            "EnsemblPlants": "http://ftp.ensemblgenomes.org/pub/plants/",
            "EnsemblFungi": "http://ftp.ensemblgenomes.org/pub/fungi/",
            "EnsemblMetazoa": "http://ftp.ensemblgenomes.org/pub/metazoa/",
        }

        if self.division not in ftp_base:
            raise ValueError(f"Unsupported division: {self.division}")

        base = ftp_base[self.division]
        file_name_species = self.url_species_name.lower()

        if self.release:
            release_folder = f"release-{self.release}"
            release_number = self.release
        else:
            release_folder = "current" if self.division != "Ensembl" else f"current_{file_type}"
            if file_type == "gtf":
                folder_url = f"{base}{release_folder}/gtf/{file_name_species}/"
            elif file_type == "pep":
                folder_url = f"{base}{release_folder}/fasta/{file_name_species}/pep/"
            else:
                raise ValueError("Invalid file_type (must be 'gtf' or 'pep')")

            resolved_filename, resolved_release = resolve_ensembl_current_filename(folder_url, file_type)
            self._resolved_release = resolved_release
            return f"{folder_url}{resolved_filename}"

        # Construct URLs for explicit release
        if file_type == "gtf":
            return f"{base}{release_folder}/gtf/{file_name_species}/{self.url_species_name}.{self.assembly_default_species_name}.{release_number}.gtf.gz"
        elif file_type == "pep":
            return f"{base}{release_folder}/fasta/{file_name_species}/pep/{self.url_species_name}.{self.assembly_default_species_name}.pep.all.fa.gz"
        else:
            raise ValueError("Invalid file_type (must be 'gtf' or 'pep')")




        def get_species_name(self) -> str:
            return self.species_name

        def get_taxon_id(self) -> str:
            return self.taxon_id

        def download(self, test_url=None) -> str:
            if not self.is_downloaded():
                download_url = test_url or self.ftp_address
                print(f"\tDownloading {download_url}")
                with closing(request.urlopen(download_url)) as r:
                    with open(os.path.join(self.goal_directory, self.local_zipname), 'wb') as f:
                        shutil.copyfileobj(r, f)

                with gzip.open(os.path.join(self.goal_directory, self.local_zipname), 'rb') as f_in:
                    with open(os.path.join(self.goal_directory, self.local_filename), "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)

                os.remove(os.path.join(self.goal_directory, self.local_zipname))
            else:
                print(f"GTF already downloaded: {self.local_filename}")
            return os.path.join(self.goal_directory, self.local_filename)

    def download_pep(self, test_url=None) -> str:
        if not self.is_pep_downloaded():
            download_url = test_url or self.ftp_pep_address
            print(f"\tDownloading {download_url}")
            with closing(request.urlopen(download_url)) as r:
                with open(os.path.join(self.goal_directory, self.local_pep_zipname), 'wb') as f:
                    shutil.copyfileobj(r, f)

            with gzip.open(os.path.join(self.goal_directory, self.local_pep_zipname), 'rb') as f_in:
                with open(os.path.join(self.goal_directory, self.local_pep_filename), "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            os.remove(os.path.join(self.goal_directory, self.local_pep_zipname))
        else:
            print(f"PEP already downloaded: {self.local_pep_filename}")
        return os.path.join(self.goal_directory, self.local_pep_filename)

    def is_downloaded(self) -> bool:
        return os.path.isfile(os.path.join(self.goal_directory, self.local_filename))

    def is_pep_downloaded(self) -> bool:
        return os.path.isfile(os.path.join(self.goal_directory, self.local_pep_filename))

    @property
    def ping(self) -> bool:
        return ping_ensembl()

    def get_release_num(self) -> str:
        return self.release or "latest"

    def remove(self) -> None:
        if self.is_downloaded():
            os.remove(os.path.join(self.goal_directory, self.local_filename))

    def remove_pep(self) -> None:
        if self.is_pep_downloaded():
            os.remove(os.path.join(self.goal_directory, self.local_pep_filename))
