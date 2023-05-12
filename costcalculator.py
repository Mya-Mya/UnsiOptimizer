from costmatmodel import CostmatModel
from pretty_midi import Note
from typing import Sequence


class CostCalculator:
    """
    Calculates the total cost based on
    * CostmatModel
    * fingering array
    * notes
    """

    def __init__(self,
                 costmatmodel: CostmatModel,
                 notes: Sequence[Note]
                 ) -> None:
        self.costmatmodel = costmatmodel
        assert len(notes) > 1
        self.notes = notes
        self.costmat_s = [
            costmatmodel.get(n1.pitch, n2.pitch, n2.start-n1.start)
            for n1, n2
            in zip(notes[:-1], notes[1:])
        ]
        self.costmat_s_len = len(self.costmat_s)

    def get_total_cost(self, fingeringarray: Sequence[int]) -> float:
        assert len(self.notes) == len(fingeringarray)
        total_cost = 0.0
        for i in range(self.costmat_s_len):
            cost = self.costmat_s[i][fingeringarray[i], fingeringarray[i+1]]
            total_cost += cost
        return total_cost
