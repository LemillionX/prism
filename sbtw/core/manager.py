from __future__ import annotations

import getpass
import json
from pathlib import Path
from typing import Any

from sbtw.core.constant import CONFIG
from sbtw.core.log import logger
from sbtw.core.project import Project


# TODO: Refactor to use singleton pattern
class ProjectManager:
    def __init__(self, project: Project | None = None):
        self.project = project

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
        logger.info("Current project is %s", self.project.name)

    def remove_project(self, name: str) -> None:
        data = self.get_projects(to_dict=True)
        if data.pop(name, None):
            logger.info("Project %s was successfully removed", name)
        else:
            logger.warning("Couldn't remove project %s", name)
        self.set_projects(data)


if __name__ == "__main__":
    _manager = ProjectManager()
    for _project in ["Toto", "Test", "SampleProject"]:
        _manager.set_project(project=_project)
        logger.info("Current project is %s", _manager.project.name)
        logger.info("Current project is %s", _manager.project.name)
