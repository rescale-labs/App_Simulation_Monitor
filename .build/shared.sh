instantiate_template() {
    template_file=$1
    instance_file=$2

    cat $template_file |
        sed "s|%VERSION%|$VERSION|g" |
        sed "s|%MOUNT_POINT%|$MOUNT_POINT|g" |
        sed "s|%ANALYSIS_CODE%|$ANALYSIS_CODE|g" |
        sed "s|%FILE_ID%|$FILE_ID|g" |
        sed "s|%JOB_ID%|$JOB_ID|g" |
        sed "s|%FULLY_SCOPED_DATE%|$FULLY_SCOPED_DATE|g" \
            > $instance_file
}