from circus.commands.base import Command
from circus.exc import ArgumentError
from circus.util import TransformableFuture

class Upgrade(Command):
    """\
        Perform a hot-upgrade of the named watcher
        ==============================================

        This command launches a 2nd process for an "upgradable" watcher.
        Upgradable processes are expected to obtain two important variables:
            1) the id of the file descriptor the 1st process is accept()'ing on
            2) the PID of the zerorestart process (also managed by circus)

        After the new process starts up and is ready to invoke accept() on the
        file descriptor that was passed in, the new process should send a
        SIGQUIT to the pid of the zerorestart process. zerorestart then invokes
        the circus command "decr" to terminate the 1st process. This will send
        a SIGTERM (by default) to the 1st process, which is expected to handle
        that signal by exiting cleanly before watcher.graceful_timeout (defaults
        to 30s). After graceful_timeout, circus sends a SIGKILL to forcibly quit
        the 1st process.

        ZMQ Message
        -----------

        ::

            {
                "command": "upgrade",
                "properties": {
                    "name": "<watchername>"
                }
            }

        The response contains the number of processes running for the watcher
        after performing the "incr" operation::

            { "status": "ok", "numprocesses": <n> }

        Command line
        ------------

        ::

            $ circusctl upgrade <name>

        Options
        +++++++

        - <name>: name of the watcher.

    """

    name = "upgrade"
    properties = ['name']

    def message(self, *args, **opts):
        if len(args) < 1:
            raise ArgumentError("number of arguments invalid")
        return self.make_message(name=args[0], command="upgrade")

    def execute(self, arbiter, props):
        watcher = self._get_watcher(arbiter, props.get('name'))

        # watcher must be configured as upgradble
        if not watcher.is_upgradable():
            return {"numprocesses": watcher.numprocesses, "upgradable": False}
        else:
            # no need to upgrade a watcher thats already stopped
            if watcher.is_stopped():
                return {'stopped': True}

            # cant do the upgrade file handle dance with > 1 process
            if watcher.numprocesses != 1:
                return {"numprocesses": watcher.numprocesses,
                        "toomanyprocesses": True}

            # start the new process. zerorestart.py will stop the old process
            resp = TransformableFuture()
            resp.set_upstream_future(watcher.incr(1))
            resp.set_transform_function(lambda x: {"numprocesses": x})
            return resp

    def console_msg(self, msg):
        if msg.get("status") == "ok":
            if msg.get('upgradable') is False:
                return 'This watcher is not upgradable'
            elif msg.get('stopped') is True:
                return 'Upgrade failed: watcher is stopped'
            elif msg.get("toomanyprocesses") is True:
                return ('Upgrade failed: can only upgrade when numprocesses=1, '
                        'but numprocesses={}'.format(msg.get('numprocesses')))
            else:
                return 'Upgrade successful'
        return self.console_error(msg)
