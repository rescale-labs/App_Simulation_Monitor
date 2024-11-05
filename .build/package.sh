#!/bin/bash

source shared.sh

ANALYSIS_CODE=$1
VERSION=$2
DIST_PATH=$3

MOUNT_POINT="/program/${ANALYSIS_CODE}_${VERSION}"
SRC_DIR=".."

# Using templates makes it easier to publish new versions without touching multiple files.
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

zip -r $DIST_PATH dist/
ls -al $DIST_PATH