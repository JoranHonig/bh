from click import command
from rich.console import Console
from rich.table import Table

from bountyhunter.immunefi.dataprovider import ImmunefiDataProvider


@command(help="List bug bounty programmes")
def list():
    immunefi_data_provider = ImmunefiDataProvider()
    programs = immunefi_data_provider.get_immunefi_programs()

    console = Console()
    # print rich table of programs
    # project name | max bounty |

    table = Table()

    table.add_column("Project", justify="left")
    table.add_column("Max Bounty", justify="right")

    for program in programs:
        maximum_reward = program.get('maximum_reward')
        human_readable_max_reward = f"${maximum_reward:,}"

        table.add_row(program.get('project'), human_readable_max_reward)

    console.print(table)
