from circus.commands.base import Command
from circus.exc import ArgumentError


class Upgrade(Command):
    """\
        Increment the number of processes in a watcher
        ==============================================

        This comment increment the number of processes in a watcher by +1.

        ZMQ Message
        -----------

        ::

            {
                "command": "incr",
                "properties": {
                    "name": "<watchername>"
                }
            }

        The response return the number of processes in the 'numprocesses`
        property::

            { "status": "ok", "numprocesses": <n>, "time", "timestamp" }

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
        if watcher.upgradable is False:
            return {"numprocesses": watcher.numprocesses, "upgradable": False}
        else:
            if watcher.numprocesses != 1:
                return {"numprocesses": watcher.numprocesses,
                        "toomanyprocesses": True}
            return {"numprocesses": watcher.incr(1)}

    def console_msg(self, msg):
        if msg.get("status") == "ok":
            if msg.get('upgradable') is False:
                return 'This watcher is not upgradable'
            elif msg.get("toomanyprocesses") is True:
                return ('Upgrade failed: there are too many '
                        'processes running for this watcher')
            else:
                return 'Upgrade successful'
        return self.console_error(msg)
