#!/usr/bin/env python3
import argparse
from collections import defaultdict

def main(genes_file, complexity_file, output_file):
    """
    Reads a list of gene IDs and a complexity file with transcript-level #Paths,
    calculates a weighted score for each gene based on the number of transcripts,
    and writes the gene list sorted by descending score.

    Scoring formula:
        For each gene:
            Let T = number of transcripts for the gene (T > 1 required to score)
            For each transcript i:
                paths_i = #Paths for that transcript
            Score = sum(paths_i × T for all transcripts i)

    Rules:
        - Genes with only 1 transcript are not scored.
        - Genes not present in the complexity file are not scored.
        - All unscored genes appear at the end in the order from genes.txt.

    Args:
        genes_file (str): Path to file containing gene IDs (one per line).
        complexity_file (str): Path to file with transcript complexity info.
        output_file (str): Path to write the sorted gene list.
    """

    # ---------------------------
    # Step 1: Load gene list
    # ---------------------------
    with open(genes_file) as f:
        gene_list = [line.strip() for line in f if line.strip()]

    # ---------------------------
    # Step 2: Parse complexity file
    # ---------------------------
    gene_to_transcripts = defaultdict(list)

    with open(complexity_file) as f:
        header = f.readline()  # Skip header
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue  # Skip malformed lines

            protein_id = parts[0]
            try:
                paths = int(parts[1])
            except ValueError:
                continue  # Skip non-integer path values

            gene_id = protein_id.split('|')[0]
            gene_to_transcripts[gene_id].append(paths)

    # ---------------------------
    # Step 3: Compute score per gene (only if >1 transcript)
    # ---------------------------
    gene_scores = {}

    for gene_id, path_list in gene_to_transcripts.items():
        transcript_count = len(path_list)
        if transcript_count <= 1:
            continue  # Skip genes with only one transcript

        score = sum(paths * transcript_count for paths in path_list)
        gene_scores[gene_id] = score

    # ---------------------------
    # Step 4: Sort and separate genes
    # ---------------------------
    scored_genes = [g for g in gene_list if g in gene_scores]
    unscored_genes = [g for g in gene_list if g not in gene_scores]

    sorted_genes = sorted(scored_genes, key=lambda g: gene_scores[g], reverse=True)
    final_order = sorted_genes + unscored_genes

    # ---------------------------
    # Step 5: Write output
    # ---------------------------
    with open(output_file, "w") as f:
        for gene in final_order:
            f.write(gene + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sort genes by transcript-weighted path complexity."
    )

    parser.add_argument("--genes_txt", required=True, help="Path to input genes.txt file")
    parser.add_argument("--complexity_txt", required=True, help="Path to input complexity.txt file")
    parser.add_argument("--output_txt", required=True, help="Path to write sorted gene list")

    args = parser.parse_args()

    main(args.genes_txt, args.complexity_txt, args.output_txt)
