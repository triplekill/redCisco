import asyncio
import json

from src.core.classes.base.BaseConsole import BaseConsole

from src.core.registry.OptionRegistry import OptionRegistry
from src.core.registry.CommandRegistry import GlobalCommandRegistry

# noinspection PyUnresolvedReferences
from src.core.commands import *

# noinspection PyUnresolvedReferences
from src.core.utilities.Colors import *

from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.styles import Style

style = Style.from_dict({"prompt": "ansired bold", "rprompt": "ansigreen"})


class RedCisco(BaseConsole):
    def __init__(self):
        super().__init__()
        self.print_queue = asyncio.Queue()
        self.config_file = "src/core/config/console.JSON"
        self.global_options = OptionRegistry()

    def register(self) -> None:
        """Class method to register the JSON options within GlobalOptionRegistry"""
        with open(self.config_file) as f:
            try:
                self.options = json.loads(f.read())
                self.global_options.register_options(self.options)
            except json.decoder.JSONDecodeError:
                print(f"Error: Unable to decode '{self.config_file} - Exiting'\n")
                exit()

    async def interactive_shell(self) -> None:
        """Class method to execute the interactive shell"""
        session = PromptSession()
        while True:
            try:
                result = await session.prompt_async(f"redCisco> ", style=style)
                if not result:
                    continue
                await self.command_interpreter(str(result).strip())
            except (EOFError, KeyboardInterrupt):
                break

    async def command_interpreter(self, command: str) -> None:
        """Class method to process the user-supplied commands at the prompt"""
        for cls in GlobalCommandRegistry:
            if not asyncio.iscoroutinefunction(GlobalCommandRegistry[cls].main):
                continue
            if command.startswith(tuple(GlobalCommandRegistry[cls].helper['name'])):
                result = await asyncio.gather(GlobalCommandRegistry[cls](command, self.print_queue).main())
                if result is False:
                    print("Result is false?!")
                    raise KeyboardInterrupt

    async def print_processor(self) -> None:
        """Class method to handle the print processing of the redCisco application"""
        try:
            while True:
                while self.print_queue.empty() is not True:
                    stub = await self.print_queue.get()
                    if isinstance(stub, str):
                        print(stub)
                    elif isinstance(stub, tuple):
                        if stub[0] == "error":
                            print(f"{r}{stub[1]}{reset}")
                        elif stub[0] == "warning":
                            print(f"{y}{stub[1]}{reset}")
                        elif stub[0] == "success":
                            print(f"{g}{stub[1]}{reset}")
                        elif stub[0] == "bold":
                            print(f"{bold}{stub[1]}{reset}")
                        else:
                            print(f"{stub[1]}")
                    self.print_queue.task_done()
                await asyncio.sleep(0.002)
        except asyncio.CancelledError:
            print('Closing the RedCisco application... Cleaning up running tasks...\n')

    async def main(self) -> None:
        """Class method to start the redCisco application"""
        self.register()
        with patch_stdout():
            print_task = asyncio.create_task(self.print_processor())
            try:
                await self.interactive_shell()
            finally:
                print_task.cancel()
