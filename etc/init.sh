#!/bin/sh

PORT=13711
LOG=/var/log/mosecom-air/mosecom-air.log
DESC='Mosecom air web service'
NAME=mosecom-air
PIDFILE=/var/run/mosecom-air/${NAME}.pid
DAEMON=/usr/bin/python
MANAGE=/usr/bin/mosecom-air-manage
DAEMON_ARGS="${MANAGE} runfcgi method=prefork host=127.0.0.1 port=$PORT \
    pidfile=${PIDFILE} outlog=${LOG} errlog=${LOG}"
SCRIPTNAME=/etc/init.d/${NAME}
PATH=/sbin:/usr/sbin:/bin:/usr/bin

. /lib/init/vars.sh
. /lib/lsb/init-functions

do_start() {
    ps aux | fgrep ${DAEMON} | fgrep ${MANAGE} > /dev/null 2>&1 && return 1
    start-stop-daemon --start --quiet --pidfile ${PIDFILE} --chuid ${NAME} \
        --exec ${DAEMON} ${DAEMON_ARGS} || return 2
}

do_stop() {
    ps aux | fgrep ${DAEMON} | fgrep ${MANAGE} > /dev/null 2>&1 || return 1
    killproc -p ${PIDFILE}
    ps aux | fgrep ${DAEMON} | fgrep ${MANAGE} > /dev/null 2>&1 && return 2
    rm -f ${PIDFILE}
}

case "$1" in
    start)
        log_daemon_msg "Starting $DESC" "${NAME}"
        do_start
        case "$?" in
            0|1) log_end_msg 0 ;;
            2) log_end_msg 1 ;;
        esac
        ;;
    stop)
        log_daemon_msg "Stopping $DESC" "${NAME}"
        do_stop
        case "$?" in
            0|1) log_end_msg 0 ;;
            2) log_end_msg 1 ;;
        esac
        ;;
    status)
        status_of_proc "${DAEMON}" "${NAME}" && exit 0 || exit $?
        ;;
    restart)
        log_daemon_msg "Restarting $DESC" "${NAME}"
        do_stop
        case "$?" in
            0|1)
                do_start
                case "$?" in
                    0) log_end_msg 0 ;;
                    1) log_end_msg 1 ;;
                    *) log_end_msg 1 ;;
                esac
                ;;
            *)
                log_end_msg 1
                ;;
        esac
        ;;
    *)
        echo "Usage: ${SCRIPTNAME} {start|stop|status|restart}" >&2
        exit 3
        ;;
esac
