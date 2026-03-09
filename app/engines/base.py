from abc import ABC, abstractmethod


class TTSEngine(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def load_model(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        raise NotImplementedError
