from abc import ABC, abstractmethod


class ToolABC(ABC):
    def __init__(self, confirm_action: bool = True, **kwargs):
        self.confirm_action = confirm_action

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def usage(self) -> str:
        pass

    @abstractmethod
    def __call__(self, query: str):
        pass
