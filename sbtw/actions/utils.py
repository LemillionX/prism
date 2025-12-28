from __future__ import annotations

import re
from pathlib import Path

from sbtw.core.log import logger

RE_VERSION = re.compile(r"^(.+_v)(?P<version>\d+)(\.[^.]+)$")


def get_last_version(file: Path) -> Path | None:
    try:
        return max(file.parent.glob(f"*{file.suffix}"))
    except ValueError as e:
        logger.warning(e)
        return None


def get_next_version(file: Path) -> Path | None:
    version_nb = 0
    last_version = get_last_version(file)
    if (last_version := get_last_version(file)) and (match := RE_VERSION.match(last_version.name)):
        version_nb = int(match.group("version"))

        version_nb += 1
        next_file = replace_version(last_version.name, version_nb)
        return file.parent / next_file
    return None


def replace_version(s: str, new_version: int) -> str:
    def repl(m: re.Match) -> str:
        width = len(m.group("version"))
        return f"{m.group(1)}{new_version:0{width}d}{m.group(3)}"

    return RE_VERSION.sub(repl, s)


def format_word(word: str) -> str:
    return word.capitalize() if word.islower() else word


def prettier(text: str) -> str:
    return " ".join(format_word(word) for word in text.split()).replace("_", " ").replace(" ", "")


def get_path_before_keyword(path: Path, keywords: list[str]) -> Path:
    parts = path.parts

    for i, part in enumerate(parts):
        if part in keywords:
            return Path(*parts[:i])

    return path


def format_size(size: int) -> str:
    modulo = 1024
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < modulo:
            return f"{size:.1f} {unit}"
        size /= modulo
    return "PB"


if __name__ == "__main__":
    from sbtw.core.log import logger

    _folder = Path(r"E:\Sammy\Projects\Test\Assets\MyAsset\Modeling\MyAsset_Modeling_v001.txt")
    logger.info("Last version is %s", get_last_version(_folder))
    logger.info("Next version is %s", get_next_version(_folder))
    logger.info("Last version is %s", get_last_version(_folder))
    logger.info("Next version is %s", get_next_version(_folder))
