
import requests
import cv2
import mediapipe as mp
import numpy as np
import time

ESP32_URL = "http://172.20.10.4"   

class VideoFrameHandler:
    def __init__(self):
        self.start_time = None
        self.play_alarm = False

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def eye_aspect_ratio(self, landmarks, eye_indices):
        p1 = np.array([landmarks[eye_indices[0]].x, landmarks[eye_indices[0]].y])
        p2 = np.array([landmarks[eye_indices[1]].x, landmarks[eye_indices[1]].y])
        p3 = np.array([landmarks[eye_indices[2]].x, landmarks[eye_indices[2]].y])
        p4 = np.array([landmarks[eye_indices[3]].x, landmarks[eye_indices[3]].y])
        p5 = np.array([landmarks[eye_indices[4]].x, landmarks[eye_indices[4]].y])
        p6 = np.array([landmarks[eye_indices[5]].x, landmarks[eye_indices[5]].y])

        vertical1 = np.linalg.norm(p2 - p6)
        vertical2 = np.linalg.norm(p3 - p5)
        horizontal = np.linalg.norm(p1 - p4)
        if horizontal == 0:
            return 0.0
        return (vertical1 + vertical2) / (2.0 * horizontal)

    def process(self, frame, thresholds):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        EAR_THRESH = thresholds.get("EAR_THRESH", 0.25)
        WAIT_TIME = thresholds.get("WAIT_TIME", 0.8)

        ear = None

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:

                left_eye_idx = [33, 160, 158, 133, 153, 144]
                right_eye_idx = [362, 385, 387, 263, 373, 380]

                ear_left = self.eye_aspect_ratio(face_landmarks.landmark, left_eye_idx)
                ear_right = self.eye_aspect_ratio(face_landmarks.landmark, right_eye_idx)
                ear = (ear_left + ear_right) / 2.0

                # Draw EAR on screen
                cv2.putText(frame, f"EAR: {ear:.2f}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                if ear < EAR_THRESH:
                    if self.start_time is None:
                        self.start_time = time.time()
                    elif time.time() - self.start_time > WAIT_TIME:
                        self.play_alarm = True
                else:
                    self.start_time = None
                    self.play_alarm = False

        
        try:
            if self.play_alarm:
                requests.get(ESP32_URL + "/on")
                cv2.putText(frame, "WAKE UP!", (50, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            else:
                requests.get(ESP32_URL + "/off")
        except:
            pass

        return frame, self.play_alarm
