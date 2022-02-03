from cv2 import cv2 #cv2模块下还有cv2模块,这样写是为了让vscode不报错
import numpy as np
#import uuid
import os
from PIL import Image
import face_recognition
import shutil
import xlrd
import xlwt


dict_video={}#定义一个字典来存储视频的参数

#截取视频的帧
def cutVideo(path):
    i = 0
    video = cv2.VideoCapture(path) # 读取视频文件
    while(True):
        ret,frame = video.read()
        if ret==False:
            print("video path is wrong")
            break
        cv2.imshow('video',frame)
        c=cv2.waitKey(50)
        if c==27:
            break
        i=i+1
        if i%20==0:
            cv2.imwrite('F:/multi-media/video frames/'+str(i)+'.png',frame)

#获取视频的帧数和帧率
def videofps(path):
    video = cv2.VideoCapture(path) # 读取视频文件
    fps=video.get(5)#帧率
    fn=video.get(7)#帧数
    dict_video['fps']=fps
    dict_video['fn']=fn
    print(f"帧率={fps}")
    print(f"帧数={fn}")

#连续帧相减法
def diffimage(src_1,src_2):
    src_1 = src_1.astype(np.int)
    src_2 = src_2.astype(np.int)
    diff = abs(src_1 - src_2)
    return diff.astype(np.uint8)

#运用连续帧相减法求出关键帧
def keyframes():
    n=dict_video['fn']
    m=n%20
    n=n-m#n为最后一帧的文件名
    keyframe = 40
    while(keyframe<=n):
        exframe=cv2.imread("F:/multi-media/video frames/"+str(keyframe-20)+".png")
        frame= cv2.imread("F:/multi-media/video frames/"+str(keyframe)+".png")
        if np.sum(diffimage(exframe,frame))/frame.size > 27:
            cv2.imwrite("F:/multi-media/key frames/"+str(keyframe)+".png",frame)
        keyframe+=20 

#删除不存在人脸的帧
def face_rec(path):
    image = face_recognition.load_image_file(path)
    face_locations = face_recognition.face_locations(image)
    if len(face_locations)<1:
        os.remove(path)
    else:
        print(path+"I found {} face(s) in this photograph:".format(len(face_locations)))

#获取三位嘉宾的面部编码
def face_code():
    #获取嘉宾1 罗朗的面部编码
    image1 = face_recognition.load_image_file("F:/multi-media/video frames/260.png")
    face_encodings_1 = face_recognition.face_encodings(image1)
    dict_video.update({"罗朗": face_encodings_1})
    #获取嘉宾2 陈晓卿面部编码
    image2 = face_recognition.load_image_file("F:/multi-media/video frames/2780.png")
    face_encoding_2 = face_recognition.face_encodings(image2)
    dict_video.update({"陈晓卿": face_encoding_2})
    #获取嘉宾2 梁文道面部编码
    image3 = face_recognition.load_image_file("F:/multi-media/video frames/620.png")
    face_encoding_3 = face_recognition.face_encodings(image3)
    dict_video.update({"梁文道": face_encoding_3})
    #获取嘉宾2 窦文涛面部编码
    image4 = face_recognition.load_image_file("F:/multi-media/video frames/1260.png")
    face_encoding_4 = face_recognition.face_encodings(image4)
    dict_video.update({"窦文涛": face_encoding_4})

#获取真正的关键帧
def real_key_frames():
    path="F:/multi-media/key frames"
    path_list=os.listdir(path)
    i=0
    j=0
    k=0
    for i in range(731):
        path_list[i]=path_list[i][0:-4]
        path_list[i]=int(path_list[i])
    path_list.sort() #对读取的路径进行排序
    for j in range(731):
        path_list[j]="F:/multi-media/key frames/"+str(path_list[j])+".png"
    
    for k in range(730):
        imagek = face_recognition.load_image_file(path_list[k])
        known_face = face_recognition.face_encodings(imagek)
        imagec = face_recognition.load_image_file(path_list[k+1])
        face_to_check = face_recognition.face_encodings(imagec)
        ED = np.linalg.norm(known_face[0]-face_to_check[0])#计算欧氏距离
        if ED<0.45:
            print(path_list[k+1]+"is not real key frame")
        else:
            print(path_list[k+1]+"is real key frame")
            shutil.copy(path_list[k+1],"F:/multi-media/real key frames/"+path_list[k+1][26:])
    shutil.copy("F:/multi-media/real key frames/"+path_list[0][26:],"F:/multi-media/real key frames/"+path_list[0][26:])

def opexcel():
    book = xlwt.Workbook()
    sheet = book.add_sheet('Sheet1')
    # sheet.write(0,0,'name')  #行,列,内容
    title = ['镜头切换点序号', '文件名','时间', '嘉宾姓名']
    #写入表头
    i = 0
    for j in title:
        sheet.write(0,i,j)
        i+=1
    FPS=dict_video['fps']
    path="F:/multi-media/real key frames"
    path_list=os.listdir(path)
    for i in range(486):
        path_list[i]=path_list[i][0:-4]
        path_list[i]=int(path_list[i])
    path_list.sort() #对读取的路径进行排序
    sheet.write(1,0,0)
    sheet.write(1,2,"0 s")
    for j in range(486):
        frames_number=int(path_list[j])
        time=frames_number/FPS
        sheet.write(j+2,1,str(frames_number)+'.png')
        sheet.write(j+2,0,j+1)
        sheet.write(j+2,2,str(time)+" s")
    image1_code = dict_video["罗朗"]
    image2_code = dict_video["陈晓卿"]
    image3_code = dict_video["梁文道"]
    image4_code = dict_video["窦文涛"]
    for k in range(486):
        imagek = face_recognition.load_image_file("F:/multi-media/real key frames/"+str(path_list[k])+".png")
        known_face = face_recognition.face_encodings(imagek)
        ED1 = np.linalg.norm(known_face[0]-image1_code[0])
        ED2 = np.linalg.norm(known_face[0]-image2_code[0])
        ED3 = np.linalg.norm(known_face[0]-image3_code[0])
        ED4 = np.linalg.norm(known_face[0]-image4_code[0])
        key=min(ED1,ED2,ED3,ED4)  
        if key==ED1:
            sheet.write(k+2,3,"罗朗")
        if key==ED2:
            sheet.write(k+2,3,"陈晓卿")
        if key==ED3:
            sheet.write(k+2,3,"梁文道")
        if key==ED4:
            sheet.write(k+2,3,"窦文涛")
    book.save("F:/multi-media/keyframes.xlsx")


#获取视频帧率
videofps('F:/multi-media/video.mp4')
#每20帧保存一次截图
cutVideo('F:/multi-media/video.mp4')
cv2.destroyAllWindows()
#获取关键帧
keyframes()
#删除不存在人脸的帧
path="F:/multi-media/key frames"
dirs=os.listdir(path)
for file in dirs:
    face_rec("F:/multi-media/key frames/"+file)
#获取人物面部编码
face_code()
#删除重复出现的人物的帧获取真正地关键帧
real_key_frames()
#写入表格
opexcel()