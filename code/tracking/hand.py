from math import sqrt


class Hand:

    def __init__(self, is_left):
        self.is_left = is_left
        self.index_finger_joints = []
        self.pointing = False

    def update_pointing_status(self, threshold):
        distance = get_joints_distance(self.index_finger_joints)
        self.pointing = distance > threshold and is_pointing_right_way(self.index_finger_joints, self.is_left)


def get_joints_distance(joints):
    total = 0
    for i in range(1, len(joints)):
        x_dif = joints[i].x - joints[i - 1].x
        y_dif = joints[i].y - joints[i - 1].y
        total += sqrt(x_dif ** 2 + y_dif ** 2)
    return total


def is_pointing_right_way(joints, is_left):
    # in this case, index 0 = first knuckle, index 2 = fingertip
    return (joints[0].x > joints[2].x) ^ is_left
