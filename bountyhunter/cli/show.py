from click import command, argument
from rich.console import Console

from bountyhunter.immunefi.dataprovider import ImmunefiDataProvider
from toolz import concat


from thefuzz import process
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory, Suggestion
from prompt_toolkit.history import InMemoryHistory


# Custom AutoSuggest class for static suggestions
class StaticAutoSuggest(AutoSuggestFromHistory):
    def __init__(self, programs):
        self.programs = programs

    def get_suggestion(self, buffer, document):
        # Static suggestion - replace with your logic
        suggestions =[program.get('project') for program in self.programs]
        text = document.text

        if not text:
            return None

        for suggestion in suggestions:
            if suggestion.startswith(text) or suggestion.lower().startswith(text.lower()):
                return Suggestion(suggestion[len(text):])
        return None


def fuzzy_search(user_input, programs, limit=5):
    choices = {program.get('project'): program.get('id') for program in programs}
    results = process.extract(user_input, choices, limit=limit)

    return [dict(name=choice[2], id=choice[0]) for choice in results]


@command(help="Show information on a bug bounty program")
def show():
    immunefi_data_provider = ImmunefiDataProvider()
    programs = immunefi_data_provider.get_immunefi_programs()
    program_completer = WordCompleter([program.get('project') for program in programs], ignore_case=True)
    while True:
        user_input = prompt("Search: ", auto_suggest=StaticAutoSuggest(programs))
        matches = fuzzy_search(user_input, programs)

        for idx, match in enumerate(matches):
            if match.get('name').lower() == user_input.lower():
                _show(match.get('id'))
                exit(0)

            print(f"{idx+1}. {match.get('name')}")

        if matches:
            selection = int(prompt("Select a program to view details (0 to exit): "))
            if selection == 0:
                break
            elif 0 < selection <= len(matches):
                _show(matches[selection-1].get('id'))
        else:
            print("No matches found.")


# @command(help="Show information about a specific bug bounty programme")
# @argument("name")
# def show(name):
#     _show(name)


def _show(name):
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
    console.print(f"[bold]{data.get('bounty', {}).get('project')}[/bold]")

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