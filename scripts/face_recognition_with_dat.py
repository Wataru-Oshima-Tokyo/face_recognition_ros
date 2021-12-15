#!/usr/bin/env python
# --*-- coding: utf-8 -*-

import cv2 
import numpy as np
import dlib 
import face_recognition
from sensor_msgs.msg import Image
import rospy
import cv_bridge
import numpy as np
from geometry_msgs.msg import Twist
import platform
import pickle
from datetime import datetime, timedelta

class FACE():
    def __init__(self):
        print("__init__")
        self.bridge = cv_bridge.CvBridge()
        self.load_known_faces()
        self.known_face_encodings = []
        self.known_face_metadata = []
        self.image_test= face_recognition.load_image_file('/home/jetson/catkin_ws/src/face_recognition_ros/images/test.jpg')
        # self.image_test=cv2.cvtColor(self.image_src, cv2.COLOR_BGR2GRAY)
        # 		self.encode_test=face_recognition.face_encodings(self.image_test, model="cnn")[0]
        self.image_sub = rospy.Subscriber('/camera/color/image_raw', Image, self.image_callback)   #Image型で画像トピックを購読し，コールバック関数を呼ぶ
        self.cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
        self.twist = Twist()    #Twistインスタンス生成

    def image_callback(self,msg):
        self.image_src = self.bridge.imgmsg_to_cv2(msg, desired_encoding = 'bgr8')
        ## NEW ##
        # 		self.enocode_image = face_recognition.face_encodings(self.image_src, model="cnn")[0]
        # 		self.recognize()
        self.recognize(self)
        cv2.imshow("Result", self.image_src)
        cv2.waitKey(3)


    def recognize(self):
        # Resize frame of video to 1/4 size for faster face recognition processing
        self.image_src = cv2.resize(self.image_src, (0, 0), fx=0.25, fy=0.25)
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = self.image_src[:, :, ::-1]

        # Find all the face locations and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame,model="cnn")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations, model="cnn")
                # Loop through each detected face and see if it is one we have seen before
        # If so, we'll give it a label that we'll draw on top of the video.
        face_labels = []
        for face_location, face_encoding in zip(face_locations, face_encodings):
            # See if this face is in our list of known faces.
            metadata = self.lookup_known_face(face_encoding)

            # If we found the face, label the face with some useful information.
            if metadata is not None:
                time_at_door = datetime.now() - metadata['first_seen_this_interaction']
                face_label = "Wataru"

            # If this is a brand new face, add it to our list of known faces
            else:
                face_label = "New visitor!"

                # Grab the image of the the face from the current frame of video
                top, right, bottom, left = face_location
                face_image = self.image_src[top:bottom, left:right]
                face_image = cv2.resize(face_image, (150, 150))

                # Add the new face to our known face data
                self.register_new_face(face_encoding, face_image)

            face_labels.append(face_label)

        # Draw a box around each face and label each face
        for (top, right, bottom, left), face_label in zip(face_locations, face_labels):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(self.image_src, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(self.image_src, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(self.image_src, face_label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        # Display recent visitor images
        number_of_recent_visitors = 0
        for metadata in self.known_face_metadata:
            # If we have seen this person in the last minute, draw their image
            if datetime.now() - metadata["last_seen"] < timedelta(seconds=10) and metadata["seen_frames"] > 5:
                # Draw the known face image
                x_position = number_of_recent_visitors * 150
                self.image_src[30:180, x_position:x_position + 150] = metadata["face_image"]
                number_of_recent_visitors += 1

                # Label the image with how many times they have visited
                visits = metadata['seen_count']
                visit_label = "Visit"
                if visits == 1:
                    visit_label = "First visit"
                cv2.putText(self.image_src, visit_label, (x_position + 10, 170), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        if number_of_recent_visitors > 0:
            cv2.putText(self.image_src, "Visitors at Door", (5, 18), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
    
    def save_known_faces(self):
        with open("known_faces.dat", "wb") as face_data_file:
            face_data = [self.known_face_encodings, self.known_face_metadata]
            pickle.dump(face_data, face_data_file)
            print("Known faces backed up to disk.")
    
    def register_new_face(self,face_encoding, face_image):
        """
        Add a new person to our list of known faces
        """
        # Add the face encoding to the list of known faces
        self.known_face_encodings.append(face_encoding)
        # Add a matching dictionary entry to our metadata list.
        # We can use this to keep track of how many times a person has visited, when we last saw them, etc.
        self.known_face_metadata.append({
            "first_seen": datetime.now(),
            "first_seen_this_interaction": datetime.now(),
            "last_seen": datetime.now(),
            "seen_count": 1,
            "seen_frames": 1,
            "face_image": face_image,
        })

    def lookup_known_face(self, face_encoding):
        """
        See if this is a face we already have in our face list
        """
        metadata = None

        # If our known face list is empty, just return nothing since we can't possibly have seen this face.
        if len(self.known_face_encodings) == 0:
            return metadata

        # Calculate the face distance between the unknown face and every face on in our known face list
        # This will return a floating point number between 0.0 and 1.0 for each known face. The smaller the number,
        # the more similar that face was to the unknown face.
        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

        # Get the known face that had the lowest distance (i.e. most similar) from the unknown face.
        best_match_index = np.argmin(face_distances)

        # If the face with the lowest distance had a distance under 0.6, we consider it a face match.
        # 0.6 comes from how the face recognition model was trained. It was trained to make sure pictures
        # of the same person always were less than 0.6 away from each other.
        # Here, we are loosening the threshold a little bit to 0.65 because it is unlikely that two very similar
        # people will come up to the door at the same time.
        if face_distances[best_match_index] < 0.65:
            # If we have a match, look up the metadata we've saved for it (like the first time we saw it, etc)
            metadata = self.known_face_metadata[best_match_index]

            # Update the metadata for the face so we can keep track of how recently we have seen this face.
            metadata["last_seen"] = datetime.now()
            metadata["seen_frames"] += 1

            # We'll also keep a total "seen count" that tracks how many times this person has come to the door.
            # But we can say that if we have seen this person within the last 5 minutes, it is still the same
            # visit, not a new visit. But if they go away for awhile and come back, that is a new visit.
            if datetime.now() - metadata["first_seen_this_interaction"] > timedelta(minutes=5):
                metadata["first_seen_this_interaction"] = datetime.now()
                metadata["seen_count"] += 1

        return metadata


if __name__ == "__main__":
    print("Start")
    rospy.init_node('follower')
    fc = FACE()
    rospy.spin()
