from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    """
    Base class for all extractors.
    """
    @abstractmethod
    def extract(self, soup, base_url):
        pass
