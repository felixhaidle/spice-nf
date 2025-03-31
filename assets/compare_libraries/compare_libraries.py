# Copyright (C) 2025 Felix Haidle
# This file is part of spice_library_pipeline and is licensed under
# the GNU General Public License v3.0. See the LICENSE file or
# https://www.gnu.org/licenses/gpl-3.0.en.html for details.

import argparse
import os
import sys
import json
import difflib

def parse_arguments():
    """Parses command-line arguments for the script."""
    parser = argparse.ArgumentParser(
        description="Compare SPICE libraries in two directories and identify mismatches."
    )

    parser.add_argument("--library1", type=str, required=True, help="Path to the first SPICE library directory")
    parser.add_argument("--library2", type=str, required=True, help="Path to the second SPICE library directory")

    args = parser.parse_args()
    library1 = args.library1
    library2 = args.library2

    # Check if directories exist
    if not os.path.isdir(args.library1):
        log_output(f"Error: The directory '{args.library1}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(args.library2):
        log_output(f"Error: The directory '{args.library2}' does not exist.")
        sys.exit(1)

    return args.library1, args.library2

def compare_directory_structure(dir1, dir2):
    """Compares the file and folder structure of two directories and log_outputs mismatches."""

    # Get relative file paths from both directories
    dir1_files = set(os.path.relpath(os.path.join(root, file), dir1)
                     for root, _, files in os.walk(dir1) for file in files)
    dir2_files = set(os.path.relpath(os.path.join(root, file), dir2)
                     for root, _, files in os.walk(dir2) for file in files)

    # Compare structures
    missing_in_dir2 = dir1_files - dir2_files
    missing_in_dir1 = dir2_files - dir1_files

    # log_output results
    if not missing_in_dir1 and not missing_in_dir2:
        log_output("✅ Directory structures match.")
    else:
        log_output("❌ Mismatched structure detected!")

        if missing_in_dir2:
            log_output(f"\n📌 Files present in {dir1} but missing in {dir2}")
            for file in sorted(missing_in_dir2):
                log_output(f"   - {file}")


        if missing_in_dir1:
            log_output(f"\n📌 Files present in {dir2} but missing in {dir1}")
            for file in sorted(missing_in_dir1):
                log_output(f"   - {file}")


def compare_annotations_entries(library1, library2):
    """
    For each top-level key in annotations.json (which are assumed to exist in both files),
    report which sub-entries in library1 are missing in library2.
    """
    file1 = os.path.join(library1, "fas_data", "annotations.json")
    file2 = os.path.join(library2, "fas_data", "annotations.json")

    # Ensure both files exist
    if not os.path.isfile(file1) or not os.path.isfile(file2):
        log_output("⚠️ annotations.json is missing in one or both libraries.")
        return

    # Load JSON data
    with open(file1, "r", encoding="utf-8") as f:
        data1 = json.load(f)
    with open(file2, "r", encoding="utf-8") as f:
        data2 = json.load(f)

    log_output("🔍 Comparing sub-entries for each top-level key:")

    # Iterate over each top-level key
    for top_key in data1:
        # If for some reason the top-level key is missing in lib2, report it
        if top_key not in data2:
            log_output(f"🚨 Top-level key '{top_key}' is missing in library2!")
            continue

        # We only compare if both values are dictionaries
        if isinstance(data1[top_key], dict) and isinstance(data2[top_key], dict):
            entries1 = set(data1[top_key].keys())
            entries2 = set(data2[top_key].keys())
            missing_entries = entries1 - entries2

            if missing_entries:
                log_output(f"\n🚨 Under '{top_key}', the following entries are present in library1 but missing in library2:")
                for entry in sorted(missing_entries):
                    log_output(f"   - {entry}")
            else:
                log_output(f"\n✅ All entries under '{top_key}' in library1 are present in library2.")
        else:
            # For non-dictionary values, you might simply note if they match or not.
            if data1[top_key] != data2[top_key]:
                log_output(f"\n🚨 Mismatch in '{top_key}': library1 has {data1[top_key]}, library2 has {data2[top_key]}.")
            else:
                log_output(f"\n✅ '{top_key}' matches in both libraries.")




def load_fas_scores(directory):
    """Aggregates all FAS scores from JSON files in the fas_scores folder into a single dictionary."""
    fas_scores = {}

    folder_path = os.path.join(directory, "fas_data", "fas_scores")

    if not os.path.isdir(folder_path):
        log_output(f"⚠️ fas_scores directory is missing in {directory}.")
        return fas_scores

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if file.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for gene, transcripts in data.items():
                    if gene not in fas_scores:
                        fas_scores[gene] = {}
                    for transcript, partners in transcripts.items():
                        if transcript not in fas_scores[gene]:
                            fas_scores[gene][transcript] = {}
                        fas_scores[gene][transcript].update(partners)  # Merge transcript data

    return fas_scores

def compare_fas_scores(library1, library2):
    """Compares aggregated FAS scores between two libraries."""

    # Load and aggregate JSON contents
    fas_data1 = load_fas_scores(library1)
    fas_data2 = load_fas_scores(library2)

    # Step 1: Check for missing genes
    missing_genes = set(fas_data1.keys()) - set(fas_data2.keys())
    if missing_genes:
        log_output("\n❌ Missing genes in Library2:")
        for gene in sorted(missing_genes):
            log_output(f"   - {gene}")

    # Step 2: Compare transcript pairings and FAS scores
    for gene, transcripts in fas_data1.items():
        if gene in fas_data2:  # Only compare if gene exists in both
            for transcript, partners in transcripts.items():
                if transcript not in fas_data2[gene]:
                    log_output(f"\n❌ Transcript {transcript} missing in gene {gene} (Library2)")
                else:
                    for partner, fas_score in partners.items():
                        if partner not in fas_data2[gene][transcript]:
                            log_output(f"\n❌ Partner {partner} missing in {gene} -> {transcript} (Library2)")
                        elif fas_data2[gene][transcript][partner] != fas_score:
                            log_output(f"\n🔄 Mismatch in FAS score for {gene} -> {transcript} -> {partner}")
                            log_output(f"   - Expected: {fas_score}, Found: {fas_data2[gene][transcript][partner]}")




def compare_annotools(library1, library2):
    """Compares annotools.txt files in the fas_data folder of both libraries."""

    file1 = os.path.join(library1, "fas_data", "annoTools.txt")
    file2 = os.path.join(library2, "fas_data", "annoTools.txt")

    # Ensure both files exist
    if not os.path.isfile(file1) or not os.path.isfile(file2):
        log_output("⚠️ annotools.txt is missing in one or both libraries.")
        return

    # Read file contents
    with open(file1, "r", encoding="utf-8") as f1:
        content1 = f1.readlines()

    with open(file2, "r", encoding="utf-8") as f2:
        content2 = f2.readlines()

    # Check if files are identical
    if content1 == content2:
        log_output("✅ annotools.txt files are identical.")
        return

    # Find differences
    log_output("❌ annotools.txt files differ. Showing first differences:\n")

    diff = list(difflib.unified_diff(content1, content2, fromfile="Library1", tofile="Library2", lineterm=""))

    # log_output first few differences
    for line in diff[:20]:  # Limit output to first 20 lines of difference
        log_output(str(line))


def compare_important_features(library1, library2):
    """Compares important_features.json between two libraries."""

    file1 = os.path.join(library1, "fas_data", "important_features.json")
    file2 = os.path.join(library2, "fas_data", "important_features.json")

    # Ensure both files exist
    if not os.path.isfile(file1) or not os.path.isfile(file2):
        log_output("⚠️ important_features.json is missing in one or both libraries.")
        return

    # Load JSON data
    with open(file1, "r", encoding="utf-8") as f:
        data1 = json.load(f)

    with open(file2, "r", encoding="utf-8") as f:
        data2 = json.load(f)

    # Step 1: Identify missing keys
    missing_keys = set(data1.keys()) - set(data2.keys())
    if missing_keys:
        log_output("\n❌ Missing keys in Library2:")
        for key in sorted(missing_keys):
            log_output(f"   - {key}")

    # Step 2: Check for missing values within keys
    for key, values1 in data1.items():
        if key in data2:
            values2 = set(data2[key])  # Convert list to set for easy comparison
            missing_values = set(values1) - values2  # Values in Library1 but missing in Library2

            if missing_values:
                log_output(f"\n🔄 Missing values for key '{key}' in Library2:")
                for value in sorted(missing_values):
                    log_output(f"   - {value}")




if __name__ == "__main__":


    # Define output report file
    report_file = "comparison_report.txt"

    # Redirect all log_outputs to both console and file
    with open(report_file, "w", encoding="utf-8") as report:

        def log_output(message):
            """Logs output to both console and report file."""
            print(message)  # log_output to console
            report.write(message + "\n")  # Write to file
                # Parse directories from command-line arguments
        library1, library2 = parse_arguments()


        # log_output confirmation
        log_output("=" * 60)
        log_output(f"🔍 Comparing SPICE Libraries:")
        log_output(f"📂 Library 1: {library1}")
        log_output(f"📂 Library 2: {library2}")
        log_output("=" * 60 + "\n")

        # Compare directory structure
        log_output("📁 [1] Checking Directory Structure...\n" + "-" * 60)
        compare_directory_structure(library1, library2)

        # Compare annotations.json
        log_output("\n📝 [2] Comparing Annotations (annotations.json)...\n" + "-" * 60)
        compare_annotations_entries(library1, library2)

        # Compare FAS scores
        log_output("\n📊 [3] Comparing FAS Scores (fas_scores/*.json)...\n" + "-" * 60)
        compare_fas_scores(library1, library2)

        # Compare annotools.txt
        log_output("\n📄 [4] Comparing Annotation Tools (annotools.txt)...\n" + "-" * 60)
        compare_annotools(library1, library2)

        # Compare important_features.json
        log_output("\n🔬 [5] Comparing Important Features (important_features.json)...\n" + "-" * 60)
        compare_important_features(library1, library2)

        log_output("\n✅ Comparison Completed. See 'comparison_report.txt' for details.")



