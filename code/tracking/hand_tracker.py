import cv2
from mediapipe.python.solutions.hands import Hands as CreateHandsModel, HAND_CONNECTIONS
from mediapipe.python.solutions.drawing_utils import draw_landmarks
from mediapipe.python.solutions.drawing_styles import get_default_hand_landmarks_style, get_default_hand_connections_style
from math import sqrt


class HandTracker:

    def __init__(self):
        self.hands = CreateHandsModel(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.pointing_distance_threshold = 0.085
        self.left_hand = Hand(True)
        self.right_hand = Hand(False)

    def track_frame(self, frame, debug=False):
        result = self.hands.process(frame)
        multi_hand_landmarks = result.multi_hand_landmarks
        multi_handedness = result.multi_handedness
        if debug:
            frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if multi_hand_landmarks:
            # hands detected, process the output

            for index, landmarks in enumerate(multi_hand_landmarks):
                # mediapipe flips left and right
                if multi_handedness[index].classification[0].label == "Left":
                    # update right hand's positions and pointing status
                    self.update_hand_positions_and_status(self.right_hand, landmarks)
                else:
                    # update left hand's positions and pointing status
                    self.update_hand_positions_and_status(self.left_hand, landmarks)

                # if we're in debug mode, draw these landmarks on the frame
                if debug:
                    draw_landmarks(frame, landmarks, HAND_CONNECTIONS, get_default_hand_landmarks_style(), get_default_hand_connections_style())
        return frame

    def update_hand_positions_and_status(self, hand, landmarks):
        # see https://google.github.io/mediapipe/solutions/hands.html for documentation on these indices
        hand.index_finger_joints = (landmarks.landmark[6], landmarks.landmark[7], landmarks.landmark[8])
        hand.update_pointing_status(self.pointing_distance_threshold)


class Hand:

    def __init__(self, is_left):
        self.is_left = is_left
        self.index_finger_joints = []
        self.pointing = False
        self.last_state = False

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
