#!/bin/bash
install_path=/opt/putsync2
log_path=/var/log/putsync2

start_putsync2() {
    ${install_path}/putsync2.pex ${intall_path}/prod.ini
}
stop_putsync2() {
    pid=$(get_putsync2_pid)
    kill ${pid}
}
restart_putsync2() {
    stop_putsync2
    start_putsync2
}
status_putsync2() {
    pid=$(get_putsync2_pid)
    if [ -z ${pid} ]; then
        if kill -0 ${pid}; then
            echo "Putsync2 is running... pid ${pid}"
        else
            exit 0
        fi
    else
        echo "Putsync2 is not running"
        exit 1
    fi
}
get_putsync2_pid() {
    if [ -f ${log_path}/putsync2.pid ]; then
        cat ${log_path}/putsync2.pid
    fi
}

case $1 in
    start)
        ;;
    stop)
        ;;
    restart)
        ;;
    status)
        ;;
esac
