from __future__ import annotations

import re
from pathlib import Path

RE_VERSION = re.compile(r"^(.+_v)(?P<version>\d+)(\.[^.]+)$")


def get_last_version(file: Path):
    return max(file.parent.glob(f"*{file.suffix}"))


def get_next_version(file: Path):
    version_nb = 0
    last_version = get_last_version(file)
    if match := RE_VERSION.match(last_version.name):
        version_nb = int(match.group("version"))

    version_nb += 1
    next_file = replace_version(last_version.name, version_nb)
    return file.parent / next_file


def replace_version(s: str, new_version: int) -> str:
    def repl(m: re.Match) -> str:
        width = len(m.group("version"))
        return f"{m.group(1)}{new_version:0{width}d}{m.group(3)}"

    return RE_VERSION.sub(repl, s)


if __name__ == "__main__":
    from sbtw.core.log import logger

    _folder = Path(
        r"E:\Sammy\Projects\Test\Assets\MyAsset\Modeling\MyAsset_Modeling_v001.txt"
    )
    logger.info("Last version is %s", get_last_version(_folder))
    logger.info("Next version is %s", get_next_version(_folder))
