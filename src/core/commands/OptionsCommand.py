import asyncio
import textwrap

from src.core.utilities.Colors import *
from src.core.utilities.Tables import *

# noinspection PyUnresolvedReferences
from src.core.classes.base.BaseCommand import BaseCommand
from src.core.registry.OptionRegistry import GlobalOptionRegistry, OptionRegistry


class OptionsCommand(BaseCommand):
    helper = {
        'name': ['options'],
        'help': 'Prints the available console or plugin options',
        'usage': 'options'
    }

    def __init__(self, command: str, print_queue: asyncio.Queue):
        super().__init__()
        self.command = command
        self.print_queue = print_queue
        self.global_options = OptionRegistry()

    async def main(self) -> None:
        """Class coroutine for bootstrapping command"""
        await self.execute()

    async def execute(self) -> None:
        """Class coroutine to execute the command logic"""
        options = self.global_options.get_registry_dict()
        pq = self.print_queue
        for ns in options.keys():
            await pq.put(f"{bold}{r}{ns}\n{r}{'=' * len(ns)}{reset}")
            field_names = [f'{bold}{"Option Name":<26}', f'{"Current Setting":<30}', f'{"Description":<30}{reset}']
            field_values = []
            for item in options[ns].items():
                __current_setting = item[1][0]
                if len(__current_setting) > 70:
                    __current_setting = textwrap.fill(item[1][0])
                field_values.append([item[0], __current_setting, item[1][1]])
            output = generate_table(field_names, field_values)
            await self.print_queue.put(output)
            await self.print_queue.put('')

