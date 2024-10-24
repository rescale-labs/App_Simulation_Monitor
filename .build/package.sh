#!/bin/bash

# Using templates makes it easier to publish new versions without touching multiple files.
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

ANALYSIS_CODE=$1
VERSION=$2
SHARE_WITH_HPC=$3

MOUNT_POINT="/program/${ANALYSIS_CODE}_${VERSION}"
SRC_DIR=".."

instantiate_template bits_build.sh-templ bits_build.sh
instantiate_template submit.json-templ submit.json
instantiate_template create_install_bits.spec-templ create_install_bits.spec
instantiate_template webapp_launch.sh-templ webapp_launch.sh
instantiate_template setup_command.sh-templ setup_command.sh
instantiate_template rescaleapp.service-templ rescaleapp.service

find $SRC_DIR/plugins | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

rm -fr dist
mkdir dist

cp -R $SRC_DIR/*.py $SRC_DIR/requirements.txt $SRC_DIR/assets $SRC_DIR/plugins ${ANALYSIS_CODE}-pngThumbnail.png dist/
cp _ibt_tools_lnx/* dist/
mv bits_build.sh webapp_launch.sh create_install_bits.spec setup_command.sh rescaleapp.service dist/

mkdir ~/build
zip -r ~/build/dist.zip dist/
