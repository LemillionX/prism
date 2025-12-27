from sbtw.actions.base import OpenInExplorer
from sbtw.actions.build.files import Increment
from sbtw.actions.build.tasks import AddTask, BuildScene, EditStatus, SetStatus
from sbtw.core.constant import Status

ACTIONS = {
    "Base": [OpenInExplorer()],
    "FilesBase": [Increment()],
    "TasksBase": [EditStatus(actions=[SetStatus(status) for status in Status])],
    "TasksView": [AddTask()],
    "Modeling": [BuildScene()],
}
