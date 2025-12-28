from pathlib import Path
from typing import Any

from sbtw.actions.base import ActionBase
from sbtw.actions.utils import get_path_before_keyword
from sbtw.core.constant import EntityType


class AddThumbnail(ActionBase):
    @staticmethod
    def name() -> str:
        return "Add Thumbnail"

    def get_thumbnail(self):
        pass

    def _execute(self, **kwargs: Any) -> None:
        path = Path(kwargs.get("path"))
        root = get_path_before_keyword(path=path, keywords=[entity_type.value for entity_type in EntityType])
        meta = root / ".project"
        return meta / path.relative_to(root)
