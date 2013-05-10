from circus.commands.base import Command
from circus.exc import ArgumentError


class Status(Command):
    """\
        Get the status of a watcher or all watchers
        ===========================================

        This command start get the status of a watcher or all watchers.

        ZMQ Message
        -----------

        ::

            {
                "command": "status",
                "properties": {
                    "name": '<name>",
                }
            }

        The response return the status "active" or "stopped" or the
        status / watchers.


        Command line
        ------------

        ::

            $ circusctl status [<name>]

        Options
        +++++++

        - <name>: name of the watcher

        Example
        +++++++

        ::

            $ circusctl status dummy
            active
            $ circusctl status
            dummy: active
            dummy2: active
            refuge: active

    """

    name = "status"

    def message(self, *args, **opts):
        if len(args) > 1:
            raise ArgumentError("message invalid")

        if len(args) == 1:
            return self.make_message(name=args[0])
        else:
            return self.make_message()

    def execute(self, arbiter, props):
        if 'name' in props:
            watcher = self._get_watcher(arbiter, props['name'])
            return {"status": watcher.status()}
        else:
            return {"statuses": arbiter.statuses()}

    def console_msg(self, msg):
        if "statuses" in msg:
            statuses = msg.get("statuses")
            watchers = sorted(statuses)
            watcher_format = '{name}: {status}'
            formatted = []
            for watcher in watchers:
                watcher_status, processes = self._format_status(
                    statuses[watcher]
                )
                if watcher_status == 'stopped':
                    s = watcher_status
                else:
                    s = '{}\n{}'.format(watcher_status, processes)

                formatted.append(watcher_format.format(
                    name=watcher,
                    status=s,
                ))

            return '\n'.join(formatted)
        elif "status" in msg and "status" != "error":
            status = msg.get('status')
            watcher_status, processes = self._format_status(status)
            if watcher_status == 'stopped':
                return watcher_status
            else:
                return '{status}:\n{processes}'.format(
                    status=watcher_status,
                    processes=processes,
                )

        return self.console_error(msg)

    def _format_status(self, status_dict):
        watcher_status = status_dict['watcher']
        process_dicts = status_dict['processes']
        process_format = '\tpid: {pid} {status} uptime: {uptime}'
        process_statuses = '\n'.join(
            process_format.format(**process)
            for process in process_dicts
        )
        return watcher_status, process_statuses
