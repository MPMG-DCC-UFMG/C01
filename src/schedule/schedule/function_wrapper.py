from datetime import datetime
from typing import Any, Callable, Dict, List, Any
import inspect

class FunctionWrapper:
    def __init__(self, funct: Callable, *args, **kwargs):
        self.funct: Callable = funct
        self.args: List[Any] = list(args)
        self.kwargs: Dict[str, Any] = kwargs

    def __call__(self, next_run: datetime = None) -> Any:
        # check if the funct accepts a next_run argument

        print('-' * 15)
        print(f'The funct {self.funct} requires next_run: {self.funct_requires_next_run()}')
        print(f'next_run: {next_run}')
        print('-' * 15)

        if self.funct_requires_next_run():
            self.kwargs["next_run"] = next_run

        return self.funct(*self.args, **self.kwargs)

    def __repr__(self) -> str:
        return f"<FunctionWrapper (funct={self.funct}, args={self.args}, kwargs={self.kwargs})>"
    
    def __str__(self) -> str:
        return f"FunctionWrapper (funct={self.funct}, args={self.args}, kwargs={self.kwargs})"
    
    def __eq__(self, other: "FunctionWrapper") -> bool:
        return self.funct == other.funct and self.args == other.args and self.kwargs == other.kwargs
    
    def __hash__(self) -> int:
        return hash((self.funct, tuple(self.args), frozenset(self.kwargs.items())))
    
    def funct_requires_next_run(self) -> bool:
        args_accept = inspect.getfullargspec(self.funct).args
        return 'next_run' in args_accept
    