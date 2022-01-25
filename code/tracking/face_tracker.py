import cv2
from mediapipe.python.solutions.face_mesh import FaceMesh as CreateFaceModel, FACEMESH_CONTOURS
from mediapipe.python.solutions.drawing_utils import draw_landmarks
from mediapipe.python.solutions.drawing_styles import get_default_face_mesh_contours_style
from event_handler import EventTypes
from helpers import get_points_distance

class FaceTracker:

    def __init__(self, event_handler):
        self.face_mesh = CreateFaceModel(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mouth_open_threshold = 0.03
        self.event_handler = event_handler
        self.face = Face(event_handler)

    def track_frame(self, frame, debug=False):
        result = self.face_mesh.process(frame)
        multi_face_landmarks = result.multi_face_landmarks
        if debug:
            frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if multi_face_landmarks:
            # face(s) detected, we only want 1
            landmarks = multi_face_landmarks[0]
            self.face.enable()
            self.face.update_mouth_landmarks(landmarks)
            self.face.update_open_status(self.mouth_open_threshold)

            # if we're in debug mode, draw these landmarks on the frame
            if debug:
                draw_landmarks(frame, landmarks, FACEMESH_CONTOURS, None, get_default_face_mesh_contours_style())
        elif not self.face.disabled:
            self.face.disable()
            self.event_handler.emit(EventTypes.JUMP_UP)
        return frame


class Face:

    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.mouth_points = []
        self.mouth_open = False
        self.disabled = True

    def update_open_status(self, threshold):
        last_state = self.mouth_open
        distance = get_points_distance(self.mouth_points)
        self.mouth_open = distance > threshold
        if last_state is not self.mouth_open:
            self.event_handler.emit(EventTypes.JUMP_DOWN if self.mouth_open else EventTypes.JUMP_UP)

    def update_mouth_landmarks(self, landmarks):
        # see https://github.com/ManuelTS/augmentedFaceMeshIndices/blob/master/Mouth.jpg for documentation on these indices
        self.mouth_points = (landmarks.landmark[12], landmarks.landmark[15])

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

