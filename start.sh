#!/bin/bash
install_path=/opt/putsync2
log_path=/var/log/putsync2

mkdir -p "$log_path"

source "${install_path}/venv/bin/activate"
nohup python3 "${install_path}/src/main.py" "${install_path}/prod.ini" &> ${log_path}/putsync2.log &
echo $! >${log_path}/putsync2.pid