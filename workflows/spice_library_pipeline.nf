/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES / SUBWORKFLOWS / FUNCTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
include { paramsSummaryMap       } from 'plugin/nf-schema'
include { softwareVersionsToYAML } from '../subworkflows/nf-core/utils_nfcore_pipeline'
include { methodsDescriptionText } from '../subworkflows/local/utils_nfcore_spice_library_pipeline_pipeline'

include { FAS_ANNOTATION         } from '../modules/local/fas/annotation'
include { FAS_SCORING            } from '../modules/local/fas/scoring'
include { CONCAT_FAS_SCORES      } from '../modules/local/concat'
include { SEQUENCES              } from '../modules/local/sequences'
include { LIBRARY_INITIALIZATION } from '../modules/local/initialization'
include { LIBRARY_RESTRUCTURE    } from '../modules/local/restructure'


/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow SPICE_LIBRARY_PIPELINE {

    take:
        species         // String: Ensembl species name
        release         // Integer: Ensembl release version
        anno_tools      // Path: Path to annotation tools file
        outdir          // Path: Output directory for the library
        annotation_gtf
        peptide_fasta

    main:

        ch_versions = Channel.empty()

        // Run library generation
        sequence_files = SEQUENCES(
            species,
            release,
            annotation_gtf,
            peptide_fasta
        )



        prefixes = channel.fromPath("${projectDir}/assets/ensembl_stable_id_prefixes.json")

        create_library = LIBRARY_INITIALIZATION(
            sequence_files.gtf_file,
            sequence_files.fasta_file,
            species,
            release,
            prefixes
        )
        ch_versions = ch_versions.mix(LIBRARY_INITIALIZATION.out.versions)

        annotated_library = FAS_ANNOTATION(
            anno_tools,
            create_library.library_dir
        )

        ch_versions = ch_versions.mix(FAS_ANNOTATION.out.versions)

        domain_importance_library = LIBRARY_RESTRUCTURE(
            annotated_library.annotated_library_ch
        )
        ch_versions = ch_versions.mix(LIBRARY_RESTRUCTURE.out.versions)

        // Channel to read gene IDs and resource requirements from the file genes.txt
        genes_ch = create_library.genes_txt_ch
        .splitText()
        .map { it.trim().split(' ') }
        .map { it[0] }  // Extract only gene_id


        fas_scores = FAS_SCORING(
            genes_ch,
            domain_importance_library.domain_importance_library_ch,
            anno_tools
            )

        ch_versions = ch_versions.mix(FAS_SCORING.out.versions)

        fas_score_library = fas_scores.fas_scored_directories.collect()

        concatenated_fas_scores_library = CONCAT_FAS_SCORES (
            fas_score_library,
            domain_importance_library.domain_importance_library_ch,
            outdir
        )

        ch_versions = ch_versions.mix(CONCAT_FAS_SCORES.out.versions)

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
        library        = concatenated_fas_scores_library.finished_library                 // channel: Generated library
        versions       = ch_versions               // channel: [ path(versions.yml) ]
}


/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
