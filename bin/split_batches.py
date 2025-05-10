#!/bin/env python3

import os
import argparse

def extract_gene_id(protein_id):
    """
    Extract the gene ID from a full protein ID.
    Example input: ENSG00000100241|ENSP00000509462|9606
    Returns: ENSG00000100241
    """
    return protein_id.split("|")[0]

def process_domains_low_memory(input_file, output_base, direction):
    """
    Process a .domains file (forward or reverse) line-by-line.
    Immediately write lines to the correct per-gene output file,
    ensuring each file has the header once.
    """
    output_handles = {}

    with open(input_file, "r") as f:
        header = next(f)  # Read and store the header line

        for line in f:
            if not line.strip():
                continue  # Skip empty lines

            pair_id = line.split("\t")[0]  # The pairID field
            prot1, prot2 = pair_id.split("#")  # Separate the two protein IDs
            gene1 = extract_gene_id(prot1)
            gene2 = extract_gene_id(prot2)

            # Write the line to both gene1 and gene2 output files
            for gene in (gene1, gene2):
                gene_dir = os.path.join(output_base, gene)
                os.makedirs(gene_dir, exist_ok=True)

                output_path = os.path.join(gene_dir, f"{gene}_{direction}.domains")

                if gene not in output_handles:
                    # First time seeing this gene: open file and write header
                    out_f = open(output_path, "w")
                    out_f.write(header)
                    output_handles[gene] = out_f

                # Write the current line into the gene's file
                output_handles[gene].write(line)

    # Close all open files
    for out_f in output_handles.values():
        out_f.close()

def process_phyloprofile_low_memory(input_file, output_base):
    """
    Process a .phyloprofile file line-by-line.
    Immediately write lines to the correct per-gene output file,
    ensuring each file has the header once.
    """
    output_handles = {}

    with open(input_file, "r") as f:
        header = next(f)  # Read and store the header line

        for line in f:
            if not line.strip():
                continue  # Skip empty lines

            parts = line.strip().split("\t")
            gene_id = extract_gene_id(parts[0])

            gene_dir = os.path.join(output_base, gene_id)
            os.makedirs(gene_dir, exist_ok=True)

            output_path = os.path.join(gene_dir, f"{gene_id}.phyloprofile")

            if gene_id not in output_handles:
                # First time seeing this gene: open file and write header
                out_f = open(output_path, "w")
                out_f.write(header)
                output_handles[gene_id] = out_f

            # Write the current line into the gene's file
            output_handles[gene_id].write(line + "\n")

    # Close all open files
    for out_f in output_handles.values():
        out_f.close()

def main(batch_dir, output_base):
    """
    Main function to split merged batch outputs into per-gene files.
    Processes forward.domains, reverse.domains, and phyloprofile.
    """
    forward_file = os.path.join(batch_dir, "merged_forward.domains")
    reverse_file = os.path.join(batch_dir, "merged_reverse.domains")
    phyloprofile_file = os.path.join(batch_dir, "merged.phyloprofile")

    all_genes = set()

    # Collect gene IDs from all files
    for file in [forward_file, reverse_file, phyloprofile_file]:
        with open(file) as f:
            next(f)  # skip header
            for line in f:
                if not line.strip():
                    continue
                if "phyloprofile" in file:
                    gene = extract_gene_id(line.split("\t")[0])
                    all_genes.add(gene)
                else:
                    prot1, prot2 = line.split("\t")[0].split("#")
                    all_genes.update([extract_gene_id(prot1), extract_gene_id(prot2)])

    # Process actual data
    process_domains_low_memory(forward_file, output_base, direction="forward")
    process_domains_low_memory(reverse_file, output_base, direction="reverse")
    process_phyloprofile_low_memory(phyloprofile_file, output_base)

    # Ensure forward/reverse files exist for all genes
    with open(forward_file) as f:
        forward_header = next(f)
    with open(reverse_file) as f:
        reverse_header = next(f)

    for gene in all_genes:
        for direction, header in [("forward", forward_header), ("reverse", reverse_header)]:
            gene_dir = os.path.join(output_base, gene)
            os.makedirs(gene_dir, exist_ok=True)
            file_path = os.path.join(gene_dir, f"{gene}_{direction}.domains")
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    f.write(header)


if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Split FAS batch output into per-gene files (memory-efficient).")
    parser.add_argument("--batch_dir", required=True, help="Directory containing merged partition batch files")
    parser.add_argument("--output_base", default="merged_output", help="Directory to save per-gene outputs")

    args = parser.parse_args()
    main(args.batch_dir, args.output_base)
