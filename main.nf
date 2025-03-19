#!/usr/bin/env nextflow
/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    BIONF/spice_library_pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Github : https://github.com/felixhaidle/spice-nf
----------------------------------------------------------------------------------------
*/

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT FUNCTIONS / MODULES / SUBWORKFLOWS / WORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { SPICE_LIBRARY_PIPELINE  } from './workflows/spice_library_pipeline'
include { PIPELINE_INITIALISATION } from './subworkflows/local/utils_nfcore_spice_library_pipeline_pipeline'
include { PIPELINE_COMPLETION     } from './subworkflows/local/utils_nfcore_spice_library_pipeline_pipeline'
/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    NAMED WORKFLOWS FOR PIPELINE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

//
// WORKFLOW: Run main analysis pipeline depending on type of input
//
workflow BIONF_SPICE_LIBRARY_PIPELINE {

    take:
        species       // String: Ensembl species name
        release       // Integer: Ensembl release version
        anno_tools    // Path: Path to annotation tools file
        outdir        // Path: Path to output
        annotation_gtf  // Path: Path to GTF annotation file
        peptide_fasta   // Path: Path to peptide FASTA file
    main:

    //
    // WORKFLOW: Run pipeline
    //
    SPICE_LIBRARY_PIPELINE (
        species,       // String: Ensembl species name
        release,       // Integer: Ensembl release version
        anno_tools,    // Path: Path to annotation tools file
        outdir,
        annotation_gtf, // Path: Path to GTF annotation file
        peptide_fasta   // Path: Path to peptide FASTA file
    )
}
/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow {

    main:
    //
    // SUBWORKFLOW: Run initialisation tasks
    //
    PIPELINE_INITIALISATION (
        params.version,
        params.validate_params,
        params.monochrome_logs,
        args,
        params.outdir,
        params.species,      // Add the species parameter
        params.release,      // Add the release parameter
        params.anno_tools,   // Add the annotation tools parameter
        params.annotation_gtf,  // New parameter
        params.peptide_fasta    // New parameter
    )

    //
    // WORKFLOW: Run main workflow
    //
    BIONF_SPICE_LIBRARY_PIPELINE (
        params.species,
        params.release,
        params.anno_tools,
        params.outdir,
        params.annotation_gtf,
        params.peptide_fasta
    )
    //
    // SUBWORKFLOW: Run completion tasks
    //
    PIPELINE_COMPLETION (
        params.outdir,
        params.monochrome_logs,
    )
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
