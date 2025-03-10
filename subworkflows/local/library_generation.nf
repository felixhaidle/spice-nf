include { GENERATE_LIBRARY } from '../../modules/local/library/generate_library'
include { FAS_ANNOTATION } from '../../modules/local/library/generate_library'
include { GET_DOMAIN_IMPORTANCE } from '../../modules/local/library/generate_library'
include { RESTRUCTURE_ANNO } from '../../modules/local/library/generate_library'
include { FAS_SCORE_CALCULATION } from '../../modules/local/library/generate_library'
include { CONCAT_FAS_SCORES } from '../../modules/local/library/generate_library'
include { PARSE_DOMAIN_OUTPUT } from '../../modules/local/library/generate_library'
include { SEQUENCE_FILES } from '../../modules/local/library/setup_library'
include { CREATE_LIBRARY } from '../../modules/local/library/setup_library'
include { FILTER_LIBRARY } from '../../modules/local/library/setup_library'
include { FINISH_LIBRARY_INITIALIZATION } from '../../modules/local/library/setup_library'
include { GET_GENE_SIZE } from '../../modules/local/library/get_gene_size.nf'


workflow LIBRARY_GENERATION {

    take:
        species
        release
        anno_tools
        outdir
        test_mode
        annotation_gtf
        peptide_fasta

    main:

        sequence_files = SEQUENCE_FILES(
            species,
            release,
            test_mode,
            annotation_gtf,
            peptide_fasta
        )

        create_library = CREATE_LIBRARY(
            sequence_files.gtf_file,
            sequence_files.fasta_file,
            species,
            release
        )


        filter_library = FILTER_LIBRARY(
            create_library.library_dir
        )




        finished_library = FINISH_LIBRARY_INITIALIZATION(
            filter_library.filtered_library_dir
        )


        /*
        spice_library = GENERATE_LIBRARY(
            species,
            release,
            outdir,
            test_mode
        )
        */

        // Define the input for FAS_ANNOTATION based on test_mode
        // fasAnno_library_input = test_mode ? file("${projectDir}/tools/SPICE/test_data/Spice_Library/spice_lib_test_homo_sapiens_94_1ee") : finished_library.finished_library_dir
        fasAnno_library_input = finished_library.finished_library_dir

        annotated_library = FAS_ANNOTATION(
            anno_tools,
            fasAnno_library_input,


        )

        domain_importance_library = GET_DOMAIN_IMPORTANCE(
            annotated_library.annotated_library_ch

        )

        restructured_library = RESTRUCTURE_ANNO(
            domain_importance_library.domain_importance_library_ch

        )


        // Channel to read gene IDs from the file
        genes_ch = restructured_library.genes_txt_ch
            .splitText()
            .map { it.trim() }

        gene_ch_with_size = GET_GENE_SIZE(
            genes_ch,
            annotation_gtf
        )

        fas_scores = FAS_SCORE_CALCULATION(
            gene_ch_with_size,
            restructured_library.restructured_library_ch,
            anno_tools
            )



        fas_score_library = fas_scores.fas_scored_directories.collect()


        concatenated_fas_scores_library = CONCAT_FAS_SCORES (
            fas_score_library,
            restructured_library.restructured_library_ch
        )


        updated_library = concatenated_fas_scores_library.finished_library

        results_directory = PARSE_DOMAIN_OUTPUT(
            updated_library,
            outdir
        )

    emit:
        library = results_directory.spice_library_ch

}
