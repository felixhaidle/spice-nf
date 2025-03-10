#!/usr/bin/env python3

import sys

def parse_gtf(gtf_file, gene_id):
    gene_size = 0
    transcript_count = 0
    found_gene = False
    gene_start, gene_end = None, None

    with open(gtf_file, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue  # Skip comments

            columns = line.strip().split("\t")
            if len(columns) < 9:
                continue  # Skip malformed lines

            feature_type = columns[2]
            start, end = int(columns[3]), int(columns[4])
            attributes = columns[8]

            # Check if this line belongs to the target gene
            if f'gene_id "{gene_id}";' in attributes:
                found_gene = True
                if feature_type == "gene":
                    gene_start, gene_end = start, end
                elif feature_type == "transcript":
                    transcript_count += 1

    # Compute gene size if gene_start and gene_end were found
    if gene_start is not None and gene_end is not None:
        gene_size = gene_end - gene_start

    # If the gene wasn't found, return 0s to avoid errors
    if not found_gene:
        gene_size = 0
        transcript_count = 0

    # Assign resources based only on transcript count
    if transcript_count < 3:
        requirements = "small"
    elif transcript_count < 20:
        requirements = "medium"
    else:
        requirements = "large"

    # Print output using tab delimiter
    print(f"{gene_id}\t{gene_size}\t{transcript_count}\t{requirements}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: extract_gene_info.py <GTF_FILE> <GENE_ID>")
        sys.exit(1)

    gtf_file = sys.argv[1]
    gene_id = sys.argv[2]
    parse_gtf(gtf_file, gene_id)
