from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

from sbtw.core.constant import CONFIG, DEFAULT_THUMBNAIL, Status
from sbtw.core.log import logger


class EntityType(str, Enum):
    Asset = "Assets"
    Shot = "Shots"


class Project:
    def __init__(self, name: str, root: Path | str):
        self.name = name
        self.root = Path(root)
        self.meta = self.root / ".project"

    def to_dict(self):
        data = self.__dict__
        for path in ["root", "meta"]:
            if data.get(path):
                data[path] = data[path].as_posix()
        return data

    def save(self):
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
        with CONFIG.open(mode="w", encoding="utf8") as config:
            json.dump(data, config, indent=4)
        logger.info("Project %s saved !", self.name)

    def create(self):
        self.root.mkdir(parents=True, exist_ok=True)
        self.meta.mkdir(parents=True, exist_ok=True)
        for folder in ["Assets", "Shots"]:
            (self.root / folder).mkdir(parents=True, exist_ok=True)
            (self.meta / folder).mkdir(parents=True, exist_ok=True)

    def get_entities(self, entity_type: EntityType = EntityType.Asset) -> list[dict]:
        return [
            {
                "name": asset.stem,
                "type": entity_type.name,
                "path": asset,
                "thumbnail": thumbnail
                if (thumbnail := self.meta / asset.relative_to(self.root)) and thumbnail.exists()
                else DEFAULT_THUMBNAIL,
            }
            for asset in (self.root / entity_type.value).glob("*")
        ]

    def get_tasks(self, entity: str, entity_type: EntityType = EntityType.Asset) -> list[dict]:
        tasks = []
        for task in (self.root / entity_type.value / entity).glob("*"):
            if not task.stem.startswith("."):
                data = {"name": task.stem, "path": task}
                with (task / ".status").open(mode="r", encoding="utf8") as f:
                    data["status"] = Status[json.load(f).get("status", "WTG")].name
                tasks.append(data)

        return tasks

    def get_files(self, task: str, entity: str, entity_type: EntityType = EntityType.Asset) -> list[dict]:
        return [
            {
                "name": file.name,
                "path": file,
                "thumbnail": thumbnail
                if (thumbnail := self.meta / file.relative_to(self.root)) and thumbnail.exists()
                else DEFAULT_THUMBNAIL,
            }
            for file in sorted((self.root / entity_type.value / entity / task).glob("*"), reverse=True)
            if not file.stem.startswith(".")
        ]


if __name__ == "__main__":
    _project = Project(name="Test", root=r"E:\Sammy\Projects\Test")
    logger.info(_project.get_entities(entity_type=EntityType.Asset))
