from sbtw.actions.base import OpenInExplorer
from sbtw.actions.build.files import Increment
from sbtw.actions.build.tasks import AddTask, BuildScene

ACTIONS = {
    "Base": [OpenInExplorer()],
    "FilesBase": [Increment()],
    "TasksView": [AddTask()],
    "Modeling": [BuildScene()],
}
