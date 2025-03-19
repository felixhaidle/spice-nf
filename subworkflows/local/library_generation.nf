include { FAS_ANNOTATION        } from '../../modules/local/fas_annotation'
include { GET_DOMAIN_IMPORTANCE } from '../../modules/local/get_domain_importance'
include { FAS_SCORE_CALCULATION } from '../../modules/local/fas_score_calculation'
include { CONCAT_FAS_SCORES     } from '../../modules/local/concat_fas_scores'
include { SEQUENCE_FILES        } from '../../modules/local/sequence_files'
include { CREATE_LIBRARY        } from '../../modules/local/create_library'


workflow LIBRARY_GENERATION {

    take:
        species
        release
        anno_tools
        outdir
        annotation_gtf
        peptide_fasta

    main:

        sequence_files = SEQUENCE_FILES(
            species,
            release,
            annotation_gtf,
            peptide_fasta
        )

        prefixes = channel.fromPath("${projectDir}/assets/ensembl_stable_id_prefixes.json")

        create_library = CREATE_LIBRARY(
            sequence_files.gtf_file,
            sequence_files.fasta_file,
            species,
            release,
            prefixes
        )

        annotated_library = FAS_ANNOTATION(
            anno_tools,
            create_library.library_dir
        )

        domain_importance_library = GET_DOMAIN_IMPORTANCE(
            annotated_library.annotated_library_ch
        )

        // Channel to read gene IDs and resource requirements from the file genes.txt
        genes_ch = create_library.genes_txt_ch
        .splitText()
        .map { it.trim().split(' ') }
        .map { tuple(it[0], it[1]) }

        fas_scores = FAS_SCORE_CALCULATION(
            genes_ch,
            domain_importance_library.domain_importance_library_ch,
            anno_tools
            )

        fas_score_library = fas_scores.fas_scored_directories.collect()

        concatenated_fas_scores_library = CONCAT_FAS_SCORES (
            fas_score_library,
            domain_importance_library.domain_importance_library_ch,
            outdir
        )

    emit:
        library = concatenated_fas_scores_library.finished_library

}
