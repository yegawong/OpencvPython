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
from os import listdir
from os.path import isfile, join,splitext,basename
import urllib
import urllib2
from Queue import Queue


REPORT_URL = "http://192.168.10.200:7000/GetInScanCode"
ReportTime = time.time()
# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(1)
encoding_que=Queue()
#提取所有文件到内存
encoding_npy=[]
encoding_npy_name=[]
encoding_npy_code=[]
#存储人脸到文件和内存
encoding_temp_npy=[]
encoding_temp_npy_name=[]
encoding_temp_npy_code=[]

def ReportCardnumber(membership_name,membership_code):
    global ReportTime
    TimeGap = time.time() - ReportTime
    if TimeGap <= 5: #5s
        return
    else:
        ReportTime = time.time()

    global REPORT_URL
    for i in range(5):
        try:
            headers = {'Content-Type': 'application/json'}
            rdata = {"vgdecoderesult":membership_code , "devicenumber":"enter_qrscanner"}
            req = urllib2.Request(url = REPORT_URL, headers = headers, data = json.dumps(rdata))
            res_data = urllib2.urlopen(req, timeout=1)
            res = res_data.read()
            #print res
            logging.info("post response:Name: "+ membership_name + " membership_code: " + membership_code + " " + res)
            break
        except Exception, e:
            logging.error("report failed e:" + str(e))
            return

def Load_Npy():
    global encoding_npy
    global encoding_npy_name
    global encoding_npy_code

    onlyfiles = [f for f in listdir('./encodings/') if isfile(join('./encodings/', f))]
    for i in range(len(onlyfiles)):
        name, ext = splitext(onlyfiles[i])
        if '.npy' != ext:
            continue
        known_face_encoding = np.load('./encodings/'+ basename(onlyfiles[i]))
        membership_name = u''+name.split('_')[0]
        membership_code = u''+name.split('_')[1]
        encoding_npy.append(known_face_encoding)
        encoding_npy_name.append(membership_name)
        encoding_npy_code.append(membership_code)

def FaceRecognitionMatch():
    global encoding_que
    global encoding_que_mutex
    global video_capture
    while video_capture.isOpened():
        # Grab a single frame of video
        ret, frame = video_capture.read()
        if not ret:
            continue
        #print "read video"

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.6, fy=0.6)
        # Find all the faces and face enqcodings in the frame of video
        face_locations = face_recognition.face_locations(small_frame)
        #print "face locations"
        if len(face_locations):
            #print "face encodings"
            top = long(float(face_locations[0][0])/0.6 + 0.5)
            right = long(float(face_locations[0][1])/0.6 + 0.5)
            bottom = long(float(face_locations[0][2])/0.6 + 0.5)
            left = long(float(face_locations[0][3])/0.6 + 0.5)
            list=[]
            list.append(tuple([top, right, bottom, left]))
            face_encoding = face_recognition.face_encodings(rgb_frame, list)

            #face_locations = face_recognition.face_locations(rgb_frame)
            #face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)
            if not face_encoding:
                continue
            encoding_que.put(face_encoding)
        else:
            pass

def FaceRecognition():
    global encoding_npy
    global encoding_npy_name
    global encoding_npy_code

    global encoding_temp_npy
    global encoding_temp_npy_name
    global encoding_temp_npy_code

    global encoding_que
    global encoding_que_mutex

    while True:
        if not encoding_que.empty():
            #print "detect face"
            face_encoding = encoding_que.get()
            if not face_encoding:
                continue

            encoding_temp_flag = False
            for j in range(len(encoding_temp_npy)):
                matches = face_recognition.compare_faces(encoding_temp_npy[j], face_encoding,tolerance=0.35)
                if True in matches:
                    ReportCardnumber(encoding_temp_npy_name[j],encoding_temp_npy_code[j])
                    encoding_temp_flag = True
                    break
            if not encoding_temp_flag:
                for i in range(len(encoding_npy)):
                    matches = face_recognition.compare_faces(encoding_npy[i], face_encoding,tolerance=0.35)
                    # If a match was found in known_face_encodings, just use the first one.
                    if True in matches:
                        ReportCardnumber(encoding_npy_name[i],encoding_npy_code[i])
                        np.save('./encodings/' + encoding_npy_name[i] + '_' + encoding_npy_code[i] + '_temp' + '.npy',face_encoding)
                        known_face_encoding = np.load('./encodings/' + encoding_npy_name[i] + '_' + encoding_npy_code[i] + '_temp' + '.npy')
                        encoding_temp_npy.append(known_face_encoding)
                        encoding_temp_npy_name.append(encoding_npy_name[i])
                        encoding_temp_npy_code.append(encoding_npy_code[i])
                        break
            encoding_que=Queue()    
        else:
            pass

def FaceRecognitionQuit(signum,frame):
    global video_capture
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    sys.exit()

def main():
    #print "Start"
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

    #打开face_recognition_x_t线程
    face_recognition_match = threading.Thread(target=FaceRecognitionMatch)
    face_recognition_match.setDaemon(True)
    face_recognition = threading.Thread(target=FaceRecognition)
    face_recognition.setDaemon(True)

    face_recognition_match.start()
    face_recognition.start()

    while face_recognition_match.isAlive() and face_recognition.isAlive():
        time.sleep(5)

    logging.error("Quit")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, FaceRecognitionQuit)
    signal.signal(signal.SIGTERM, FaceRecognitionQuit)
    try:
        Load_Npy()
        main()
    except Exception, e:
        logging.error(str(e))
