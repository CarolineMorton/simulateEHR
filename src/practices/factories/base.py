# External imports
from typing import List, Optional, Dict
from abc import ABC, abstractmethod


# Internal Imports
from src.practices.practice import Practice



class PracticeFactoryBase(ABC):
    """
    Abstract Factory that creates the practices. This is a base class
    and should not be used directly.
    """
    @abstractmethod
    def create_practice(self, practice_id: int) -> Practice:
        pass

    @abstractmethod
    def create_practices(self, number_of_practices: int) -> List[Practice]:
        pass

