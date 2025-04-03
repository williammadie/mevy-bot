from dataclasses import dataclass
from asyncio.tasks import Task

@dataclass
class WorkflowInfo:
    asyncio_task: Task
