#!/bin/bash

CREATE_TASK=true
JIRA_USER=bdobrzelecki@rescale.com

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

ANALYSIS_CODE="rescale_simmon"
VERSION=$(date +"%Y.%m.%d")
MOUNT_POINT="/program/${ANALYSIS_CODE}_${VERSION}"

instantiate_template bits_build.sh-templ bits_build.sh
instantiate_template submit.sh-templ submit.sh
instantiate_template create_install_bits.spec-templ create_install_bits.spec
instantiate_template webapp_launch.sh-templ webapp_launch.sh
instantiate_template setup_command.sh-templ setup_command.sh
instantiate_template rescaleapp.service-templ rescaleapp.service

find ../plugins | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
mkdir dist
cp -R ../*.py ../requirements.txt ../assets ../plugins ${ANALYSIS_CODE}.png dist/
mv webapp_launch.sh setup_command.sh rescaleapp.service dist/
zip -r dist.zip dist/
rm -fr dist/

JOB_ID=$(rescale-cli -q --profile us submit -e -i submit.sh | jq -r .id)
echo "Submitted Job: ${JOB_ID}"

if [ $CREATE_TASK = true ]; then
    # Share job
    APIKEY=$(python3 -c "import configparser; c = configparser.ConfigParser(); c.read('${HOME}/.config/rescale/apiconfig'); print(c['us']['apikey'])")
    curl -X POST "https://platform.rescale.com/api/v3/jobs/${JOB_ID}/share/" \
        -H "Content-Type: application/json" \
        -H "Authorization: Token ${APIKEY}" \
        -d '{"account":"04-038224927","message":""}'

    # Create jira
    FULLY_SCOPED_DATE=$(date +"%Y-%m-%d")

    JIRA_USER=$(python3 -c "import configparser; c = configparser.ConfigParser(); c.read('${HOME}/.config/jira/apiconfig'); print(c['jira']['user'])")
    JIRA_APIKEY=$(python3 -c "import configparser; c = configparser.ConfigParser(); c.read('${HOME}/.config/jira/apiconfig'); print(c['jira']['apikey'])")

    instantiate_template jira.json-template jira.json

    echo $JIRA_USER:$JIRA_APIKEY

    curl -X POST https://rescale.atlassian.net/rest/api/3/issue \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -u "$JIRA_USER:$JIRA_APIKEY" \
        -d @jira.json
fi

rm bits_build.sh submit.sh create_install_bits.spec dist.zip jira.json
