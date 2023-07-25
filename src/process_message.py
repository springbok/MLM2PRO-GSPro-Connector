from dataclasses import dataclass


@dataclass
class ProcessMessage:
    error: bool
    message: str
