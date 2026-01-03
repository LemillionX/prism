from sbtw.actions.base import OpenInExplorer
from sbtw.actions.entity import AddAsset, AddShot
from sbtw.actions.files import Increment
from sbtw.actions.projects import RemoveProject
from sbtw.actions.tasks import AddTask, BuildScene, EditStatus, SetStatus
from sbtw.actions.thumbnail import CaptureThumbnail, SetThumbnail
from sbtw.core.constant import Status

ACTIONS = {
    "Base": [OpenInExplorer(), SetThumbnail(), CaptureThumbnail()],
    "AssetsView": [AddAsset(), OpenInExplorer()],
    "ShotsView": [AddShot(), OpenInExplorer()],
    "FilesBase": [Increment()],
    "TasksBase": [EditStatus(actions=[SetStatus(status) for status in Status])],
    "TasksView": [AddTask(), OpenInExplorer()],
    "FilesView": [OpenInExplorer()],
    "ProjectBase": [RemoveProject()],
    "Modeling": [BuildScene()],
}
