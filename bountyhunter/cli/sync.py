from click import command, argument

from bountyhunter.immunefi.dataprovider import ImmunefiDataProvider
from tqdm import tqdm
from pathlib import Path
from loguru import logger
from pygit2 import clone_repository, Repository

logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)


@command(help="Synchronise github repositories from bounty programs")
@argument("location")
def sync(location):
    location = Path(location)
    if not location.exists():
        logger.info("Location does not exist, creating it")
        location.mkdir(parents=True)
    if not location.is_dir():
        logger.error("Location must be a directory")
        return

    immunefi_data_provider = ImmunefiDataProvider()
    programs = immunefi_data_provider.get_immunefi_programs()

    for program in tqdm(programs):
        logger.info(f"Syncing {program.get('id')}")

        program_dir = location / program.get('id')
        if not program_dir.exists():
            program_dir.mkdir()

        program_info = immunefi_data_provider.get_program_info(program.get('id'))
        immunefi_data_provider.program_info_extract_assets(program_info)

        github_links = [asset['url'] for asset in program_info['bounty']['assets'] if asset['type'] == 'GitHub']
        for link in github_links:
            logger.info(f"Cloning {link}")
            # check if we've already cloned this repository (pull if that's the case
            if (program_dir / link.split('/')[-1]).exists():
                logger.info(f"Repository {link} already exists, skipping")
                continue

            clone_repository(f"https://{link}.git", str(program_dir / link.split('/')[-1]))

    logger.info("Sync complete")