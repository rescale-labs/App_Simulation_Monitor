PYTHON_VERSION=3.11

MOUNT_POINT="/program/rescale_simmon_lnx_2024.10.17"
VERSION="2024.10.17"

INSTALL_DIR=$MOUNT_POINT/$VERSION
mkdir -p $INSTALL_DIR
source /etc/profile.d/greeting.sh

wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $INSTALL_DIR/miniconda
eval "$(/${INSTALL_DIR}/miniconda/bin/conda shell.bash hook)"
rm ~/miniconda.sh

conda create -y --name RESCALE python=$PYTHON_VERSION
conda activate RESCALE

pip install --upgrade pip

if [ ! -d "dist" ]
then
    unzip dist.zip
fi

mv dist/rescale_simmon_lnx.png .

cp -R dist/* $INSTALL_DIR
pushd $INSTALL_DIR
pip install -r requirements.txt
chmod a+x *.sh
popd

rm -fr dist* *-templ

create_install_bits create_install_bits.spec << EOF
rescale_simmon_lnx_2024.10.17
EOF

cd $HOME/work
cp settings.json settings.json-orig
jq '.software.pngThumbnail = "rescale_simmon_lnx.png"' settings.json-orig > settings.json
rm settings.json-orig