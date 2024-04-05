from click import command

from bountyhunter.immunefi.dataprovider import ImmunefiDataProvider


@command(help="Synchronise targets")
def sync():
    immunefi_data_provider = ImmunefiDataProvider()
    programs = immunefi_data_provider.get_immunefi_programs()

    for program in programs:
        print(program.get('project'))
