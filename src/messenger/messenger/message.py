from typing import Any, Dict
from typing_extensions import TypedDict

class Message(TypedDict):
    sender: str 
    content: Dict[Any, Any]