# SPICE Library Comparison Script

## Overview

This script compares the contents of two SPICE library directories, verifying whether Library1 is a subset of Library2 in structure and content. It checks for differences in folder layout, annotation entries, FAS scores, and associated metadata.

## Usage

Run the script from the command line as follows:

```bash
python compare_libraries.py --library1 <path/to/library1> --library2 <path/to/library2>
```

Where:

- `--library1`: Path to the first SPICE library directory (expected subset).
- `--library2`: Path to the second SPICE library directory (reference set).

> ℹ️ All results are written to a file named `comparison_report.txt`, and also printed to the console.

## Functionality

### 1. 📁 Directory Structure Comparison

- Compares the file and folder structure of both libraries.
- Reports missing files in either directory.

### 2. 📄 Annotations File (`annotations.json`)

- Ensures all top-level keys in Library1's `annotations.json` exist in Library2.
- Reports missing keys or mismatches in sub-entries.

### 3. 📊 FAS Scores (`fas_scores/*.json`)

- Aggregates all FAS score files in both libraries.
- Compares presence of genes, transcripts, and partner scores.
- Reports discrepancies in FAS data.

### 4. 📃 Annotation Tools File (`annotools.txt`)

- Verifies the presence of the file in both libraries.
- Compares file content line-by-line.

### 5. 🔬 Important Features (`important_features.json`)

- Compares the presence of keys between libraries.
- Checks if all values under each key in Library1 exist in Library2.

## Output

The script produces a structured output both on the console and in a file:

- ✅ Matching elements
- ❌ Missing files, genes, transcripts, or values
- 🔄 Differences in annotation content or FAS scores
