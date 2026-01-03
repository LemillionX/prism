from __future__ import annotations

import re
from pathlib import Path

from sbtw.core.log import logger

# Match: prefix ending with `_v`, numeric version, optional intermediate suffixes (e.g. `.1001`), then final extension
RE_VERSION = re.compile(r"^(.+_v)(?P<version>\d+)(?P<suffix>(?:\.[^.]+)*)\.(?P<ext>[^.]+)$")


def get_version_number(file: Path) -> int:
    if match := RE_VERSION.match(file.name):
        return int(match.group("version"))

    return -1


def get_last_version(file: Path) -> Path | None:
    suffix = ""
    if (m := RE_VERSION.match(file.name)) and (s := m.group("suffix")):
        suffix = s

    files = [
        f
        for f in file.parent.glob(f"*{file.suffix}")
        if (m := RE_VERSION.match(f.name)) and m.group("suffix") == suffix
    ]

    try:
        return max(files, key=get_version_number)
    except ValueError as e:
        logger.warning(e)
        return None


def get_next_version(file: Path) -> Path | None:
    version_nb = 0
    if (last_version := get_last_version(file)) and (match := RE_VERSION.match(last_version.name)):
        version_nb = int(match.group("version"))

        version_nb += 1
        next_file = replace_version(last_version.name, version_nb)
        return file.parent / next_file
    return None


def replace_version(s: str, new_version: int) -> str:
    def repl(m: re.Match) -> str:
        width = len(m.group("version"))
        # Reconstruct: prefix + zero-padded version + optional suffix + final extension
        return f"{m.group(1)}{new_version:0{width}d}{m.group('suffix')}.{m.group('ext')}"

    return RE_VERSION.sub(repl, s)


def format_word(word: str) -> str:
    return word.capitalize() if word.islower() else word


def prettier(text: str) -> str:
    return " ".join(format_word(word) for word in text.split()).replace(" ", "")


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

    _files = [
        r"E:\Sammy\Projects\Test\Shots\epXXXshYYYY\Layout\epXXXshYYYY_Layout_v001.1001.txt",
        r"E:\Sammy\Projects\Test\Shots\epXXXshYYYY\Layout\epXXXshYYYY_Layout_v001.1002.txt",
        r"E:\Sammy\Projects\Test\Shots\epXXXshYYYY\Layout\epXXXshYYYY_Layout_v002.txt",
        r"E:\Sammy\Projects\Test\Shots\epXXXshYYYY\Layout\epXXXshYYYY_Layout_v002.Modeling.txt",
    ]
    for _file in _files:
        logger.info("Last version of %s is %s", _file, get_last_version(Path(_file)))
        logger.info("Next version of %s is %s", _file, get_next_version(Path(_file)))
