import asyncio

from src.core.utilities.Colors import *
from src.core.RedCisco import RedCisco


def heading():
    print(f"""

{r}██████╗ ███████╗██████╗ {reset} ██████╗██╗███████╗ ██████╗ ██████╗ 
{r}██╔══██╗██╔════╝██╔══██╗{reset}██╔════╝██║██╔════╝██╔════╝██╔═══██╗
{r}██████╔╝█████╗  ██║  ██║{reset}██║     ██║███████╗██║     ██║   ██║
{r}██╔══██╗██╔══╝  ██║  ██║{reset}██║     ██║╚════██║██║     ██║   ██║
{r}██║  ██║███████╗██████╔╝{reset}╚██████╗██║███████║╚██████╗╚██████╔╝
{r}╚═╝  ╚═╝╚══════╝╚═════╝ {reset} ╚═════╝╚═╝╚══════╝ ╚═════╝ ╚═════╝ 

{bold}{r}[*] Author:    d3d (@MaliciousGroup){reset}
{bold}{r}[*] Donate:    bc1qd5f7krnpf5j2zth0nytk979nu7yyhfnjj8x405{reset}
""")


if __name__ == "__main__":
    console = RedCisco()
    heading()
    try:
        asyncio.run(console.main())
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
