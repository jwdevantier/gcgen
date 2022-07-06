from abc import ABC, abstractmethod


class GcgenError(ABC, Exception):
    @abstractmethod
    def printerr(self) -> None:
        """Print message for end-user."""
        raise NotImplementedError(
            f"{self.__module__}.{type(self).__qualname__} does not implement `printerr`"
        )
