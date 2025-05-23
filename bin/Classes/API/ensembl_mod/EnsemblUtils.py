#!/bin/env python

#######################################################################
# Copyright (C) 2023 Christian Bluemel
#
# This file is part of Spice.
#
#  ensemblUtils is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ensemblUtils is distributed in the hope that it will be useful,
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

import requests
import sys
import re



from typing import Dict, List, Tuple
from typing import Any

from requests import Response

from urllib import request
from urllib.error import URLError, HTTPError



def chunks(lst: List[str], n: int) -> List[List[str]]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def make_request_data(id_list: List[str]) -> str:
    request_data: str = '{ "ids" : ['
    for entry in id_list:
        request_data += '"' + entry + '", '
    request_data = request_data[:-2]
    request_data += ' ] }'
    return request_data


def ping_ensembl() -> bool:
    """

    :rtype: object
    """
    r: Response = requests.get("https://rest.ensembl.org/info/ping?", headers={"Content-Type": "application/json"})
    if not r.ok:
        print("Ensembl is currently down. Can't download sequences. Aborting...")
        r.raise_for_status()
        sys.exit()
    decoded: Dict[str, Any] = r.json()
    return bool(decoded["ping"])


def make_local_ensembl_name(path, release_num, suffix, assembly_name, url_species) -> str:
    release_num: str = str(release_num)
    ensembl_path: str = path + url_species + "." + assembly_name + "." + release_num + suffix
    return ensembl_path


def get_current_release() -> str:
    r = requests.get("https://rest.ensembl.org/info/data/?", headers={"Content-Type": "application/json"})
    if not r.ok:
        print("Could not get current release number...")
        r.raise_for_status()
        sys.exit()
    else:
        release_num: str = max(r.json()["releases"])
    return str(release_num)


def get_id_taxon(species: str) -> str:
    r = requests.get("https://rest.ensembl.org/info/genomes/taxonomy/" + species + "?",
                     headers={"Content-Type": "application/json"})

    if not r.ok:
        r.raise_for_status()
        sys.exit()

    decoded: List[Dict[str, Any]] = r.json()
    return decoded[0]["species_taxonomy_id"]

def get_species_info(raw_species: str) -> dict:
    r = requests.get(f"https://rest.ensembl.org/info/genomes/{raw_species}?",
                     headers={"Content-Type": "application/json"})
    if not r.ok:
        raise Exception("Species could not be found.")

    decoded = r.json()
    return {
        "name": decoded["name"],
        "url_name": decoded["url_name"],
        "assembly_default": decoded["assembly_default"],
        "division": decoded["division"]
    }

def resolve_ensembl_current_filename(
    base_url: str,
    file_type: str = "gtf",
    url_species_name: str = "",
    assembly_name: str = ""
) -> Tuple[str, str]:
    """
    Retrieve the latest valid filename from an Ensembl 'current' FTP folder, and extract its release version.
    """
    try:
        req = request.Request(base_url, headers={"User-Agent": "Mozilla/5.0"})
        with request.urlopen(req) as response:
            html = response.read().decode("utf-8")

            if file_type == "gtf":
                pattern = re.compile(r'href="([^"]+\.gtf\.gz)"')
                matches = [
                    m for m in pattern.findall(html)
                    if m.startswith(f"{url_species_name}.{assembly_name}")
                    and not any(x in m for x in ["abinitio", "chr"])
                ]
            elif file_type == "pep":
                pattern = re.compile(r'href="([^"]+\.pep\.all\.fa\.gz)"')
                matches = [
                    m for m in pattern.findall(html)
                    if m.startswith(f"{url_species_name}.{assembly_name}")
                    and "abinitio" not in m
                ]
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            if not matches:
                raise Exception(f"No .{file_type} files found at {base_url}")

            # Sort to prefer latest numeric release
            def extract_release(filename: str) -> int:
                match = re.search(r'\.(\d+)\.', filename)
                return int(match.group(1)) if match else 0

            matches.sort(key=extract_release, reverse=True)
            filename = matches[0]

            release_match = re.search(r'\.(\d+)\.', filename)
            release = release_match.group(1) if release_match else "unknown"

            return filename, release

    except (HTTPError, URLError) as e:
        raise Exception(f"Could not resolve latest file from {base_url}: {e}")





def main():
    print(ping_ensembl())


if __name__ == "__main__":
    main()
