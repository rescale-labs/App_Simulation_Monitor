#!/bin/bash

# Using templates makes it easier to publish new versions without touching multiple files.
instantiate_template() {
    template_file=$1
    instance_file=$2
    cat $template_file \
    | sed "s|%VERSION%|$VERSION|g" \
    | sed "s|%MOUNT_POINT%|$MOUNT_POINT|g" \
    | sed "s|%ANALYSIS_CODE%|$ANALYSIS_CODE|g" \
    > $instance_file
}

ANALYSIS_CODE="rescale_simmon"
VERSION="2023.12.11"
MOUNT_POINT="/program/${ANALYSIS_CODE}_${VERSION}"

instantiate_template bits_build.sh-templ bits_build.sh
instantiate_template submit.sh-templ submit.sh
instantiate_template create_install_bits.spec-templ create_install_bits.spec
instantiate_template webapp_launch.sh-templ webapp_launch.sh
instantiate_template setup_command.sh-templ setup_command.sh

find ../plugins | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
mkdir dist
cp -R ../*.py ../requirements.txt ../assets ../plugins pngThumbnail.png dist/
mv webapp_launch.sh setup_command.sh dist/
zip -r dist.zip dist/
rm -fr dist/

rescale-cli --profile us submit -i submit.sh

rm bits_build.sh submit.sh create_install_bits.spec dist.zip