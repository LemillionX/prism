from sbtw.actions.assets import AddAsset
from sbtw.actions.base import OpenInExplorer
from sbtw.actions.files import Increment
from sbtw.actions.projects import RemoveProject
from sbtw.actions.tasks import AddTask, BuildScene, EditStatus, SetStatus
from sbtw.actions.thumbnail import CaptureThumbnail, SetThumbnail
from sbtw.core.constant import Status

ACTIONS = {
    "Base": [OpenInExplorer(), SetThumbnail(), CaptureThumbnail()],
    "AssetsView": [AddAsset()],
    "FilesBase": [Increment()],
    "TasksBase": [EditStatus(actions=[SetStatus(status) for status in Status])],
    "TasksView": [AddTask()],
    "ProjectBase": [RemoveProject()],
    "Modeling": [BuildScene()],
}
