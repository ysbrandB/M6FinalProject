import cv2


class Camera:

    def __init__(self, webcam_id):
        self.webcam_id = webcam_id
        self.cap = cv2.VideoCapture(self.webcam_id)

    def read_frame(self):
        if self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                # failed to read camera frame. ignore and continue
                return None

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        else:
            self.cap.release()
            exit(1)

    def get_aspect_ratio(self):
        return self.cap.get(3) / self.cap.get(4)

    def __del__(self):
        self.cap.release()
