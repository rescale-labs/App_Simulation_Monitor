#!/bin/bash

# Using templates makes it easier to publish new versions without touching multiple files.
instantiate_template() {
    template_file=$1
    instance_file=$2
    cat $template_file |
        sed "s|%VERSION%|$VERSION|g" |
        sed "s|%MOUNT_POINT%|$MOUNT_POINT|g" |
        sed "s|%ANALYSIS_CODE%|$ANALYSIS_CODE|g" |
        sed "s|%JOB_ID%|$JOB_ID|g" |
        sed "s|%FULLY_SCOPED_DATE%|$FULLY_SCOPED_DATE|g" \
            >$instance_file
}

ANALYSIS_CODE=$1
VERSION=$2

MOUNT_POINT="/program/${ANALYSIS_CODE}_${VERSION}"
SRC_DIR="../.."

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
mv webapp_launch.sh setup_command.sh rescaleapp.service dist/

zip -r dist.zip dist/

JOB_ID=$(rescale-cli -q --profile us submit -e -i submit.sh | jq -r .id)
echo "Submitted Job: ${JOB_ID}"

echo "Uploading inputs..."
FILE_ID=$(
    curl -s -X POST \
        -H "Content-Type:multipart/form-data" \
        -H "Authorization: Token ${RESCALE_API_KEY}" \
        -F "file=@dist.zip" \
        https://platform.rescale.com/api/v2/files/contents/ |
        jq -r ".id"
)
echo "Uploaded file_id: ${FILE_ID}"

echo "Creating job"
instantiate_template submit.json-templ submit.json
JOB_ID=$(
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Token ${RESCALE_API_KEY}" \
        -d@submit.json \
        "https://platform.rescale.com/api/v2/jobs/" |
        jq -r '.id'
)

echo "Submitting job ${JOB_ID}"
curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Token ${RESCALE_API_KEY}" \
    "https://platform.rescale.com/api/v2/jobs/${JOB_ID}/submit/"

echo "Waiting for the build job to complete"
max_poll=180
poll_cnt=0
poll_wait=30

echo -n "Polling"
while [[ $poll_cnt -lt $max_poll ]]; do
    res=$(
        curl -s \
            -H "Authorization: Token ${RESCALE_API_KEY}" \
            "https://platform.rescale.com/api/v2/jobs/${JOB_ID}/statuses/" |
            jq '.results[] | select(.status == "Completed")'
    )

    echo $res

    if [[ ! -z ${res} ]]; then
        break
    fi

    poll_cnt=$((poll_cnt + 1))
    echo -n "."
    sleep $poll_wait
done

if [[ $(echo $res | jq -r '.statusReason') != "Completed successfully" ]]; then
    echo "Build job failed"
    exit 1
fi

rm bits_build.sh submit.sh create_install_bits.spec dist.zip jira.json
