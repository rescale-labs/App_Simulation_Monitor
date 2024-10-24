#!/bin/bash

. shared.sh

DIST_PATH=$1
SHARE_WITH_HPC=$2

echo "Uploading inputs..."
FILE_ID=$(
    curl -s -X POST \
        -H "Content-Type:multipart/form-data" \
        -H "Authorization: Token ${RESCALE_API_KEY}" \
        -F "file=@${DIST_PATH}" \
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

if [[ "$SHARE_WITH_HPC" == "true" && -n "$JOB_ID" ]]; then
    # Share job
    curl -X POST "https://platform.rescale.com/api/v3/jobs/${JOB_ID}/share/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Token ${RESCALE_API_KEY}" \
        -d '{"account":"04-038224927","message":""}'
fi
