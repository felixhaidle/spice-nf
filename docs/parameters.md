# BIONF/spice_library_pipeline pipeline parameters

Nextflow pipeline to create SPICE libraries

## Input/output options

Define where the pipeline should find input data and save output data.

| Parameter | Description | Type | Default | Required |
|-----------|-----------|-----------|-----------|-----------|
| `outdir` | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. | `string` | results | True |
| `species` | Species name as available on Ensembl, in lowercase (e.g., 'homo_sapiens', 'mus_musculus'). <details><summary>Help</summary><small>Provide the species name in Ensembl format. Must be lowercase with underscores. Example: 'homo_sapiens' for human or 'mus_musculus' for mouse.</small></details>| `string` |  | True |
| `release` | Ensembl genome release version (e.g., '113'). <details><summary>Help</summary><small>Specify the Ensembl release version for the genome (e.g., 113).</small></details>| `integer` |  | True |
| `anno_tools` | Path to the directory containing annotation tool files. <details><summary>Help</summary><small>Specify the path to the directory where the annotation tool files are stored. Each file in the directory should describe a tool (e.g., ToolName:ToolVersion).</small></details>| `string` |  | True |
| `annotation_gtf` | Path to the GTF annotation file. <details><summary>Help</summary><small>Provide the path to the GTF annotation file if available. This parameter is optional.</small></details>| `string` |  |  |
| `peptide_fasta` | Path to the peptide FASTA file. <details><summary>Help</summary><small>Provide the path to the peptide FASTA file if available. This parameter is optional.</small></details>| `string` |  |  |
| `exclude_anno` | Annotation tools that should NOT be used for the FAS annotation | `string` |  |  |

## fas.doAnno options

Optional parameters that can be used to adjust the FAS annotation

| Parameter | Description | Type | Default | Required |
|-----------|-----------|-----------|-----------|-----------|
| `fas_doAnno_eInstance` | E-value cutoff for PFAM/SMART domain instances. Default: 0.01 | `string` |  |  |
| `fas_doAnno_hmmCores` | Number of CPUs dedicated to HMMER-based domain search (Pfam/SMART) | `string` |  |  |
| `fas_doAnno_eFlps` | E-value cutoff for fLPS domain annotation. Default: 1e-7 | `string` |  |  |
| `fas_doAnno_org` | Organism type used for SignalP annotation | `string` |  |  |
| `fas_doAnno_eFeature` | E-value cutoff for PFAM/SMART domains in annotation. Default: 0.001 | `string` |  |  |

## fas.run options

Optional parameters to adjust the FAS scoring

| Parameter | Description | Type | Default | Required |
|-----------|-----------|-----------|-----------|-----------|
| `fas_run_eInstance` | E-value cutoff for domain instances in FAS scoring. Default: 0.01 | `string` |  |  |
| `fas_run_eFlps` | E-value cutoff for fLPS in FAS scoring. Default: 1e-7 | `string` |  |  |
| `fas_run_eFeature` | E-value cutoff for PFAM/SMART domains in FAS scoring. Default: 0.001 | `string` |  |  |
| `fas_run_org` | Organism type used during SignalP-based scoring | `string` |  |  |
| `fas_run_weight_correction` | Weighting function for feature frequencies in scoring | `string` |  |  |
| `fas_run_ref_proteome` | Path to reference proteome used for weighting features | `string` |  |  |
| `fas_run_priority_threshold` | Threshold to activate priority mode for dense feature architectures. Default: 30 | `string` |  |  |
| `fas_run_max_cardinality` | Maximum number of feature paths allowed before triggering fallback strategies. Default: 500 | `string` |  |  |
| `fas_run_score_weights` | Three space-separated floats defining weights for MS, CS, and PS scores. Example: '0.7 0.0 0.3' | `string` |  |  |
| `fas_run_paths_limit` | Path complexity limit (as 10^n). Default: 0 (no limit) | `string` |  |  |
| `fas_run_max_overlap_percentage` | Maximum percentage overlap allowed between features. Default: 0.4 | `string` |  |  |

## Generic options

Less common options for the pipeline, typically set in a config file.

| Parameter | Description | Type | Default | Required |
|-----------|-----------|-----------|-----------|-----------|
| `version` | Display version and exit. | `boolean` |  |  |
| `publish_dir_mode` | Method used to save pipeline results to output directory. <details><summary>Help</summary><small>The Nextflow `publishDir` option specifies which intermediate files should be saved to the output directory. This option tells the pipeline what method should be used to move these files. See [Nextflow docs](https://www.nextflow.io/docs/latest/process.html#publishdir) for details.</small></details>| `string` | copy |  |
| `monochrome_logs` | Do not use coloured log outputs. | `boolean` |  |  |
| `validate_params` | Boolean whether to validate parameters against the schema at runtime | `boolean` | True |  |
| `pipelines_testdata_base_path` | Base URL or local path to location of pipeline test dataset files | `string` | https://raw.githubusercontent.com/nf-core/test-datasets/ |  |
| `trace_report_suffix` | Suffix to add to the trace report filename. Default is the date and time in the format yyyy-MM-dd_HH-mm-ss. | `string` |  |  |

## Institutional config options

Parameters used to describe centralised config profiles. These should not be edited.

| Parameter | Description | Type | Default | Required |
|-----------|-----------|-----------|-----------|-----------|
| `custom_config_version` | Git commit id for Institutional configs. | `string` | master |  |
| `custom_config_base` | Base directory for Institutional configs. <details><summary>Help</summary><small>If you're running offline, Nextflow will not be able to fetch the institutional config files from the internet. If you don't need them, then this is not a problem. If you do need them, you should download the files from the repo and tell Nextflow where to find them with this parameter.</small></details>| `string` | https://raw.githubusercontent.com/nf-core/configs/master |  |
| `config_profile_name` | Institutional config name. | `string` |  |  |
| `config_profile_description` | Institutional config description. | `string` |  |  |
| `config_profile_contact` | Institutional config contact information. | `string` |  |  |
| `config_profile_url` | Institutional config URL link. | `string` |  |  |

## Other parameters

| Parameter | Description | Type | Default | Required |
|-----------|-----------|-----------|-----------|-----------|
| `input` | Not used in this pipeline | `string` |  |  |
