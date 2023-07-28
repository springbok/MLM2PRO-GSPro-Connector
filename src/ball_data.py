
class BallData:
    def __init__(self):
        self.speed = 0
        self.spin_axis = 0
        self.total_spin = 0
        self.hla = 0
        self.vla = 0
        self.club_speed = 0
        self.back_spin = 0
        self.side_spin = 0

    def __copy__(self):
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        return obj
