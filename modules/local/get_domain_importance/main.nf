process GET_DOMAIN_IMPORTANCE {
    executor 'local'
    cpus '1'

    input:
        path annotated_library // Path: Output from previous step


    output:
        path "${annotated_library}", emit: domain_importance_library_ch



    script:
    """

    get_domain_importance.py \
    -i "${annotated_library}/fas_data/annotations.json" \
    -o "${annotated_library}/fas_data/"

    restructure_anno.py \
    -i "${annotated_library}/fas_data/annotations.json" \
    -o "${annotated_library}/fas_data/architectures"
    """
}
