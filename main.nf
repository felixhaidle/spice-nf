#!/usr/bin/env nextflow
/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    BIONF/spice_library_pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
<<<<<<< HEAD
    Github : https://github.com/felixhaidle/spice-nf
=======
    Github : https://github.com/BIONF/spice_library_pipeline
>>>>>>> TEMPLATE
----------------------------------------------------------------------------------------
*/

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT FUNCTIONS / MODULES / SUBWORKFLOWS / WORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

<<<<<<< HEAD
include { SPICE_NF  } from './workflows/spice-nf'
include { PIPELINE_INITIALISATION } from './subworkflows/local/utils_nfcore_spice_nf_pipeline'
include { PIPELINE_COMPLETION     } from './subworkflows/local/utils_nfcore_spice_nf_pipeline'
=======
include { SPICE_LIBRARY_PIPELINE  } from './workflows/spice_library_pipeline'
include { PIPELINE_INITIALISATION } from './subworkflows/local/utils_nfcore_spice_library_pipeline_pipeline'
include { PIPELINE_COMPLETION     } from './subworkflows/local/utils_nfcore_spice_library_pipeline_pipeline'
>>>>>>> TEMPLATE
/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    NAMED WORKFLOWS FOR PIPELINE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

//
// WORKFLOW: Run main analysis pipeline depending on type of input
//
<<<<<<< HEAD
workflow BIONF_SPICE_NF {
=======
workflow BIONF_SPICE_LIBRARY_PIPELINE {

>>>>>>> TEMPLATE
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
<<<<<<< HEAD
    SPICE_NF (
        species,       // String: Ensembl species name
        release,       // Integer: Ensembl release version
        anno_tools,    // Path: Path to annotation tools file
        outdir,
        test_mode,
        annotation_gtf, // Path: Path to GTF annotation file
        peptide_fasta   // Path: Path to peptide FASTA file
=======
    SPICE_LIBRARY_PIPELINE (
        samplesheet
>>>>>>> TEMPLATE
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
<<<<<<< HEAD
    BIONF_SPICE_NF (
        params.species,
        params.release,
        params.anno_tools,
        params.outdir,        
        params.test_mode,     
        params.annotation_gtf,  
        params.peptide_fasta    
=======
    BIONF_SPICE_LIBRARY_PIPELINE (
        PIPELINE_INITIALISATION.out.samplesheet
>>>>>>> TEMPLATE
    )
    //
    // SUBWORKFLOW: Run completion tasks
    //
    PIPELINE_COMPLETION (
        params.outdir,
        params.monochrome_logs,
<<<<<<< HEAD
        params.hook_url
        
=======
>>>>>>> TEMPLATE
    )
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
