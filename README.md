# BIONF/spice_library_pipeline

## Acknowledgements & Original Software

This pipeline includes adaptations from the **Splicing-based Protein Isoform Comparison Estimator (SPICE)** tool, originally developed by [Christian Blümel](https://github.com/chrisbluemel) and [Julian Dosch](https://github.com/JuRuDo).
The original SPICE implementation is available at [https://github.com/chrisbluemel/SPICE](https://github.com/chrisbluemel/SPICE) and is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Introduction

This repository contains a Nextflow-based pipeline to automate the creation of SPICE libraries.
Instead of running multiple scripts manually, you can now use this streamlined pipeline.

```mermaid
flowchart TB
    %% Parameters %%
    subgraph PARAMETERS
        species[species]
        release[release]
        anno_tools[anno_tools]
        outdir[outdir]
    end

    %% Processes %%
    subgraph PIPELINE
        SEQUENCES[SEQUENCES]
        TOOLS[TOOLS]
        LIBRARY_INITIALIZATION[LIBRARY_INITIALIZATION]
        FAS_ANNOTATION[FAS_ANNOTATION]
        LIBRARY_RESTRUCTURE[LIBRARY_RESTRUCTURE]
        FAS_SCORING[FAS_SCORING]
        CONCAT_FAS_SCORES[CONCAT_FAS_SCORES]
    end

    %% Outputs %%
    subgraph OUTPUTS
        library[library]
    end

    %% Connections %%
    species --> SEQUENCES
    release --> SEQUENCES
    SEQUENCES --> LIBRARY_INITIALIZATION

    species --> LIBRARY_INITIALIZATION
    release --> LIBRARY_INITIALIZATION

    anno_tools --> TOOLS

    TOOLS --> LIBRARY_INITIALIZATION
    TOOLS --> FAS_ANNOTATION

    LIBRARY_INITIALIZATION --> FAS_ANNOTATION
    FAS_ANNOTATION --> LIBRARY_RESTRUCTURE
    LIBRARY_RESTRUCTURE --> FAS_SCORING
    LIBRARY_RESTRUCTURE --> CONCAT_FAS_SCORES

    FAS_SCORING --> CONCAT_FAS_SCORES
    outdir --> CONCAT_FAS_SCORES

    CONCAT_FAS_SCORES --> library
```

It is roughly divided into the following steps:

The pipeline is roughly divided into the following steps:

- Download peptide sequences and annotation files from [ENSEMBL](https://www.ensembl.org/index.html) for the target organism.
- Initialize the SPICE library structure and fetch species metadata from [ENSEMBL](https://www.ensembl.org/index.html).
- Annotate the peptide sequences using [fas.doAnno](https://doi.org/10.1093/bioinformatics/btad226).
- Restructure the annotated sequences in preparation for FAS scoring.
- Perform FAS scoring using [fas.run](https://doi.org/10.1093/bioinformatics/btad226).
- Merge the resulting FAS scores into the final library structure.

## Usage

Below is the general installation/setup/usage explanation. A detailed explanation and further assistance can be found in the [WIKI](https://github.com/felixhaidle/spice-nf/wiki)

> [!NOTE]
> If you are from AK Ebersberger please refer to the [AKE usage documentation](https://github.com/felixhaidle/spice-nf/wiki/02_1-Usage-AKE).

### Install FAS

SPICE heavily relies on **FAS** to function, as the FAS algorithm estimates transcript (dis)similarities.

FAS itself depends on various annotation tools, which cannot be bundled with this pipeline.
You must first follow the instructions [here](https://github.com/BIONF/FAS) to set it up.

Make sure the following command runs successfully in the environment where you will execute the pipeline (e.g., when submitting a job via SLURM):

```bash
fas.doAnno -i test_annofas.fa -o test_output
```

### Set up the pipeline

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

| Parameter        | Description                                                                                         |
| ---------------- | --------------------------------------------------------------------------------------------------- |
| `-profile conda` | Specifies the execution profile (only `conda` is supported).                                        |
| `--species`      | Species name (e.g., `homo_sapiens`, `mus_musculus`). Must match ENSEMBL naming.                     |
| `--release`      | ENSEMBL release version (e.g., `109`, `110`). Used to fetch annotation data.                        |
| `--anno_tools`   | Path to the installed annotation tools directory (equivalent to the `-t` parameter in `fas.setup`). |
| `--outdir`       | Output directory for pipeline results. Will be created if it doesn't exist.                         |

A full overview of all available parameters can be found in [`parameters.md`](docs/parameters.md).

> [!WARNING]
> Please provide pipeline parameters via the CLI or the Nextflow `-params-file` option.
> Custom config files (via the `-c` option) can be used for configuration **except for parameters**; see [docs](https://nf-co.re/docs/usage/getting_started/configuration#custom-configuration-files).

A full list of available parameters and documentation can also be found in the **Wiki**.

## Credits

`BIONF/spice_library_pipeline` was originally written by **Felix Haidle**.

We thank the following people for their extensive assistance in the development of this pipeline:

<!-- TODO nf-core: If applicable, make list of people who have also contributed -->

## AI Assistance Acknowledgment

Parts of this project’s documentation, code structuring, and scripting were developed with the assistance of AI (ChatGPT by OpenAI).
All final decisions, modifications, and validations were made by the project author(s).

## Citations

<!-- TODO nf-core: Add citation for pipeline after first release. Uncomment lines below and update Zenodo doi and badge at the top of this file. -->
<!-- If you use BIONF/spice_library_pipeline for your analysis, please cite it using the following doi: [10.5281/zenodo.XXXXXX](https://doi.org/10.5281/zenodo.XXXXXX) -->

<!-- TODO nf-core: Add bibliography of tools and data used in your pipeline -->

An extensive list of references for the tools used by the pipeline can be found in [`CITATIONS.md`](CITATIONS.md).

This pipeline uses code and infrastructure developed and maintained by the [nf-core](https://nf-co.re) community, reused here under the [MIT license](https://github.com/nf-core/tools/blob/main/LICENSE).

> **The nf-core framework for community-curated bioinformatics pipelines.**
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).
