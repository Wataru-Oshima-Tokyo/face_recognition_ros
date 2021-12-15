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

class FACE():
	def __init__(self):
		print("__init__")
		self.bridge = cv_bridge.CvBridge()
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
		cv2.imshow("Result", self.image_src)
		cv2.waitKey(3)
		
    def recognize(self):
 		try:
			# self.image_src = cv2.cvtColor(self.image_src, cv2.COLOR_BGR2GRAY)
			floc = face_recognition.face_locations(self.image_src, model="cnn")[0]
			self.encode_face = face_recognition.face_encodings(self.image_src, model="cnn")[0]
			cv2.rectangle(self.image_src,(floc[3],floc[0]),(floc[1],floc[2]),(255,0,255),2)
			self.compare()
		except:
			print("no face recognized")
			
	def compare(self):
		self.name = "Wataru"
		self.result = face_recognition.compare_faces([self.encode_face],self.encode_test)[0]
		self.faceDis = face_recognition.face_distance([self.encode_face],self.encode_test)[0]
		print(self.result,self.faceDis)
		# if self.faceDis <.45:
		# 	cv2.putText(self.image_src, f'{self.name}{round(self.faceDis,2)}',(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)

if __name__ == "__main__":
	print("Start")
	rospy.init_node('follower')
	fc = FACE()
	rospy.spin()
