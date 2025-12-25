from abc import ABCMeta, abstractmethod
from typing import Any

from sbtw.core.log import logger


class ActionBase(metaclass=ABCMeta):
    @staticmethod
    def name() -> str:
        pass

    def pre_run(self, **kwargs):
        logger.debug("%s has no pre-run", self)

    def post_run(self, **kwargs):
        logger.debug("%s has no post-run", self)

    @abstractmethod
    def _execute(self, **kwargs: Any):
        pass

    @classmethod
    def execute(cls, **kwargs):
        self = cls()
        logger.info("Executing '%s' action", cls.name())
        failed = None

        try:
            self.pre_run(**kwargs)
        except Exception:
            logger.exception("%s: pre-run has failed", cls.name())
            raise

        try:
            self._execute(**kwargs)
        except Exception as e:
            logger.exception("%s: execution has failed", cls.name())
            failed = e
        finally:
            try:
                self.post_run(**kwargs)
            except Exception:
                logger.exception("%s: post-run has failed", cls.name())
                raise

        if failed:
            raise failed


class BuildBase(ActionBase):
    @staticmethod
    def name() -> str:
        return "Build"
