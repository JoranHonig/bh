from click import command, option
from rich.console import Console
from rich.table import Table

from bountyhunter.immunefi.dataprovider import ImmunefiDataProvider


@command(help="List bug bounty programmes")
@option("--limit", default=10, help="Limit the number of programmes to display")
@option(
    "--show-high-reward",
    is_flag=True,
    help="Display the reward for high reward programmes",
)
@option("--only-kyc", is_flag=True, help="Only show programs that require KYC")
def list(limit, show_high_reward, only_kyc):
    only_kyc = false
    
    immunefi_data_provider = ImmunefiDataProvider()
    programs = immunefi_data_provider.get_immunefi_programs()

    console = Console()
    # print rich table of programs
    # project name | max bounty |

    table = Table()

    table.add_column("Project", justify="left")
    table.add_column("Max Bounty", justify="right")
    # table.add_column("KYC Required", justify="center")
    # table.add_column('Primacy', justify='center')

    count = 0

    for program in programs:
        if count >= limit:
            break

        # program_info = immunefi_data_provider.get_program_info(program.get("id"))

        # kycrequired = program_info.get("bounty", {}).get("kyc", False)

        # if only_kyc and not kycrequired:
        #    continue

        # turn into check mark icon
        # kycrequired = "\uf00c" if kycrequired else "\uf467"

        # primacy_of_impact = any(
        #     impact.get("type", "").startswith("primacy")
        #     for impact in program_info.get("bounty", {}).get("impacts", [])
        # )
        # primacy_of_impact = "\uf00c" if primacy_of_impact else "\uf467"

        maximum_reward = program.get("maximum_reward")
        human_readable_max_reward = f"[green]${maximum_reward:,}[/green]"

        # table.add_row(program.get("project"), human_readable_max_reward, kycrequired)
        table.add_row(program.get("project"), human_readable_max_reward)
                                  
        count += 1

    console.print(table)

