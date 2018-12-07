#!/usr/bin/env python
# -*- coding: utf-8 -*-

import face_recognition
import cv2
import json
import logging
import time
import sys
import threading, signal
import numpy as np

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(1)
face_name=''
membership_code = ''

def FaceRegisterDetect():
    global video_capture
    global face_name
    i = 0
    while True:
        # Hit 'q' on the keyboard to quit!
        if(i%10 == 0):
            print("Detecting...")
        if(i>999):
            i = 0
        # Grab a single frame of video
        
        i+=1

        ret,frame = video_capture.read()
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]

        # Find all the faces and face enqcodings in the frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if len(face_locations):
            print face_locations
            # Store this frame to an image
            cv2.imwrite('./pic/' + face_name + '.jpg', frame)
            break
        #cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            FaceRegisterQuit();
            break

    for (top, right, bottom, left),face_encoding in zip(face_locations,face_encodings):
        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Store this frame to an image
        cv2.imwrite('./pic/' + face_name + '_rectangle' + '.jpg', frame)

        return face_encoding

def FaceRegister():
    global face_name,membership_code
    print "开始注册人脸程序"
    while True:
        face_name = raw_input("请输入注册者姓名（英文缩写不能出现'.'）：")
        membership_code = raw_input("请输入本人会员码（数字）：")
        face_encoding = FaceRegisterDetect()

        np.save('./encodings/' + face_name + '_' + membership_code + '.npy',face_encoding)
        # arch = np.load('./encodings/' + face_name + '_face_encodings.npy')

        waitkey = raw_input("按 'D' 退出程序：")
        if ord(waitkey) in [68, 100]:
            FaceRegisterQuit()
            break

def FaceRegisterQuit():
    global video_capture

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    sys.exit()

def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='./log/face_recognition.log',
                        filemode='a+')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # signal.signal(signal.SIGINT, FaceRegisterQuit)
    # signal.signal(signal.SIGTERM, FaceRegisterQuit)

    FaceRegister()


if __name__ == '__main__':
    main()
