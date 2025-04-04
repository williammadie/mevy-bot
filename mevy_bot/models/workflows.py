from dataclasses import dataclass
from multiprocessing import Process

@dataclass
class WorkflowInfo:
    workflow_process: Process
