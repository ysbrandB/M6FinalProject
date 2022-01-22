import cv2
from hand_tracker import HandTracker
# mp_face_mesh = mp.solutions.face_mesh

cap = cv2.VideoCapture(2)
hand_tracker = HandTracker()
# face = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = hand_tracker.track_frame(image, True)


    # if face_results.multi_face_landmarks:
    #     face_landmarks = face_results.multi_face_landmarks[0]
    #     mp_drawing.draw_landmarks(
    #         image,
    #         face_landmarks,
    #         mp_face_mesh.FACEMESH_CONTOURS,
    #         None,
    #         mp_drawing_styles.get_default_face_mesh_contours_style())
    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('You are being tracked lmao', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()