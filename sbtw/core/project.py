from __future__ import annotations

import getpass
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sbtw.actions.utils import format_size, get_path_before_keyword
from sbtw.core.constant import CONFIG, DEFAULT_THUMBNAIL, METADATA, SOFTWARES, EntityType, Status
from sbtw.core.log import logger


def get_meta_path(path: Path) -> Path:
    root = get_path_before_keyword(path=path, keywords=[entity_type.value for entity_type in EntityType])
    meta = root / ".project"
    return meta / path.relative_to(root)


class Project:
    def __init__(self, name: str | None = None, root: Path | str | None = None, path: Path | None = None):
        if path:
            self.get_project(path)
        elif name and root:
            self.name = name
            self.set_root(root)
        else:
            self.name = None
            self.root = Path()

    def set_root(self, root: Path):
        self.root = Path(root)
        self.meta = self.root / ".project"

    def to_dict(self):
        data = self.__dict__
        for path in ["root", "meta"]:
            if data.get(path):
                data[path] = data[path].as_posix()
        return data

    def save(self, **kwargs: Any):
        logger.info("Saving project %s ...", self.name)
        # -------------------- Load projects data --------------------
        try:
            with CONFIG.open(mode="r", encoding="utf8") as config:
                data = json.load(config)
        except json.decoder.JSONDecodeError:
            logger.warning(
                "Config file  %s seems to be empty. Initializing it...",
                CONFIG.as_posix(),
            )
            data = {"projects": {}}

        # -------------------- Save project data --------------------
        data["projects"][self.name] = self.to_dict()
        for k, v in kwargs.items():
            data["projects"][self.name][k] = v

        with CONFIG.open(mode="w", encoding="utf8") as config:
            json.dump(data, config, indent=4)
        logger.info("Project %s saved !", self.name)

    def create(self):
        logger.info("Creating root folder %s ...", self.root.as_posix())
        self.root.mkdir(parents=True, exist_ok=True)
        logger.info("Creating metadata folder %s ...", self.meta.as_posix())
        self.meta.mkdir(parents=True, exist_ok=True)

        for folder in ["Assets", "Shots"]:
            logger.info("Creating folder %s ...", (self.root / folder).as_posix())
            (self.root / folder).mkdir(parents=True, exist_ok=True)
            logger.info("Creating metadata folder %s ...", (self.meta / folder).as_posix())
            (self.meta / folder).mkdir(parents=True, exist_ok=True)
        logger.info("Project %s created !", self.name)

    def get_entities(self, entity_type: EntityType = EntityType.Asset) -> list[dict]:
        return [
            {
                "name": asset.stem,
                "type": entity_type.name,
                "path": asset,
                "thumbnail": self.get_thumbnail(asset),
            }
            for asset in (self.root / entity_type.value).glob("*")
        ]

    def get_tasks(self, entity: str, entity_type: EntityType = EntityType.Asset) -> list[dict]:
        tasks = []
        for task in (self.root / entity_type.value / entity).glob("*"):
            metadata = self.get_task_metadata(task)
            data = {"name": task.stem, "path": task, "thumbnail": self.get_thumbnail(task)}
            data.update(metadata)
            data["status"] = Status[metadata.get("status", "WTG")].name
            tasks.append(data)

        return tasks

    def get_files(self, task: str, entity: str, entity_type: EntityType = EntityType.Asset) -> list[dict]:
        files = []
        for file in sorted((self.root / entity_type.value / entity / task).glob("*"), reverse=True):
            data = {
                "name": file.name,
                "path": file,
                "author": None,
                "icon": self.get_software(file),
                "thumbnail": self.get_thumbnail(file),
                "date": datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
                "size": format_size(file.stat().st_size),
            }
            metadata = self.get_file_metadata(file)
            data["author"] = metadata.get("author", "Unknown Author")
            files.append(data)

        return files

    def get_thumbnail_path(self, element: Path):
        thumbnail = self.meta / element.relative_to(self.root)
        if element.is_dir():
            thumbnail = thumbnail / f"{element.stem}-thumbnail"
        else:
            thumbnail = thumbnail.parent / f"{thumbnail.stem}-thumbnail"
        return thumbnail.with_suffix(".png")

    def get_thumbnail(self, element: Path) -> Path:
        thumbnail = self.get_thumbnail_path(element)
        if thumbnail.exists():
            return thumbnail

        return DEFAULT_THUMBNAIL

    def get_software(self, file: Path) -> list[Path]:
        return SOFTWARES.get(file.suffix.lower(), [])

    def get_project(self, path: Path):
        root = get_path_before_keyword(
            path=path, keywords=[".project"] + [entity_type.value for entity_type in EntityType]
        )
        self.name = root.stem
        self.set_root(root)

    def get_task_metadata(self, task: Path) -> dict:
        meta = get_meta_path(task)
        meta.mkdir(parents=True, exist_ok=True)
        try:
            with (meta / METADATA).open(mode="r", encoding="utf8") as f:
                metadata = json.load(f)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            logger.warning("Metadata for %s do not exist. Creating them...", meta.as_posix())
            metadata = {"name": task.stem, "entity": task.parent.stem}
            with (meta / METADATA).open(mode="w", encoding="utf8") as f:
                json.dump(metadata, f, indent=4)

        return metadata

    def get_file_metadata(self, file: Path) -> dict:
        meta = get_meta_path(file).with_suffix(METADATA)
        meta.parent.mkdir(parents=True, exist_ok=True)
        meta.touch(exist_ok=True)
        try:
            with meta.open(mode="r", encoding="utf8") as f:
                metadata = json.load(f)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            logger.warning("Metadata for %s do not exist. Creating them...", file.as_posix())
            metadata = {"author": getpass.getuser(), "status": Status.WTG.name}
            with meta.open(mode="w", encoding="utf8") as f:
                json.dump(metadata, f, indent=4)

        return metadata

    def set_task_metadata(self, task: Path, **kwargs: Any):
        # -------------------- Get project --------------------
        self.get_project(task)
        meta = get_meta_path(task) / METADATA

        # -------------------- Load metadata --------------------
        metadata = self.get_task_metadata(task)

        # -------------------- Save metadata --------------------
        for k, v in kwargs.items():
            metadata[k] = v
        with meta.open(mode="w", encoding="utf8") as f:
            json.dump(metadata, f, indent=4)

    def set_file_metadata(self, file: Path, **kwargs: Any):
        # -------------------- Get project --------------------
        self.get_project(file)
        meta = get_meta_path(file).with_suffix(METADATA)
        meta.parent.mkdir(parents=True, exist_ok=True)

        # -------------------- Load metadata --------------------
        metadata = self.get_file_metadata(file)

        # -------------------- Save metadata --------------------
        for k, v in kwargs.items():
            metadata[k] = v
        with meta.open(mode="w", encoding="utf8") as f:
            json.dump(metadata, f, indent=4)


if __name__ == "__main__":
    _project = Project(name="Test", root=r"E:\Sammy\Projects\Test")
    logger.info(_project.get_entities(entity_type=EntityType.Asset))
    logger.info(_project.get_entities(entity_type=EntityType.Asset))
    logger.info(_project.get_entities(entity_type=EntityType.Asset))
