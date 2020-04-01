from src.core.classes.abstract.AbstractCommand import AbstractCommand
from src.core.registry.CommandRegistry import CommandRegistry, GlobalCommandRegistry


class BaseCommand(AbstractCommand):
    """Base Command Class"""
    helper = {}

    def __init_subclass__(cls, **kwargs) -> None:
        """Auto-register command classes on creation"""

        """
        :param cls:         Class to register
        :param kwargs:      Possible keyword arguments
        :type cls:          baseCommand class
        :type kwargs:       dict
        :return:            None
        """
        try:
            assert isinstance(cls, type(BaseCommand))
            if cls not in GlobalCommandRegistry:
                CommandRegistry(cls)
            super().__init_subclass__(**kwargs)
        except AssertionError:
            pass

    def __init__(self) -> None:
        self.options = {}

    async def main(self) -> None:
        """Coroutine handler to start command process"""

        """
        :return:            None
        """
        pass

    async def execute(self) -> None:
        """Coroutine to execute the command logic"""

        """
        :return:            None
        """
        pass
