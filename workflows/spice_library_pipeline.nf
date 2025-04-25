// Copyright (C) 2025 Felix Haidle
// Licensed under GNU GPL v3. See LICENSE file or https://www.gnu.org/licenses/gpl-3.0.en.html

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT MODULES / SUBWORKFLOWS / FUNCTIONS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

// nf-core
include { paramsSummaryMap       } from 'plugin/nf-schema'
include { softwareVersionsToYAML } from '../subworkflows/nf-core/utils_nfcore_pipeline'
include { methodsDescriptionText } from '../subworkflows/local/utils_nfcore_spice_library_pipeline_pipeline'

// local
include { FAS_ANNOTATION         } from '../modules/local/fas/annotation'
include { FAS_SCORING            } from '../modules/local/fas/scoring'
include { CONCAT_GENES           } from '../modules/local/concat/genes'
include { SEQUENCES              } from '../modules/local/sequences'
include { LIBRARY_INITIALIZATION } from '../modules/local/initialization'
include { LIBRARY_RESTRUCTURE    } from '../modules/local/restructure'
include { TOOLS                  } from '../modules/local/tools'
include { COMPLEXITY             } from '../modules/local/complexity'
include { METADATA               } from '../modules/local/metadata'
include { SEED_PARALLELIZATION   } from '../modules/local/seed_parallelization'
include { CONCAT_PROTEIN_PAIRS   } from '../modules/local/concat/protein_pairs'

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
        annotation_gtf  // Path: Path to a .gtf file
        peptide_fasta   // PAth: PAth to a .fasta file

    main:

        //
        // Initialize channel to track the versions of the used software
        //

        ch_versions = Channel.empty()

        //
        // Logic to use either supplied annotation and fasta file or download them
        //

        gtf_file_ch = Channel.empty()
        fasta_file_ch = Channel.empty()

        def gtf_exists = annotation_gtf && file(annotation_gtf).exists()
        def fasta_exists = peptide_fasta && file(peptide_fasta).exists()


        if (!gtf_exists || !fasta_exists) {
            metadata_ch = SEQUENCES(
                species,
                release
            )
            ch_versions = ch_versions.mix(SEQUENCES.out.versions)



            gtf_file_ch = metadata_ch.gtf_file
            fasta_file_ch = metadata_ch.fasta_file
        } else {
            metadata_ch = METADATA(
                species,
                params.is_ensembl
            )

            ch_versions = ch_versions.mix(METADATA.out.versions)

            gtf_file_ch = channel.fromPath(annotation_gtf)
            fasta_file_ch = channel.fromPath(peptide_fasta)


        }







        //
        // Load the file with the ENSEMBL stable ID prefixes
        //

        prefixes = channel.fromPath("${projectDir}/assets/ensembl_stable_id_prefixes.json")

        //
        // Update annoTools.txt if there is the user input to exclude an annotation tool
        //

        anno_tools_ch = Channel.empty()

        if (params.exclude_anno) {
            updated_anno_tools_ch = TOOLS(
                channel.fromPath("${anno_tools}/annoTools.txt"),
                params.exclude_anno
            )

            anno_tools_ch = updated_anno_tools_ch.anno_file
            ch_versions = ch_versions.mix(TOOLS.out.versions)

        } else {
            anno_tools_ch = channel.fromPath("${anno_tools}/annoTools.txt")
        }


        //
        // Library generation logic
        //

        create_library = LIBRARY_INITIALIZATION(
            gtf_file_ch,
            fasta_file_ch,
            metadata_ch.species_name,
            metadata_ch.release,
            prefixes,
            anno_tools_ch,
            metadata_ch.taxon_id
        )
        ch_versions = ch_versions.mix(LIBRARY_INITIALIZATION.out.versions)

        annotated_library = FAS_ANNOTATION(
            anno_tools,
            create_library.library_dir,
            anno_tools_ch
        )

        ch_versions = ch_versions.mix(FAS_ANNOTATION.out.versions)

        domain_importance_library = LIBRARY_RESTRUCTURE(
            annotated_library.annotated_library_ch
        )
        ch_versions = ch_versions.mix(LIBRARY_RESTRUCTURE.out.versions)

        //
        // Channel to read gene IDs and resource requirements from the file genes.txt
        //

        complexity_ch = COMPLEXITY(
            domain_importance_library.domain_importance_library_ch,
            anno_tools_ch
        )
        ch_versions = ch_versions.mix(COMPLEXITY.out.versions)

        protein_pairs = SEED_PARALLELIZATION(
            create_library.genes_txt_ch,
            complexity_ch.complexity,
            domain_importance_library.domain_importance_library_ch,
            params.fas_partitions
        )
        ch_versions = ch_versions.mix(SEED_PARALLELIZATION.out.versions)

        protein_pairs.protein_pairings_ch.view()
        protein_pairs.partition_ch.view()

        if (params.fas_partitions > 0) {
            input_fas = protein_pairs.partition_ch.flatten()
        } else {
            input_fas = protein_pairs.protein_pairings_ch.flatten()
        }

        input_fas.view()

        fas_scores = FAS_SCORING(
            input_fas,
            domain_importance_library.domain_importance_library_ch,
            anno_tools
            )

        ch_versions = ch_versions.mix(FAS_SCORING.out.versions)



        fas_scores_ch = fas_scores.fas_scored_directories.collect()

        merged_fas_scores = CONCAT_PROTEIN_PAIRS (
            create_library.genes_txt_ch,
            fas_scores_ch
        )
        ch_versions = ch_versions.mix(CONCAT_PROTEIN_PAIRS.out.versions)


        concatenated_fas_scores_library = CONCAT_GENES (
            merged_fas_scores.genes_directorys,
            domain_importance_library.domain_importance_library_ch,
            outdir
        )

        ch_versions = ch_versions.mix(CONCAT_GENES.out.versions)

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
