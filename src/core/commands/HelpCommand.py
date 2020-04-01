import asyncio

from src.core.utilities.Colors import *
from src.core.utilities.Tables import *

from src.core.classes.base.BaseCommand import BaseCommand

from src.core.registry.CommandRegistry import GlobalCommandRegistry


class HelpCommand(BaseCommand):
    helper = {
        'name': ['help'],
        'help': 'This command prints the help for all or a specific command',
        'usage': 'help, help <command>'
    }

    def __init__(self, command: str, print_queue: asyncio.Queue):
        super().__init__()
        self.command = command
        self.print_queue = print_queue

    async def main(self) -> None:
        """Class method to start the command logic"""
        await self.execute()

    async def execute(self) -> None:
        """Class method to execute the command logic"""
        if len(self.command.split()) >= 2:
            await self.help_command(self.command.split()[1])
        else:
            await self.help()

    async def help(self):
        if not GlobalCommandRegistry:
            return
        await self.print_queue.put(f"\n{bold}{r}Core Commands:\n{r}{'=' * 14}{reset}")
        field_names = [f'{bold}Command', f'Description', f'Usage{reset}']
        field_values = []
        for cls in GlobalCommandRegistry:
            info = GlobalCommandRegistry[cls].helper
            field_values.append([', '.join(info['name']), info['help'], info['usage']])
        output = generate_table(field_names, field_values)
        await self.print_queue.put(output + '\n')

    async def help_command(self, command: str):
        if not GlobalCommandRegistry:
            return
        field_names = [f'{bold}Command', f'Description', f'Usage{reset}']
        field_values = []
        for cls in GlobalCommandRegistry:
            if command in GlobalCommandRegistry[cls].helper['name']:
                await self.print_queue.put(f"\n{bold}Core Commands:\n{'=' * 14}{reset}")
                info = GlobalCommandRegistry[cls].helper
                field_values.append([', '.join(info['name']), info['help'], info['usage']])
        if not field_values:
            return
        output = generate_table(field_names, field_values)
        await self.print_queue.put(output + '\n')
