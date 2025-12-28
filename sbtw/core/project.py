from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sbtw.actions.utils import get_path_before_keyword
from sbtw.core.constant import CONFIG, DEFAULT_THUMBNAIL, METADATA, EntityType, Status
from sbtw.core.log import logger


def get_meta_path(path: Path) -> Path:
    root = get_path_before_keyword(path=path, keywords=[entity_type.value for entity_type in EntityType])
    meta = root / ".project"
    return meta / path.relative_to(root)


class Project:
    def __init__(self, name: str | None = None, root: Path | str | None = None, path: Path | None = None):
        if path:
            self.get_project(path)
        else:
            self.name = name
            self.set_root(root)

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
            data = {}

        # -------------------- Save project data --------------------
        data[self.name] = self.to_dict()
        for k, v in kwargs.items():
            data[self.name][k] = v

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
            data = {"name": task.stem, "path": task}
            meta = get_meta_path(task)
            meta.mkdir(parents=True, exist_ok=True)
            with (get_meta_path(task) / METADATA).open(mode="r", encoding="utf8") as f:
                data["status"] = Status[json.load(f).get("status", "WTG")].name
            tasks.append(data)

        return tasks

    def get_files(self, task: str, entity: str, entity_type: EntityType = EntityType.Asset) -> list[dict]:
        return [
            {
                "name": file.name,
                "path": file,
                "thumbnail": self.get_thumbnail(file),
            }
            for file in sorted((self.root / entity_type.value / entity / task).glob("*"), reverse=True)
        ]

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

    def get_project(self, path: Path):
        root = get_path_before_keyword(
            path=path, keywords=[".project"] + [entity_type.value for entity_type in EntityType]
        )
        self.name = root.stem
        self.set_root(root)


if __name__ == "__main__":
    _project = Project(name="Test", root=r"E:\Sammy\Projects\Test")
    logger.info(_project.get_entities(entity_type=EntityType.Asset))
    logger.info(_project.get_entities(entity_type=EntityType.Asset))
    logger.info(_project.get_entities(entity_type=EntityType.Asset))
