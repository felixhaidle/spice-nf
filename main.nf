#!/usr/bin/env nextflow
/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    BIONF/spice-nf
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Github : https://github.com/felixhaidle/spice-nf
----------------------------------------------------------------------------------------
*/

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT FUNCTIONS / MODULES / SUBWORKFLOWS / WORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { SPICE_NF  } from './workflows/spice-nf'
include { PIPELINE_INITIALISATION } from './subworkflows/local/utils_nfcore_spice_nf_pipeline'
include { PIPELINE_COMPLETION     } from './subworkflows/local/utils_nfcore_spice_nf_pipeline'
/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    NAMED WORKFLOWS FOR PIPELINE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

//
// WORKFLOW: Run main analysis pipeline depending on type of input
//
workflow BIONF_SPICE_NF {
    take:
        species       // String: Ensembl species name
        release       // Integer: Ensembl release version
        anno_tools    // Path: Path to annotation tools file
        outdir        // Path: Path to output
        test_mode     // Boolean: Indicating test mode
        annotation_gtf  // Path: Path to GTF annotation file
        peptide_fasta   // Path: Path to peptide FASTA file
    main:

    //
    // WORKFLOW: Run pipeline
    //
    SPICE_NF (
        species,       // String: Ensembl species name
        release,       // Integer: Ensembl release version
        anno_tools,    // Path: Path to annotation tools file
        outdir,
        test_mode,
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
        params.input,
        params.species,      // Add the species parameter
        params.release,      // Add the release parameter
        params.anno_tools,   // Add the annotation tools parameter
        params.test_mode,
        params.annotation_gtf,  // New parameter
        params.peptide_fasta    // New parameter
    )

    //
    // WORKFLOW: Run main workflow
    //
    BIONF_SPICE_NF (
        params.species,
        params.release,
        params.anno_tools,
        params.outdir,        
        params.test_mode,     
        params.annotation_gtf,  
        params.peptide_fasta    
    )
    //
    // SUBWORKFLOW: Run completion tasks
    //
    PIPELINE_COMPLETION (
        params.email,
        params.email_on_fail,
        params.plaintext_email,
        params.outdir,
        params.monochrome_logs,
        params.hook_url
        
    )
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
