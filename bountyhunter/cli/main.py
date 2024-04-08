from click import command, group

from bountyhunter.cli.sync import sync
from bountyhunter.cli.list import list
from bountyhunter.cli.show import show

# `bounty-hunter sync` command is used for synchronising targets
# `bounty-hunter hunt` will automatically run napalm


@group("Bounty hunting utility tool")
def cli():
    pass


cli.add_command(sync)
cli.add_command(search)
cli.add_command(list)
cli.add_command(show)

if __name__ == "__main__":
    cli()