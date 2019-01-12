import cv2
import os,sys
import numpy as np

ascii_char = list(
    "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")

char_len = len(ascii_char)

# 视频容器
fourcc = cv2.VideoWriter_fourcc(*'XVID')
outstream = cv2.VideoWriter('./output.avi', fourcc, 10, (1080,960))

if __name__ == "__main__":

    # 获取当前工作目录
    curpath = os.getcwd()

    # 获取当前目录下的所有文件
    files = os.listdir(curpath)

    for curfile in files: # 遍历文件夹
        if os.path.isdir(curfile):
            continue
        if os.path.splitext(curfile)[-1][1:] != "jpg":
            continue
        img = cv2.imread(curfile)
        img = cv2.resize(img,(1080,960),interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #使用opencv转化成灰度图
        bg_img=np.zeros(img.shape,dtype=np.uint8) #创建白板
        bg_img.fill(255)
        text = ""
        for pixel_line in range(0, len(gray), 10):
            for pixel in range(0, len(gray[pixel_line]), 10):                  #字符串拼接
                text = ascii_char[int(gray[pixel_line][pixel] / 256 * char_len )]
                cv2.putText(bg_img, text, (pixel, pixel_line), cv2.FONT_HERSHEY_COMPLEX, 0.2, 
                    (int(img[pixel_line][pixel][0]), 
                     int(img[pixel_line][pixel][1]), 
                     int(img[pixel_line][pixel][2])),1)
        for i in range(5):
            outstream.write(bg_img)

        for pixel_line in range(0, len(gray), 10):
            for pixel in range(0, len(gray[pixel_line]), 10):                  #字符串拼接
                text = ascii_char[int(gray[pixel_line][pixel] / 256 * char_len )]
                cv2.putText(bg_img, text, (pixel, pixel_line), cv2.FONT_HERSHEY_COMPLEX, 0.2, 
                    (int(img[pixel_line][pixel][0]), 
                     int(img[pixel_line][pixel][1]), 
                     int(img[pixel_line][pixel][2])),2)
            if pixel_line%100 == 0:
                outstream.write(bg_img)

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
        for i in range(10):
            outstream.write(bg_img)
    outstream.release()

                

