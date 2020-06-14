"""Module for defining client commands."""


# =============================================================================
# >> CLASSES
# =============================================================================
class CommandHandler:
    """Class for validating and handling client commands."""

    __instance = None

    def instance():
        """Singleton instance"""
        if CommandHandler.__instance is None:
            CommandHandler()
        return CommandHandler.__instance

    def __init__(self):
        if CommandHandler.__instance is not None:
            raise Exception("This class is a singleton, use .instance() access method.")

        self.command_list = []
        self.prefix = ["/", "!"]

        CommandHandler.__instance = self

    def add_command(
        self,
        name,
        callback,
        alias=[],
        args=[],
        flags=[],
        disallowed_states=[],
        description="",
        usage="",
        prefix_required=True,
        log=False,
        visibility=0,
    ):
        """Register a new command."""
        command = Command(
            name,
            callback,
            alias,
            args,
            flags,
            disallowed_states,
            description,
            usage,
            prefix_required,
            log,
            visibility,
        )
        self.command_list.append(command)
        print(f"[deepsurf] Registered command: '{command.name}'")

    def execute_command(self, command, player, args):
        """Execute command."""

        required_args = 0
        for arg in command.args:
            if arg.required:
                required_args += 1

        if len(args) < required_args:
            return "Usage: " + command.usage

        for i in range(0, len(command.args)):
            try:
                arg = args[i]
            except IndexError:
                arg = None
            if not command.args[i].validate(arg):
                return (
                    f"Invalid argument {arg}, must be type {command.args[i].arg_type}"
                )

        if not player:
            return

        return command.callback(player, command)

    def check_command(self, message, player):
        # Message should be "<prefix><command> *args"
        message = message.split()
        command = message[0]
        try:
            args = message[1:]
        except IndexError:
            args = []

        command = self.get_command(command)
        if command is None:
            return

        return self.execute_command(command, player, args)

    def get_command(self, message):
        for cmd in self.command_list:
            if cmd.name == message:
                return cmd
            for alias in cmd.alias:
                if alias == message:
                    return cmd
        return None


class Command:
    """Class for defining new commands."""

    def __init__(
        self,
        name,
        callback,
        alias,
        args,
        flags,
        disallowed_states,
        description,
        usage,
        prefix_required,
        log,
        visibility,
    ):
        self.name = name
        self.callback = callback
        self.alias = alias

        # Arguments
        self.args = args

        # Response to incorrect command args
        self.usage = usage

        # Elaborate explanation of a command (potentially !help <command>)
        self.description = description

        # If command can be used without any prefix
        self.prefix_required = prefix_required

        # If command should be logged
        self.log = log

        # Who the response should be visible to (person who used it, admin, everyone)
        self.visibility = visibility


class Argument:
    """Class for defining and validating command arguments."""

    def __init__(self, arg_type, required, default):
        assert arg_type in [str, bool, int, float]
        self.arg_type = arg_type
        self.required = required
        self.value = default

    def validate(self, arg):
        """Validate passed argument"""

        try:
            self.value = self.arg_type(arg)
        except (ValueError, TypeError):
            self.value = None

        return not (self.value is None and self.required)
