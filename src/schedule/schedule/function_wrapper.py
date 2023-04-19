from typing import Any, Callable, Dict, List, Any

class FunctionWrapper:
    def __init__(self, funct: Callable, *args, **kwargs):
        self.funct: Callable = funct
        self.args: List[Any] = list(args)
        self.kwargs: Dict[str, Any] = kwargs

    def __call__(self) -> Any:
        return self.funct(*self.args, **self.kwargs)

    def __repr__(self) -> str:
        return f"<FunctionWrapper (funct={self.funct}, args={self.args}, kwargs={self.kwargs})>"
    
    def __str__(self) -> str:
        return f"FunctionWrapper (funct={self.funct}, args={self.args}, kwargs={self.kwargs})"
    
    def __eq__(self, other: "FunctionWrapper") -> bool:
        return self.funct == other.funct and self.args == other.args and self.kwargs == other.kwargs
    
    def __hash__(self) -> int:
        return hash((self.funct, tuple(self.args), frozenset(self.kwargs.items())))