from abc import ABC, abstractmethod

class BaseObserver(ABC):
    @abstractmethod
    def update(self, **kwargs):
        """Handle event update"""
        pass
