from dataclasses import dataclass


@dataclass
class BallData:
    Speed: float
    SpinAxis: float
    TotalSpin: float
    HLA: float
    VLA: float
    ClubSpeed: float