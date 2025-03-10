# README: SPICE Library Comparison Script

## Overview
This script compares the contents of two SPICE library directories, verifying that Library1 is a valid subset of Library2. It performs structural and content-based comparisons across multiple files and folders within the libraries.

## Usage
Run the script using the following command:
```
python compare_libraries.py <library1_path> <library2_path>
```
where:
- `<library1_path>`: Path to the first SPICE library directory.
- `<library2_path>`: Path to the second SPICE library directory.

## Functionality
### 1. **Directory Structure Comparison**
- Ensures both library directories have the same folder and file structure.
- Reports files or folders missing in either directory.

### 2. **Annotations File (`annotations.json`)**
- Verifies that all key-value pairs in `annotations.json` from Library1 exist in Library2.
- Identifies missing keys and mismatched values.

### 3. **FAS Scores (`fas_scores` JSON Files)**
- Merges all `.json` files in `fas_scores/` into a unified dictionary for comparison.
- Checks if all genes from Library1 exist in Library2.
- Verifies transcript pairings within each gene.
- Compares FAS scores and reports discrepancies.

### 4. **Annotation Tools File (`annotools.txt`)**
- Ensures that `annotools.txt` exists in both libraries.
- Compares content line-by-line and reports differences.

### 5. **Important Features (`important_features.json`)**
- Checks if all keys from Library1 exist in Library2.
- Verifies that all values (gene lists) for each key in Library1 are present in Library2.
- Reports missing keys and missing values.

## Output
The script provides a structured console output highlighting:
- ✅ Matching elements.
- ❌ Missing files, genes, transcripts, or values.
- 🔄 Differences in key contents or FAS scores.

## Next Steps
Potential enhancements:
- Log mismatches to a file instead of console output.
- Introduce numerical tolerance for minor floating-point differences in FAS scores.
- Allow optional case-insensitive comparisons for `important_features.json`.

For further improvements or debugging, feel free to modify the script accordingly!

---
created by Felix Haidle, using ChatGPT

