#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import threading, signal
import Queue
import numpy as np
import sys,os
import time
import argparse

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--input', type=str, default = None)
parser.add_argument('--output', type=str, default= None)
parser.add_argument('--parallel', type=int, default=1)
args = parser.parse_args()
if not args.input or not args.output or not args.parallel:
    print "usage: convertVideo.py [-h] [--input=color_video_file] [--output=block&white_video_file] [--parallel=int]"
    sys.exit()
path,file=os.path.split(args.output);
if not os.path.exists(path):
    os.makedirs(args.output)
if not os.path.isfile(args.output):
    os.system(r"touch {}".format(args.output))
cap = cv2.VideoCapture(args.input)
video_frame_count = cap.get(7)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(args.output, fourcc, cap.get(5), (int(cap.get(3)), int(cap.get(4))), 0)
frame_que = Queue.Queue()#视频帧队列
frame_mutex = threading.Lock()#读取视频帧信号量
thresh_que = Queue.PriorityQueue()#二值化后的视频帧优先队列
thresh_frame_count = 0 #存储帧数
convert_frame_mutex = threading.Lock()#转换视频帧信号量
convert_frame_count = 0

#优先队列类
class Job(object):
    def __init__(self, frame_count, frame):
        self.frame_count = frame_count
        self.frame = frame
        return
    def __cmp__(self, other):
        return cmp(self.frame_count, other.frame_count)

#保存二值化后的视频帧
def save_thresh_frame():
    global thresh_que,out,video_frame_count,thresh_frame_count
    while True:
        if not thresh_que.empty():
            next_job = thresh_que.get()
            thresh_que.task_done()
            if thresh_frame_count+1 == next_job.frame_count:
                thresh_frame_count = next_job.frame_count
                out.write(next_job.frame)
            else:
               thresh_que.put(Job(next_job.frame_count, next_job.frame))
        if thresh_frame_count == video_frame_count:
            break

#自适应阈值
def custom_threshold(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)  #把输入帧灰度化
    h, w =gray.shape[:2]
    m = np.reshape(gray, [1,w*h])
    mean = m.sum()/(w*h)#求出平均值
    ret, thresh = cv2.threshold(gray, mean, 255, cv2.THRESH_BINARY)
    return ret, thresh

#转换图像并保存
class convert_frame(threading.Thread):
    def __init__(self,threadname):
        threading.Thread.__init__(self,name=threadname)
    def run(self):
        global frame_que,thresh_que,thresh_frame_count,video_frame_count,convert_frame_mutex,convert_frame_count
        while True:
            if not frame_que.empty():
                frame_count, frame_frame = frame_que.get()
                ret, thresh = custom_threshold(frame_frame)
                thresh_que.put(Job(frame_count, thresh))
                if convert_frame_mutex.acquire():
                    convert_frame_count = convert_frame_count + 1
                    convert_frame_mutex.release()
                frame_que.task_done()
            if convert_frame_count == video_frame_count:
                break

#读取视频流
class read_frame(threading.Thread):
    def __init__(self,threadname):
        threading.Thread.__init__(self,name=threadname)
    def run(self):
        global cap, video_frame_count,frame_mutex
        while cap.get(1) < video_frame_count:
            if frame_mutex.acquire():
                # get a frame
                ret, frame = cap.read()
                if ret:
                    frame_que.put((cap.get(1), frame))
                frame_mutex.release()

def quit(signum,frame):
    global cap,out
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    sys.exit()

#主函数
def main():
    starttime= time.time()
    global args
    for i in range(args.parallel):
        thread1 = read_frame(i)
        thread2 = convert_frame(i)
        thread1.setDaemon(True)
        thread2.setDaemon(True)
        thread1.start()
        thread2.start()
    save_thresh_frame()
    print "UseTime(s):",str(time.time()-starttime)
if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    main()