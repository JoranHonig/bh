from click import command, argument
from rich.console import Console

from bountyhunter.immunefi.dataprovider import ImmunefiDataProvider
from toolz import concat

@command(help="Show information about a specific bug bounty programme")
@argument("name")
def show(name):
    immunefi_data_provider = ImmunefiDataProvider()
    data = immunefi_data_provider.get_program_info(name)

    if not data:
        print("Program not found")
        return

    # interesting keys:
    # data.bounty.project - project name
    # data.bounty.maxBounty - maximum reward
    # data.bounty.launchDate - launch date (yyyy-mm-ddThh:mm:ss...)
    # data.bounty.updatedDate - updated date
    # data.bounty.rewards = [{"assetType": ..., "level": ..., "payout": ..., "pocRequired": ...}]
    # data.bounty.programOverview - program overview
    # data.bounty.tags.productType = ["example"] ( can be null)
    # data.bounty.tags.projectType ( can be null)
    # data.bounty.tags.ecosystem ( can be null)
    # data.bounty.tags.programType ( can be null)
    # data.bounty.tags.language ( can be null)

    # only yyyy-mm-dd
    launch_date = data.get('bounty', {}).get('launchDate').split('T')[0]
    updated_date = data.get('bounty', {}).get('updatedDate').split('T')[0]

    console = Console()

    # title
    console.print(f"[bold]{data.get('bounty', {}).get("project")}[/bold]")

    # metadata in grey italics
    console.print(f"[italic][grey]launch: {launch_date}, updated on {updated_date}[/grey][/italic]")

    # print tags on same line
    subtags = [ l for l in data.get('bounty', {}).get('tags', {}).values() if l]
    tags = list(concat(subtags))
    tags_str = ', '.join([f"#{tag}" for tag in tags])

    console.print(f"[italic][grey]{tags_str}[/grey][/italic]\n")

    # rewards
    console.print("[bold]Reward Levels[/bold]")
    for reward in data.get('bounty', {}).get('rewards', []):
        console.print(f"{reward.get('assetType')} - {reward.get('level')}: [green]{reward.get('payout')}[/green]")

    # Assets
    # print github links
    assets = immunefi_data_provider.program_info_extract_assets(data)
    github_assets = [asset for asset in assets if asset.get('type') == 'GitHub']
    if github_assets:
        console.print("\n[bold]Github Links[/bold]")
        for asset in github_assets:
            console.print(f"{asset.get('url')}")