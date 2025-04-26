#!/bin/env python3

import os
import argparse
import json
import shutil

def load_path_counts(path_count_file):
    """Load protein path counts from a TSV file"""
    path_counts = {}
    with open(path_count_file, "r") as f:
        next(f)
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                try:
                    path_counts[parts[0]] = int(parts[1])
                except ValueError:
                    continue
    return path_counts


def unpack_genes(pairings_json_path, out_dir):
    """Unpack all genes into individual TSV files"""
    os.makedirs(out_dir, exist_ok=True)

    with open(pairings_json_path, "r") as f:
        json_data = json.load(f)

    skip_keys = {"feature", "interproID", "clan", "count", "length", "version"}
    gene_files = []

    for gene_id, data in json_data.items():
        if gene_id in skip_keys or not isinstance(data, str):
            continue

        gene_path = os.path.join(out_dir, f"{gene_id}.tsv")
        with open(gene_path, "w") as f_out:
            f_out.write(data)
        gene_files.append(gene_path)

    return gene_files


def split_gene_files(gene_files):
    """Split each gene .tsv file into individual pairing files (geneID_lineNum.tsv)"""
    all_pair_files = []

    for file_path in gene_files:
        gene_id = os.path.basename(file_path).replace(".tsv", "")
        with open(file_path, "r") as f:
            for i, line in enumerate(f):
                if not line.strip():
                    continue
                pair_file = f"{gene_id}_{i}.tsv"
                with open(pair_file, "w") as out_f:
                    out_f.write(line)
                all_pair_files.append(pair_file)

    return all_pair_files


def score_pairs(pair_files, path_counts):
    """Calculate score for each protein pair file"""
    pair_scores = []

    for f in pair_files:
        with open(f, "r") as pf:
            line = pf.readline().strip()
            try:
                p1, p2 = line.split("\t")
                score = path_counts.get(p1, 0) + path_counts.get(p2, 0)
                pair_scores.append((f, score))
            except ValueError:
                continue

    return pair_scores


def lpt_partition(pair_scores, num_bins):
    """Greedy LPT-style partitioning"""
    sorted_pairs = sorted(pair_scores, key=lambda x: x[1], reverse=True)
    bins = [[] for _ in range(num_bins)]
    totals = [0] * num_bins

    for file_name, score in sorted_pairs:
        min_bin = totals.index(min(totals))
        bins[min_bin].append(file_name)
        totals[min_bin] += score

    return bins


def merge_files_into_partitions(partitions):
    """Merge .tsv files into partition_X/partition_X.tsv (one entry per line)."""
    for i, bin_files in enumerate(partitions):
        part_dir = f"partition_{i}"
        os.makedirs(part_dir, exist_ok=True)

        merged_path = os.path.join(part_dir, f"partition_{i}.tsv")
        with open(merged_path, "w") as merged_file:
            for f in bin_files:
                with open(f, "r") as infile:
                    for line in infile:
                        line = line.rstrip('\n')  # remove any accidental multiple newlines
                        merged_file.write(line + "\n")  # re-add exactly one newline





def main():
    parser = argparse.ArgumentParser(description="Partition FAS protein pairings based on LPT scoring")
    parser.add_argument("--pairings_json", required=True, help="JSON file with all gene pairings")
    parser.add_argument("--paths_file", required=True, help="Protein path complexity file")
    parser.add_argument("--tmp_dir", default="unpacked_genes", help="Temporary dir for unpacked gene .tsv files")
    parser.add_argument("--partitions", type=int, default=8, help="Number of CPU partitions")

    args = parser.parse_args()

    if args.partitions < 1:
        split_partitions_number = 1
    else:
        split_partitions_number = args.partitions

    # Load protein complexity scores
    path_counts = load_path_counts(args.paths_file)
    print(f"Loaded {len(path_counts)} protein path scores")

    # Step 1–2: Unpack genes and split to protein pair .tsv files
    gene_files = unpack_genes(args.pairings_json, args.tmp_dir)
    print(f"Unpacked {len(gene_files)} genes")

    pair_files = split_gene_files(gene_files)
    print(f"Split into {len(pair_files)} individual pairing files")

    # Adjust partition number if too many partitions requested
    total_pairs = len(pair_files)
    if split_partitions_number > total_pairs:
        print(f"Warning: Requested {split_partitions_number} partitions, but only {total_pairs} pairs available.")
        split_partitions_number = total_pairs
        print(f"Adjusting to {split_partitions_number} partitions.")


    # Step 3–4: Score each pair using protein path counts
    scored_pairs = score_pairs(pair_files, path_counts)
    print(f"Scored {len(scored_pairs)} pairing files")

    # Step 5: Partition using LPT
    partitions = lpt_partition(scored_pairs, split_partitions_number)
    print(f"Partitioned into {split_partitions_number} bins")

    # Step 6: Move files to bin directories
    merge_files_into_partitions(partitions)
    print("Files organized into partition folders")


if __name__ == "__main__":
    main()

