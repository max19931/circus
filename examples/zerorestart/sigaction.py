import ctypes

from ctypes_configure import configure


libc = ctypes.CDLL(None)


class siginfo_t(ctypes.Structure):
    pass


sa_sigaction_t = ctypes.CFUNCTYPE(None,
                                  ctypes.c_int,
                                  ctypes.POINTER(siginfo_t),
                                  ctypes.c_void_p)


class _CConfigure:
    _compilation_info_ = configure.ExternalCompilationInfo(
        includes=['signal.h', 'sys/types.h', 'unistd.h'],
    )

    pid_t = configure.SimpleType('pid_t', ctypes.c_int)

    SA_SIGINFO = configure.ConstantInteger('SA_SIGINFO')

    struct_sigaction = configure.Struct('struct sigaction', [
        ('sa_flags', ctypes.c_int),
        ('sa_sigaction', sa_sigaction_t)
    ])

    siginfo_t = configure.Struct('siginfo_t', [
        ('si_pid', ctypes.c_int),
    ])

_info = configure.configure(_CConfigure)

pid_t = _info['pid_t']
struct_sigaction = _info['struct_sigaction']
siginfo_t._fields_ = _info['siginfo_t']._fields_
SA_SIGINFO = _info['SA_SIGINFO']

sigaction = libc.sigaction
sigaction.argtypes = [ctypes.c_int,
                      ctypes.POINTER(struct_sigaction),
                      ctypes.POINTER(struct_sigaction)]
sigaction.restype = ctypes.c_int


def install(signo, sa_flags, handler):
    """
    Convenience function to install a sigaction() handler
    """
    action = struct_sigaction()
    action.sa_flags = SA_SIGINFO
    action.sa_sigaction = sa_sigaction_t(handler)
    return sigaction(signo, ctypes.pointer(action), None)
