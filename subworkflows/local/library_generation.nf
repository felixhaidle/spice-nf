include { GENERATE_LIBRARY } from '../../modules/local/library/generate_library'
include { FAS_ANNOTATION } from '../../modules/local/library/generate_library'
include { GET_DOMAIN_IMPORTANCE } from '../../modules/local/library/generate_library'
include { RESTRUCTURE_ANNO } from '../../modules/local/library/generate_library'
include { FAS_SCORE_CALCULATION } from '../../modules/local/library/generate_library'


workflow LIBRARY_GENERATION {

    take:
        species
        release
        anno_tools
        outdir
        test_mode

    main:

        spice_library = GENERATE_LIBRARY(
            species,
            release,
            outdir,
            test_mode
        )

        // Define the input for FAS_ANNOTATION based on test_mode
        fasAnno_library_input = test_mode ? file("${projectDir}/tools/SPICE/test_data/Spice_Library/spice_lib_test_homo_sapiens_94_1ee") : spice_library.library_ch

        annotated_library = FAS_ANNOTATION(
            anno_tools,
            fasAnno_library_input,
            test_mode,
            outdir
        )

        domain_importance_library = GET_DOMAIN_IMPORTANCE(
            annotated_library.annotated_library_ch,
            outdir
        )

        restructured_library = RESTRUCTURE_ANNO(
            domain_importance_library.domain_importance_library_ch,
            outdir
        )
      

        // Channel to read gene IDs from the file
        genes_ch = restructured_library.genes_txt_ch
            .splitText()
            .map { it.trim() }
        

        test = FAS_SCORE_CALCULATION(
            genes_ch,
            domain_importance_library.domain_importance_library_ch,
            outdir
            )
        test.gene_tsv_ch.view()

        // Result collection step
        /* Collect the outputs after all parallel processes are complete
        FAS_RESULT_COLLECTION(
            spice_library = domain_importance_library.domain_importance_library_ch,
            outdir = outdir,
            gene_tsv_ch = gene_results.gene_tsv_ch.collect()
        )
        */

    emit:
        library = restructured_library.restructured_library_ch
        
}
