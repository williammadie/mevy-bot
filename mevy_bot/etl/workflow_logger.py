import os
import json
import logging
from datetime import datetime
from typing import Self

from mevy_bot.path_finder import PathFinder

application_logger = logging.getLogger(__name__)


class WorkflowLogger:

    def __init__(self: Self, job_id: int) -> None:
        self.job_id = job_id
        self.log_filepath = os.path.join(
            PathFinder.workflow_log_dirpath(),
            f"{job_id}.log"
        )
        os.makedirs(
            PathFinder.workflow_log_dirpath(),
            exist_ok=True
        )

    def info(self: Self, message: str) -> None:
        application_logger.info(message)
        self._write_log("INFO", message)

    def warning(self: Self, message: str) -> None:
        application_logger.warning(message)
        self._write_log("WARNING", message)

    def error(self: Self, message: str) -> None:
        application_logger.error(message)
        self._write_log("ERROR", message)

    def _write_log(self: Self, level: str, message: str) -> None:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "message": message
        }
        try:
            with open(self.log_filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            application_logger.exception("Failed to write workflow log: %s", e)
