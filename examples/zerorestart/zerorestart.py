
import os
import sys
import time
import signal
import socket
import logging

import circus.exc
import circus.client

import sigaction


process = os.path.basename(sys.argv[0]) if sys.argv else '<unknown>'
logging.basicConfig(
        format='{0}[{1}]::%(levelname)s::%(asctime)s::%(name)s - %(message)s'
                .format(socket.gethostname(), process),
        level=logging.DEBUG
        )
logger = logging.getLogger(__name__)


circus = circus.client.CircusClient(timeout=30.0)


def pid_to_watcher(pid):
    pid = str(pid)
    try:
        stats = circus.send_message('stats')
    except circus.exc.CallError as e:
        logger.info(
                'Error getting watcher name for pid "{}": {}'.format(pid, e))
    else:
        for watcher, procs in stats.get('infos', {}).iteritems():
            if pid in procs and len(procs) == 2:
                return watcher


def stop_old_process(watcher):
    try:
        circus.send_message('decr', name=watcher)
    except circus.exc.CallError as e:
        logger.info('Error stopping old process for watcher "{}": {}'.format(
                watcher, e))


def signal_handler(signo, ptr_info, extra):
    pid = ptr_info[0].si_pid
    logger.info('Received signal from pid: {}'.format(pid))
    watcher = pid_to_watcher(pid)
    if watcher is not None:
        logger.info('Stopping old process for watcher "{}"'.format(watcher))
        stop_old_process(watcher)

sigaction.install(signal.SIGQUIT, sigaction.SA_SIGINFO,
                  signal_handler)


def run():
    while (True):
        time.sleep(1)


if __name__ == '__main__':
    run()
