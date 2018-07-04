#-*- coding:utf-8 -*-
import requests
import dicom
from PIL import Image
import glob
import os , shutil
import cv2
import numpy as np
def detect_brigthArtifact(np_img):

    img = np_img
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    mark = (gray > 220).astype(np.uint8)

    # inside　기준을　ratio = 0.8로　잡음

    part = np.ones(gray.shape, dtype=np.uint8)
    center_pos = np.array(gray.shape[:2]) // 2
    radius = int(center_pos.min() * 0.8)
    cv2.circle(part, tuple(center_pos), radius, 0, -1)

    blank = np.zeros_like(img)
    mark = cv2.bitwise_and(mark, mark, mask=part)
    # artifact가　총　면적의　２％　이상이면　검출되었다고　판단
    #artfect 검출
    artifact_ratio = mark.sum() / (mark.shape[0] * mark.shape[1])


    return artifact_ratio


"""
# Bright Spot imag except outside
# 외곽의　기준을　ratio = 0.99로　잡음　（ 대부분　이미지가　외각의　경우　좀　더　밝게　찍힘　그래서　그건　무시）
part = np.zeros(gray.shape, dtype=np.uint8)
center_pos = np.array(gray.shape[:2]) // 2
radius = int(center_pos.min() * 0.99)
cv2.circle(part, tuple(center_pos), radius, 1, -1)

mark = cv2.bitwise_and(mark, mark, mask=part)
"""

def detect_darkArtifact(np_img):
    img = np_img
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.GaussianBlur(img, (11, 11), 0)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    mark = (gray < 40).astype(np.uint8)

    # 외곽의　기준을　ratio = 0.99로　잡음　（ 대부분　이미지가　외각의　경우　좀　더　밝게　찍힘　그래서　그건　무시）
    part = np.zeros(gray.shape, dtype=np.uint8)
    center_pos = np.array(gray.shape[:2]) // 2
    radius = int(center_pos.min() * 0.99)
    cv2.circle(part, tuple(center_pos), radius, 1, -1)

    mark = cv2.bitwise_and(mark, mark, mask=part)

    # artifact가　총　면적의　２％　이상이면　검출되었다고　판단
    dark_ratio = mark.sum() / (mark.shape[0] * mark.shape[1])

    return dark_ratio
url = "http://52.79.122.106:8000/upload"
files={}
result={}
f=open('retina_test.txt','w')
neg_count  =0
path = '2908521_20160809_R.png.png'

files = {'file': open(path)}
post_value=requests.post(url, files=files)
print post_value.json()

img=Image.open(path)
img=np.asarray(img)
print detect_brigthArtifact(img)
print detect_darkArtifact(img)
img=Image.open('./abnormal_sample.png')
img=Image.open('./normal_sample.png')
print np.shape(img)