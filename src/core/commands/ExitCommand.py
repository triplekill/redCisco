import asyncio

from src.core.classes.base.BaseCommand import BaseCommand


class ExitCommand(BaseCommand):
    helper = {
        'name': ['exit', 'quit'],
        'help': 'This command will exit the redCisco application',
        'usage': 'exit'
    }

    def __init__(self, command: str, print_queue: asyncio.Queue):
        super().__init__()
        self.command = command
        self.print_queue = print_queue

    async def main(self) -> None:
        """Class method to start the command logic"""
        raise EOFError

    async def execute(self) -> None:
        """Class method to execute the command logic"""
        pass
