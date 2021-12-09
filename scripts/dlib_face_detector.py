
#!/usr/bin/env python
# --*-- coding: utf-8 -*-

import cv2
import os
import numpy as np
import dlib
import face_recognition
class DLIB_FACE():
    def __init__(self):
        print("__init__")
		self.bridge = cv_bridge.CvBridge()
		self.image_test= face_recognition.load_image_file('/home/jetson/catkin_ws/src/face_recognition_ros/images/test.jpg')
		# self.image_test=cv2.cvtColor(self.image_src, cv2.COLOR_BGR2GRAY)
		self.encode_test=face_recognition.face_encodings(self.image_test)[0]
		self.image_sub = rospy.Subscriber('/camera/color/image_raw', Image, self.image_callback)   #Image型で画像トピックを購読し，コールバック関数を呼ぶ
		self.cmd_vel_pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
		self.twist = Twist()    #Twistインスタンス生成
        self.face_locations = []
        self.face_encodings = []
    
  	def image_callback(self,msg):
		self.image_src = self.bridge.imgmsg_to_cv2(msg, desired_encoding = 'bgr8')
		## NEW ##
# 		self.enocode_image = face_recognition.face_encodings(self.image_src)[0]
# 		self.recognize()
# 		cv2.imshow("Result", self.image_src)
# 		cv2.waitKey(3)  



        ### Path where images are present for testing
        imagefolderpath = "Images/"

        ### Model for face detection
        face_detector = dlib.get_frontal_face_detector()


        t = time.time()
        faces = face_detector(self.image_src,0)
        for face in faces:
            x,y,w,h = face.left(),face.top(),face.right(),face.bottom()
            face_locations.append((x,y,h,w))
        face_encodings = face_recognition.face_encodings(image, known_face_locations = face_locations, num_jitters = 1, model="cnn")

        for (left, top, bottom, right) in face_locations:
            cv2.rectangle(self.image_src, (left,top), (right, bottom), (0, 0, 255), 2)
            cv2.imshow('Image', self.image_src)
            cv2.waitKey(3)
if __name__ == "__main__":
	print("Start")
	rospy.init_node('follower')
	fc = DLIB_FACE()
	rospy.spin()
