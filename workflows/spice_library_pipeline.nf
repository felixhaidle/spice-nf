/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES / SUBWORKFLOWS / FUNCTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
include { paramsSummaryMap       } from 'plugin/nf-schema'
include { softwareVersionsToYAML } from '../subworkflows/nf-core/utils_nfcore_pipeline'
<<<<<<< HEAD:workflows/spice-nf.nf
include { methodsDescriptionText } from '../subworkflows/local/utils_nfcore_spice_nf_pipeline'
include { LIBRARY_GENERATION     } from '../subworkflows/local/library_generation.nf'
=======
include { methodsDescriptionText } from '../subworkflows/local/utils_nfcore_spice_library_pipeline_pipeline'
>>>>>>> TEMPLATE:workflows/spice_library_pipeline.nf

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

<<<<<<< HEAD:workflows/spice-nf.nf
workflow SPICE_NF {
=======
workflow SPICE_LIBRARY_PIPELINE {
>>>>>>> TEMPLATE:workflows/spice_library_pipeline.nf

    take:
        species       // String: Ensembl species name
        release       // Integer: Ensembl release version
        anno_tools    // Path: Path to annotation tools file
        outdir        // Path: Output directory for the library
        test_mode     // Boolean: Whether to run in test mode
        annotation_gtf
        peptide_fasta

    main:

<<<<<<< HEAD:workflows/spice-nf.nf
        ch_versions = Channel.empty()

        // Run library generation
        LIBRARY_GENERATION(
            species = species,
            release = release,
            anno_tools = anno_tools,
            outdir = outdir,
            test_mode = test_mode,
            annotation_gtf = annotation_gtf,
            peptide_fasta = peptide_fasta
        ).set { ch_library }
=======
    ch_versions = Channel.empty()

    //
    // Collate and save software versions
    //
    softwareVersionsToYAML(ch_versions)
        .collectFile(
            storeDir: "${params.outdir}/pipeline_info",
            name:  'spice_library_pipeline_software_'  + 'versions.yml',
            sort: true,
            newLine: true
        ).set { ch_collated_versions }
>>>>>>> TEMPLATE:workflows/spice_library_pipeline.nf

        //
        // Collate and save software versions
        //
        softwareVersionsToYAML(ch_versions)
            .collectFile(
                storeDir: "${params.outdir}/pipeline_info",
                name:  ''  + 'pipeline_software_' +  ''  + 'versions.yml',
                sort: true,
                newLine: true
            ).set { ch_collated_versions }

    emit:
        library        = ch_library                 // channel: Generated library
        versions       = ch_versions               // channel: [ path(versions.yml) ]
}


/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
