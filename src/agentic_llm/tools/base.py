from abc import ABC, abstractmethod


class ToolABC(ABC):
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
