#!/bin/bash

ANALYSIS_CODE="rescale_simmon"
VERSION="2023.09.16-dev"
MOUNT_POINT="/program/${ANALYSIS_CODE}_${VERSION}"

# Using templates makes it easier to publish new versions without touching multiple files.
instantiate_template() {
    template_file=$1
    instance_file=$2
    cat $template_file | sed "s|%ANALYSIS_CODE%|$ANALYSIS_CODE|g" \
    | sed "s|%MOUNT_POINT%|$MOUNT_POINT|g" \
    | sed "s|%VERSION%|$VERSION|g" > $instance_file
}

instantiate_template settings.json-templ settings.json
instantiate_template spub_build.sh-templ spub_build.sh
instantiate_template spub_launch.sh-templ spub_launch.sh

# Prepare distribution zip.
mkdir dist
cp -R ../*.py ../requirements.txt ../assets ../plugins dist/
cp spub_launch.sh dist/
zip -r dist.zip dist/
rm -fr dist/

# Create Sandbox - files are uploaded. Capture Sandbox ID.
printf "0\n" | rescale-cli spub tile create -s settings.json |
while read -r line
do
    echo $line
    echo "$line" | grep -E '^.*--sandbox-id .*`.$'
    if [ $? -eq 0 ]
    then
        sandbox_id=$(echo "$line" | sed 's/.*--sandbox-id \(.*\)`./\1/')
    fi
done

# Capture SSH command for the Sandbox.
rescale-cli spub sandbox connect --sandbox-id $sandbox_id |
while read -r line
do
    echo "$line" | grep -E '^ssh.*$'
    if [ $? -eq 0 ]
    then
        ssh_command=$line
    fi
done

# Launch the build script on the Sandbox, via SSH.
ssh_cmd=`echo "$ssh_command" | sed 's/ssh/ssh -o \"StrictHostKeyChecking=no\"/g'`" \"cd work && . ./spub_build.sh\""
eval $ssh_cmd

# Sleep for 2 minutes (seems to help in solving the zero-size files issue)
sleep 60

# Publish tile.
printf "$ANALYSIS_CODE\n" | rescale-cli spub tile publish --sandbox-id $sandbox_id --visibility organization-private

# Clean up.
rm settings.json spub_build.sh spub_launch.sh dist.zip
