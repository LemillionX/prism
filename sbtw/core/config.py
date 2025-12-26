from sbtw.actions.base import OpenInExplorer
from sbtw.actions.build.files import Increment
from sbtw.actions.build.tasks import BuildScene

ACTIONS = {
    "Base": [OpenInExplorer()],
    "FilesBase": [Increment()],
    "Modeling": [BuildScene()],
}
