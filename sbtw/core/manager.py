from __future__ import annotations

import getpass
import json
from pathlib import Path
from typing import Any

from sbtw.core.constant import CONFIG, EntityType
from sbtw.core.log import logger
from sbtw.core.project import Project


# Singleton ProjectManager: only one instance exists per process
class ProjectManager:
    _instance: ProjectManager | None = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Avoid re-running initialization on subsequent constructions
        if self._initialized:
            return

        # ------------- Variables -------------
        self.project = None
        self.current_path = None
        self._initialized = True
        self.username = None

        # ------------ Load Config -------------
        logger.info("Loading configuration from %s", CONFIG.as_posix())
        data = self.get_config()
        self.username = data.get("username")
        logger.info("Configuration loaded !")
        logger.info("Connected as %s", self.username)

    def create(self, name: str, root: Path | str):
        self.project = Project(name=name, root=root)
        self.project.create()
        self.project.save()

    def get_config(self) -> dict:
        try:
            with CONFIG.open(mode="r", encoding="utf8") as config:
                data = json.load(config)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            logger.warning("Config file %s does not exist. Creating it...", CONFIG.as_posix())
            data = {"username": getpass.getuser(), "projects": {}}
            with CONFIG.open(mode="w", encoding="utf8") as f:
                json.dump(data, f, indent=4)

        return data

    def save_config(self, **kwargs: Any) -> None:
        config = self.get_config()
        for k, v in kwargs.items():
            config[k] = v

        with CONFIG.open(mode="w", encoding="utf8") as f:
            json.dump(config, f, indent=4)

        logger.info("Configuration saved !")

    def get_projects(self, to_dict: bool = False) -> list[dict] | dict:
        data = self.get_config()
        if to_dict:
            return data.get("projects", {})

        return data.get("projects", {}).values()

    def set_projects(self, data: dict) -> None:
        config = self.get_config()
        config["projects"] = data
        with CONFIG.open(mode="w", encoding="utf8") as f:
            json.dump(config, f, indent=4)

    def set_project(self, project: str):
        data = self.get_projects(to_dict=True)
        if project_data := data.get(project):
            self.project = Project(name=project_data["name"], root=Path(project_data["root"]))
        else:
            logger.exception("Project %s not in config file %s", project, CONFIG.as_posix())

        self.current_path = self.project.root
        logger.info("Current project is %s", self.project.name)

    def remove_project(self, name: str) -> None:
        data = self.get_projects(to_dict=True)
        if data.pop(name, None):
            logger.info("Project %s was successfully removed", name)
        else:
            logger.warning("Couldn't remove project %s", name)
        self.set_projects(data)

    def get_current_element(self) -> dict:
        tokens = self.current_path.relative_to(self.project.root.parent).parts
        entity = {"path": self.current_path, "username": self.username, "root": self.project.root}
        for idx, key in enumerate(["project", "entity_type", "entity", "task", "file"]):
            entity[key] = tokens[idx] if len(tokens) > idx else None
            if key == "entity_type" and entity[key]:
                entity[key] = EntityType(entity[key])
        return entity


if __name__ == "__main__":
    _manager = ProjectManager()
    for _project in ["Toto", "Test", "SampleProject"]:
        _manager.set_project(project=_project)
        logger.info("Current project is %s", _manager.project.name)
