import cv2
import os,sys
import numpy as np

ascii_char = list(
    "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")

char_len = len(ascii_char)

# 视频容器
cap = cv2.VideoCapture('input.avi')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
outstream = cv2.VideoWriter('output.avi', fourcc, cap.get(5), (int(cap.get(3)), int(cap.get(4))))

if __name__ == "__main__":

    video_frame_count = cap.get(7)
    while cap.get(1) < video_frame_count:
        # get a frame
        ret, frame = cap.read()
        if not ret:
            print("Error")
            sys.exit(1)
        img = frame
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #使用opencv转化成灰度图
        bg_img=np.zeros(img.shape,dtype=np.uint8) #创建白板
        bg_img.fill(255)
        text = ""
        for pixel_line in range(0, len(gray), 5):
            for pixel in range(0, len(gray[pixel_line]), 5):                  #字符串拼接
                text = ascii_char[int(gray[pixel_line][pixel] / 256 * char_len )]
                cv2.putText(bg_img, text, (pixel, pixel_line), cv2.FONT_HERSHEY_COMPLEX, 0.2, 
                    (int(img[pixel_line][pixel][0]), 
                     int(img[pixel_line][pixel][1]), 
                     int(img[pixel_line][pixel][2])),1)
        outstream.write(bg_img)
    outstream.release()