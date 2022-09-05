from abc import ABC, abstractmethod
from typing import Any, Dict

from messenger import Message

class Processor(ABC):
    @abstractmethod
    def process_message(self, message: Message) -> bool:
        pass  