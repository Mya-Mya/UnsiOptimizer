from numpy import ndarray
from abc import ABC,abstractmethod


class CostmatModel(ABC):
    @abstractmethod
    def get(self, current: int, next: int, delta_time: float) -> ndarray:
        """

        Parameters
        ----------
        current : int
            Note number of current note.
        next : int
            Note number of next note.
        delta_time :float
            Time from the beginning of the current note to the beginning of the next note.

        Returns
        -------
        costmat : ndarray
            Cost matrix. 
            costmat[i,j] is the cost of playing the current note with i, and the next note with j. 
        """
        pass
