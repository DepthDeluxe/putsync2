#!/bin/bash
HOST=jud@192.168.77.248
SSH_OPTIONS="-o PreferredAuthentications=password -o PubkeyAuthentication=no"

mkdir -p build/

tar -czvf build/putsync2.tar.gz src/ prod.ini dev.ini requirements.txt start.sh putsync2

scp ${SSH_OPTIONS} build/putsync2.tar.gz ${HOST}:./

deploy_commands="\"
    rm -rf /opt/putsync2/* &&
    tar -xf putsync2.tar.gz -C /opt/putsync2 &&
    cp /opt/putsync2/putsync2 /etc/init.d/putsync2 &&
    cd /opt/putsync2 &&
    virtualenv --python=/usr/local/bin/python3.6 ./venv &&
    source ./venv/bin/activate &&
    pip install -r ./requirements.txt &&
    deactivate
\""
ssh -t ${SSH_OPTIONS} ${HOST} sudo /bin/bash -c "$deploy_commands"