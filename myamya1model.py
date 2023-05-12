from costmatmodel import CostmatModel
from standardmodel import StandardModel
from pretty_midi import note_number_to_name
from numpy import ndarray,array
from math import ceil
from typing import Optional
from pandas import read_csv
from pathlib import Path
from os.path import splitext

def woextfn(fp:Path):
    """
    Returns the file name without extension.
    """
    fullfn = fp.name
    ext_split = splitext(fullfn)
    res = ext_split[0]
    return res

class Myamya1Model(CostmatModel):
    """
    Implementation of CostmatModel.
    This model is based on Mya-Mya's experience.
    The cost matrix depends on
    1. Whole-tone distance (e.g. the whole-tone distance of C4 and E4 is 2.)
    2. Whether containing semitones (e.g. the move from C#4 to F4 containes semitones.)
    """
    def __init__(self) -> None:
        super().__init__()
        self.standard = StandardModel()
        self.tablename_to_table = {
            woextfn(fp):array(read_csv(fp,header=None))
            for fp 
            in (Path(__file__).parent/"myamya1modeldata").iterdir()
        }
    def get_tablename(self, now: int, next: int) -> Optional[str]:
        assert now <= next
        if now == next:
            return "0"
        distance = next-now
        if distance == 1:
            return "+0h"
        blacks = int("#" in note_number_to_name(now))+ int("#" in note_number_to_name(next))
        has_half = (blacks % 2 == 1)
        finger_distance = ceil((distance-1)/2.)
        if finger_distance >= 5:
            return None
        return "+"+str(finger_distance)+("h"if has_half else "")

    def get(self, now: int, next: int, delta_time: float) -> ndarray:
        if next < now:
            return self.get(next, now, delta_time).T
        tablename = self.get_tablename(now, next)
        if tablename is None:
            return self.standard.get(now,next,delta_time)
        table = self.tablename_to_table[tablename]
        return table