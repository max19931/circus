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
                    "name": "<watchername>",
                    "nb": <nbprocess>
                }
            }

        The response return the number of processes in the 'numprocesses`
        property::

            { "status": "ok", "numprocesses": <n>, "time", "timestamp" }

        Command line
        ------------

        ::

            $ circusctl incr <name> [<nbprocess>]

        Options
        +++++++

        - <name>: name of the watcher.
        - <nbprocess>: the number of processes to add.

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
            nb = props.get("nb", 1)
            return {"numprocesses": watcher.incr(nb)}

    def console_msg(self, msg):
        if msg.get("status") == "ok":
            if msg.get('upgradable') is False:
                return 'This watcher is not upgradable'
            else:
                return 'Upgrade successful'
        return self.console_error(msg)
