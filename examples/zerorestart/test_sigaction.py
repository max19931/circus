import os
import signal

import sigaction


def test_install_and_fire():
    pid = os.getpid()

    def handler(signo, ptr_info, extra):
        info = ptr_info[0]
        assert pid == info.si_pid
    sigaction.install(signal.SIGUSR2,
                      sigaction.SA_SIGINFO, handler)

    os.kill(pid, signal.SIGUSR2)

if __name__ == '__main__':
    test_install_and_fire()
