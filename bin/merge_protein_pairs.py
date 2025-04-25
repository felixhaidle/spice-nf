#!/bin/env python
import os
import glob
import argparse

def merge_files(file_type, pattern, output_file):
    """
    Merge multiple files of the same type into a single output file.
    Assumes each input file has a header; only the first file's header is written.
    """
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"No files found for type: {file_type}")
        return

    print(f"Merging {len(files)} '{file_type}' files into: {output_file}")

    with open(output_file, "w") as out_f:
        header_written = False
        for path in files:
            with open(path) as in_f:
                lines = in_f.readlines()
                if not lines:
                    continue
                if not header_written:
                    # Write header from the first file
                    out_f.write(lines[0])
                    header_written = True
                # Skip header line for all but the first file
                out_f.writelines(lines[1:])

    print(f"Finished merging '{file_type}' into {output_file}\n")

def main(gene_id, output_base):
    """
    Prepare output directory and define file types to merge based on the gene_id.
    Skip processing if no matching files are found.
    """
    output_dir = os.path.join(output_base, gene_id)

    # Define the file types to merge (excluding .tsv)
    targets = {
        "forward.domains": {
            "pattern": f"./{gene_id}_*_forward.domains",
            "outfile": os.path.join(output_dir, f"{gene_id}_forward.domains"),
        },
        "reverse.domains": {
            "pattern": f"./{gene_id}_*_reverse.domains",
            "outfile": os.path.join(output_dir, f"{gene_id}_reverse.domains"),
        },
        "phyloprofile": {
            "pattern": f"./{gene_id}_*.phyloprofile",
            "outfile": os.path.join(output_dir, f"{gene_id}.phyloprofile"),
        }
    }

    # Check if any files exist for this gene across all patterns
    found_any = any(glob.glob(conf["pattern"]) for conf in targets.values())

    if not found_any:
        print(f"No matching files found for gene {gene_id}. Skipping.\n")
        return

    # Create output directory if matches are found
    os.makedirs(output_dir, exist_ok=True)

    # Merge files by type
    for key, conf in targets.items():
        merge_files(key, conf["pattern"], conf["outfile"])


if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Merge gene-related files from multiple parallel runs.")
    parser.add_argument("--gene_id", required=True, help="Gene ID to process (e.g., ENSG00000100281)")
    parser.add_argument("--output_base", default="merged_output", help="Base directory where merged results are stored")

    args = parser.parse_args()
    main(args.gene_id, args.output_base)
