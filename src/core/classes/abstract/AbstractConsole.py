import abc


class AbstractConsole(metaclass=abc.ABCMeta):
    """Abstract Console Class"""

    @abc.abstractmethod
    def register(self):
        """Class method to register options with a registry"""

    @abc.abstractmethod
    async def interactive_shell(self):
        """Coroutine to start the interactive shell"""

    @abc.abstractmethod
    async def command_interpreter(self, command):
        """Coroutine to start the command interpreter"""

    @abc.abstractmethod
    async def print_processor(self):
        """Coroutine to process print jobs sent to print queue"""

    @abc.abstractmethod
    async def main(self):
        """Coroutine to star the main event loop"""
