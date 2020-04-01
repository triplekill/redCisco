import abc


class AbstractCommand(metaclass=abc.ABCMeta):
    """Abstract Command Class"""

    @abc.abstractmethod
    async def main(self):
        """Coroutine initial command handler"""

    @abc.abstractmethod
    async def execute(self):
        """Coroutine to execute the command logic"""
