import cv2
import os
import numpy as np
import dlib
import face_recognition

face_locations = []
face_encodings = []

### Path where images are present for testing
imagefolderpath = "Images/"

### Model for face detection
face_detector = dlib.get_frontal_face_detector()

for image in os.listdir(imagefolderpath):
    image = cv2.imread(os.path.join(imagefolderpath,image),1)

    t = time.time()
    faces = face_detector(image,0)
    for face in faces:
        x,y,w,h = face.left(),face.top(),face.right(),face.bottom()
        face_locations.append((x,y,h,w))
    face_encodings = face_recognition.face_encodings(image, known_face_locations = face_locations, num_jitters = 1)

    for (left, top, bottom, right) in face_locations:
        cv2.rectangle(image, (left,top), (right, bottom), (0, 0, 255), 2)
        cv2.imshow('Image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
