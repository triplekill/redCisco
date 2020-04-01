from src.core.classes.abstract.AbstractConsole import AbstractConsole


class BaseConsole(AbstractConsole):
    """Abstract Console Class"""

    def __init__(self) -> None:
        self.options = {}

    def register(self) -> None:
        """Class method to register options with a registry"""

        """
        :return:            None
        """
        pass

    async def interactive_shell(self) -> None:
        """Coroutine to start the interactive shell"""

        """
        :return:            None
        """
        pass

    async def command_interpreter(self, command: str) -> None:
        """Coroutine to start the command interpreter"""

        """
        :param command:     command
        :type command:      str
        :return:            None
        """
        pass

    async def print_processor(self) -> None:
        """Coroutine to process print jobs sent to print queue"""

        """
        :return:            None
        """
        pass

    async def main(self) -> None:
        """Coroutine to star the main event loop"""

        """
        :return:            None
        """
        pass
