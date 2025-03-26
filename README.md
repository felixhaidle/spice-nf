# BIONF/spice_library_pipeline

## Introduction

The tool **Splicing-based Protein Isoform Comparison Estimator (SPICE)** was created by Christian Blümel. The original implementation can be found in this repository: https://github.com/chrisbluemel/SPICE.

This repository contains a Nextflow-based pipeline to automate the creation of SPICE libraries.
Instead of running multiple scripts manually, you can now use this streamlined pipeline.

It is roughly divided into the following steps:

* (Down)load transcriptome files
* Initialize the SPICE library structure
* Annotate peptide sequences for FAS scoring
* Reorganize the library structure
* FAS scoring
* Merge FAS scores

## Usage

SPICE heavily relies on **FAS** to function, as the FAS algorithm estimates transcript (dis)similarities.

FAS itself depends on various annotation tools, which cannot be bundled with this pipeline.
You must first follow the instructions here: https://github.com/BIONF/FAS.

Make sure the following command runs successfully in the environment where you will execute the pipeline (e.g., when submitting a job via SLURM):

```bash
fas.doAnno -i test_annofas.fa -o test_output
```

As this pipeline is not part of nf-core, you first need to clone the repository:

```bash
git clone git@github.com:felixhaidle/spice-nf.git
```

After cloning, you should test the functionality using the test profile.

> [!NOTE]
> If you are new to Nextflow and nf-core, please refer to [this page](https://nf-co.re/docs/usage/installation) for instructions on setting up Nextflow.
> Make sure to [test your setup](https://nf-co.re/docs/usage/introduction#how-to-run-a-pipeline) using `-profile test` before running the workflow on actual data.

> [!WARNING]
> This pipeline currently only supports the "conda" profile. The environment requirements are defined in `assets/environment.yml`. All processes use the same environment.

```bash
nextflow run BIONF/spice_library_pipeline \
   -profile conda,test \
   --outdir <OUTDIR>
```

### Run the full pipeline:

```bash
nextflow run BIONF/spice_library_pipeline \
   -profile conda \
   --species <SPECIES> \
   --release <ENSEMBL_RELEASE_VERSION> \
   --anno_tools <PATH_TO_ANNOTOOLS_INSTALLATION> \
   --outdir <OUTDIR>
```


| Parameter         | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `-profile conda`  | Specifies the execution profile (only `conda` is supported).                                 |
| `--species`       | Species name (e.g., `homo_sapiens`, `mus_musculus`). Must match ENSEMBL naming. |
| `--release`       | ENSEMBL release version (e.g., `109`, `110`). Used to fetch annotation data. |
| `--anno_tools`    | Path to the installed annotation tools directory (equivalent to the `-t` parameter in `fas.setup`). |
| `--outdir`        | Output directory for pipeline results. Will be created if it doesn't exist.  |

A full overview of all available parameters can be found in [`parameters.md`](assets/parameters.md).

> [!WARNING]
> Please provide pipeline parameters via the CLI or the Nextflow `-params-file` option.
> Custom config files (via the `-c` option) can be used for configuration **except for parameters**; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

A full list of available parameters and documentation can also be found in the **Wiki**.

## Credits

`BIONF/spice_library_pipeline` was originally written by **Felix Haidle**.

We thank the following people for their extensive assistance in the development of this pipeline:

<!-- TODO nf-core: If applicable, make list of people who have also contributed -->

## Citations

<!-- TODO nf-core: Add citation for pipeline after first release. Uncomment lines below and update Zenodo doi and badge at the top of this file. -->
<!-- If you use BIONF/spice_library_pipeline for your analysis, please cite it using the following doi: [10.5281/zenodo.XXXXXX](https://doi.org/10.5281/zenodo.XXXXXX) -->

<!-- TODO nf-core: Add bibliography of tools and data used in your pipeline -->

An extensive list of references for the tools used by the pipeline can be found in [`CITATIONS.md`](CITATIONS.md).

This pipeline uses code and infrastructure developed and maintained by the [nf-core](https://nf-co.re) community, reused here under the [MIT license](https://github.com/nf-core/tools/blob/main/LICENSE).

> **The nf-core framework for community-curated bioinformatics pipelines.**
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).
