from requests import get
from json import loads
from typing import Dict, Any
from toolz import memoize
from bs4 import BeautifulSoup
from re import match, findall
import json


class ImmunefiDataProvider:
    @staticmethod
    def _clean_immunefi_program(program):
        program.pop('contentfulId')
        return program

    def get_immunefi_programs(self):
        url = "https://immunefi.com/_next/data/eDW5IfKuoHBKtCwL_1Nrf/bug-bounty.json"
        response = get(url)
        data: Dict[str, Any] = loads(response.text)

        programs = data.get("pageProps", {}).get("bounties", [])
        programs = [self._clean_immunefi_program(program) for program in programs]

        return programs

    def program_info_extract_assets(self, program_info):
        assets = program_info.get("bounty", {}).get("assets", [])
        assets_body = program_info.get("bounty", {}).get("assetsBody", None) or program_info.get("bounty", {}).get("assetsBodyV2", "")

        github_links = findall(r"github.com/[a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+", assets_body)
        # dedupe
        github_links = list(set(github_links))

        for link in github_links:
            assets.append(
                {'description': 'Github Link', 'id': None, 'isPrimacyOfImpact': False, 'type': 'GitHub', 'url': link}
            )

        return assets

    def get_program_info(self, program_id):
        url = f"https://immunefi.com/bounty/{program_id}"

        response = get(url)
        data_match = findall(r"<script id=\"__NEXT_DATA__\" type=\"application/json\">(.*)</script>", response.text)

        if not data_match:
            return

        data: Dict[str, Any] = loads(data_match[0])
        data = (data.get("props", {}).get("pageProps", {}))

        return data
