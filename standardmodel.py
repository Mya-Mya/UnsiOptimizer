from costmatmodel import CostmatModel
from numpy import ndarray, array
from math import ceil, floor


def abs_ceil(x):
    return ceil(x) if x > 0 else floor(x)


class StandardModel(CostmatModel):
    """
    Implementation of CostmatModel.
    In this model, the cost is increased by the difference between note-distance and finger-distance.
    * note-distance : the distance between current not and next note.
    * finger-distance : the distance between i (the finger of playing the current note) and j (the finger of playing the next note).
    """

    def get(self, current: int, next: int, delta_time: float) -> ndarray:
        note_distance = abs_ceil((next-current)/2.)
        m = [[0 for _ in range(5)] for __ in range(5)]
        for start_finger in range(5):
            for end_finger in range(5):
                element = abs(note_distance-(end_finger-start_finger))
                m[start_finger][end_finger] = element
        return array(m)
