from dataclasses import dataclass


@dataclass
class ProcessMessage:
    error: bool         # This is an error message
    logging: bool       # Log message via logging
    ui: bool            # Display in UI
    message: str        # message
