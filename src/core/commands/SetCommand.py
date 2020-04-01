import asyncio

from src.core.classes.base.BaseCommand import BaseCommand
from src.core.registry.OptionRegistry import OptionRegistry, GlobalOptionRegistry


class SetCommand(BaseCommand):
    helper = {
        'name': ['set'],
        'help': 'By using set, you can change the global console or plugin options',
        'usage': 'set <key> <value>'
    }

    def __init__(self, command: str, print_queue: asyncio.Queue):
        super().__init__()
        self.command = command
        self.print_queue = print_queue
        self.global_options = OptionRegistry()

    async def main(self) -> None:
        """Class method to start the command logic"""
        await self.execute()

    async def execute(self) -> None:
        """Class method to execute the command logic"""
        if not GlobalOptionRegistry or len(self.command.split()) < 3:
            return
        __cmd_parts = self.command.split()
        if __cmd_parts[2] == '=':
            __cmd_parts.remove('=')
        if __cmd_parts[2] == '\"\"':
            __cmd_parts[2] = ''
        _, key, *value = tuple(__cmd_parts)
        self.global_options.set_registry_value(key, ' '.join(value))
