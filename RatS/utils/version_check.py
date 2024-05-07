import logging
from pathlib import Path

import requests
import toml
from packaging.version import Version

GITHUB_API_RELEASE_ENDPOINT = "https://api.github.com/repos/StegSchreck/RatS/releases/latest"


def check_version() -> None:
    response = requests.get(GITHUB_API_RELEASE_ENDPOINT)
    latest_version = Version(version=response.json()["tag_name"])
    logging.info(f"Latest RatS version is {latest_version}")

    pyproject_toml_file = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject_toml_file.exists() and pyproject_toml_file.is_file():
        __package_version = toml.load(pyproject_toml_file)["tool"]["poetry"]["version"]
        local_version = Version(version=__package_version)
        logging.info(f"Local RatS version is {local_version}")
        if local_version < latest_version:
            logging.warning(
                f"The local RatS version {local_version} is behind the latest version {latest_version}. "
                f"Please consider updating."
            )
