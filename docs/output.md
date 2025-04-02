# BIONF/spice_library_pipeline: Output

## Introduction

This document describes the output produced by the pipeline.

The directories listed below will be created in the results directory after the pipeline has finished. All paths are relative to the top-level results directory.

## Pipeline Outputs

Here I describe the outputs based on an example found in `assets/test_files/example_run_result`.

### The SPICE Library

The reason why this pipeline exists: the SPICE library.

The name of a SPICE library consists of four parts:

- `spice_lib_`
  _Short for SPICE library_
- Organism name
- Ensembl version number
- Hexadecimal identifier indicating which annotation tools were used for FAS scoring.

The folder `spice_lib_human_113_3ee` from the example therefore contains a SPICE library for the human transcriptome, based on Ensembl release 113, using the annotation tools described by the identifier.

The FAS hex code identifiers are explained [here](FAS_hex_identifier.md)

The library is structured as follows:

```bash
spice_lib_human_113_3ee/
├── info.yaml
├── paths.json
├── fas_data/
└── transcript_data/
```

**info.yaml**
Structured summary of the library build process. Includes input arguments, version info, run status, and counts of collected sequences, genes, proteins, and transcripts. Useful for tracking pipeline configuration and verifying successful completion of each step.

**paths.json**
JSON index that maps all important files and folders created by the pipeline. It allows downstream tools to easily locate relevant contents.

> [!WARNING]
> If you move the library to a different directory (for example a central storage), you may need to update the "root" entry to the new location.

#### **fas_data/**

```bash
fas_data/
├── annotation/
├── annotations.json
├── annoTools.txt
├── architectures/
├── fas_index.json
├── fas.phyloprofile
├── fas_scores/
├── forward.domains
├── reverse.domains
└── important_features.json
```

**annotation/**
Currently empty. May be used for downstream purposes.

**annotations.json**
Output of `fas.doAnno`. Contains domain and feature annotations for all collected FAS sequences. Each entry is keyed by gene, protein, and species ID and includes domain positions, E-values, and tool-specific metadata. Also contains a record of the annotation tool versions used.

**annoTools.txt**
The configuration file used by `fas.doAnno` to determine which annotation tools to apply.

**architectures/**
Contains an index file indicating which of the numbered files a gene appears in. The numbered files contain information about domains in proteins, and the path files provide the corresponding locations.

**fas_index.json**
Specifies which file in the `fas_scores/` directory contains the FAS scores for each gene. Acts as a lookup index for score data.

**fas.phyloprofile**
Tab-delimited file mapping FAS transcripts to their orthologs. Includes FAS scores in forward (**FAS_F**) and backward (**FAS_B**) comparisons.

**fas_scores/**
Directory containing `.json` files with pairwise FAS scores for transcript comparisons.

**forward.domains**
Tab-delimited file describing annotated domains and features for each pair of orthologous FAS sequences in the **forward direction**. Includes domain positions, feature types (e.g., Pfam, SMART, TMHMM), scores, and matched positions.

**reverse.domains**
Tab-delimited file describing annotated domains and features for each pair of orthologous FAS sequences in the **backward direction**. Includes domain positions, feature types (e.g., Pfam, SMART, TMHMM), scores, and matched positions.

**important_features.json**
JSON file listing domains that differ between isoforms of the same gene. If one transcript has a domain and another does not, it is recorded here. These entries are especially relevant for detecting functional changes due to alternative splicing.

#### **transcript_data/**

```bash
transcript_data/
├── genes.txt
├── phyloprofile_ids.tsv
├── sequences.json
├── transcript_info.json
├── transcript_pairings.json
└── transcript_set.fasta
```

**genes.txt**

List of gene identifiers included in the SPICE library.

**phyloprofile_ids.tsv**

Tab-separated file listing protein transcript IDs and their corresponding NCBI taxonomy IDs.

**sequences.json**

JSON file containing peptide sequences for all proteins in the library.

**transcript_info.json**

Structured JSON file containing gene- and transcript-level metadata for all entries in the library. Each gene includes its name, biotype, taxon ID, chromosome, and species, as well as its associated transcripts. For each transcript, attributes include its Ensembl protein and transcript ID, name, biotype, support level (TSL), and annotation tags.

**transcript_pairings.json**

JSON file containing transcript pairings for each gene in the library. Each key is a gene ID, and the corresponding value is a tab-separated string with two transcript identifiers. These represent the primary transcript pairings used for FAS scoring.

**transcript_set.fasta**

FASTA file containing **protein sequences** (please don't kill the messenger) for all transcripts used in the library. Each header includes the gene ID, protein ID, and taxonomy ID in the format:
`>GENE_ID|PROTEIN_ID|TAXON_ID`

### Pipeline information

These are files created by nextflow to store information about the pipeline run.

Check out the [nextflow documentation](https://www.nextflow.io/docs/latest/reports.html) to learn more about the reports

```bash
pipeline_info/
├── execution_report_2025-04-02_18-22-23.html
├── execution_timeline_2025-04-02_18-22-23.html
├── execution_trace_2025-04-02_18-22-23.txt
├── params_2025-04-02_18-22-35.json
├── pipeline_dag_2025-04-02_18-22-23.html
└── pipeline_software_versions.yml
```

> **Note:** File names include timestamps based on when the pipeline was run. Your output files will have different names depending on the execution date. You can also modify the suffix by using the `trace_report_suffix` parameter.

**execution_report.html**

Interactive report showing a summary of the pipeline run. Includes status of processes, run duration and resource usage.

**execution_timeline.html**

Detailed timeline of each process in the workflow. Useful for visualizing parallelization and bottlenecks.

**execution_trace.txt**

Tabular log of all processes with runtime, memory, and CPU usage. Can be used for in-depth resource tracking.

**pipeline_dag.html**

Graph view of the pipeline structure. Shows the order and dependencies of all processes.

**params.json**

JSON file containing all parameters used in the pipeline run. Helpful for reproducibility.

**pipeline_software_versions.yml**

List of software and versions used in the pipeline.
