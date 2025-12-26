from __future__ import annotations

import json
from pathlib import Path

from sbtw.core.constant import CONFIG
from sbtw.core.log import logger
from sbtw.core.project import Project


class ProjectManager:
    def __init__(self, project: Project | None = None):
        self.project = project

    def create(self, name: str, root: Path | str):
        self.project = Project(name=name, root=root)
        self.project.create()
        self.project.save()

    def get_projects(self) -> list[dict]:
        try:
            with CONFIG.open(mode="r", encoding="utf8") as config:
                data = json.load(config)
        except json.decoder.JSONDecodeError:
            logger.warning("No project in  %s...", CONFIG.as_posix())
            data = {}
        return data.values()

    def set_project(self, project: str):
        try:
            with CONFIG.open(mode="r", encoding="utf8") as config:
                data = json.load(config)
        except json.decoder.JSONDecodeError:
            logger.exception("No project in  %s...", CONFIG.as_posix())
        else:
            if project_data := data.get(project):
                self.project = Project(
                    name=project_data["name"], root=Path(project_data["root"])
                )
            else:
                logger.exception(
                    "Project %s not in config file %s", project, CONFIG.as_posix()
                )
        logger.info("Current project is %s", self.project.name)


if __name__ == "__main__":
    _manager = ProjectManager()
    for _project in ["Toto", "Test", "SampleProject"]:
        _manager.set_project(project=_project)
        logger.info("Current project is %s", _manager.project.name)
