import cv2
from mediapipe.python.solutions.hands import Hands as CreateHandsModel, HAND_CONNECTIONS
from mediapipe.python.solutions.drawing_utils import draw_landmarks
from mediapipe.python.solutions.drawing_styles import get_default_hand_landmarks_style, get_default_hand_connections_style
from math import sqrt
from event_handler import EventTypes

class HandTracker:

    def __init__(self, event_handler):
        self.hands = CreateHandsModel(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.pointing_distance_threshold = 0.085
        self.event_handler = event_handler
        self.left_hand = Hand(True, event_handler)
        self.right_hand = Hand(False, event_handler)

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
                hand = self.left_hand
                # mediapipe flips left and right
                if multi_handedness[index].classification[0].label == "Left":
                    hand = self.right_hand
                if len(multi_handedness) == 1:
                    self.get_other_hand(hand).disable()
                hand.update_finger_joints(landmarks)
                hand.update_pointing_status(self.pointing_distance_threshold)

                # if we're in debug mode, draw these landmarks on the frame
                if debug:
                    draw_landmarks(frame, landmarks, HAND_CONNECTIONS, get_default_hand_landmarks_style(), get_default_hand_connections_style())
            if self.left_hand.pointing or self.right_hand.pointing:
                self.event_handler.emit(EventTypes.RUN_DOWN)
            else:
                self.event_handler.emit(EventTypes.RUN_UP)
        else:
            self.left_hand.disable()
            self.right_hand.disable()
            self.event_handler.emit(EventTypes.RUN_UP)
        return frame

    def get_other_hand(self, hand):
        return self.left_hand if hand is self.right_hand else self.right_hand


class Hand:

    def __init__(self, is_left, event_handler):
        self.is_left = is_left
        self.event_handler = event_handler
        self.index_finger_joints = []
        self.pointing = False

    def update_pointing_status(self, threshold):
        last_state = self.pointing
        distance = get_joints_distance(self.index_finger_joints)
        self.pointing = distance > threshold and is_pointing_right_way(self.index_finger_joints, self.is_left)
        if last_state is not self.pointing:
            if self.is_left:
                self.event_handler.emit(EventTypes.LEFT_DOWN if self.pointing else EventTypes.LEFT_UP)
            else:
                self.event_handler.emit(EventTypes.RIGHT_DOWN if self.pointing else EventTypes.RIGHT_UP)

    def update_finger_joints(self, landmarks):
        # see https://google.github.io/mediapipe/solutions/hands.html for documentation on these indices
        self.index_finger_joints = (landmarks.landmark[6], landmarks.landmark[7], landmarks.landmark[8])

    def disable(self):
        self.event_handler.emit(EventTypes.LEFT_UP if self.is_left else EventTypes.RIGHT_UP)

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

