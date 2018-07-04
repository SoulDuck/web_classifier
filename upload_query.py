# -*- coding: utf-8 -*-
import requests
import glob , os


#### login ######

url = "http://ec2-13-209-32-216.ap-northeast-2.compute.amazonaws.com/login"
data = {"member_id":"aptos2018","member_pw":"q1w2e3r4"}

s = requests.Session()
s.post(url, data=data)

#####################


######### upload #################

url = "http://ec2-13-209-32-216.ap-northeast-2.compute.amazonaws.com/upload"

paths=glob.glob('/Users/seongjungkim/Desktop/Test/*.png')
for path in paths:
    img_dir  , name=os.path.split(path)
    name=os.path.splitext(name)[0]
    name = name.replace('_L' ,'').replace('_R' ,'')
    pat_code , date = name.split('_')
    L_path = os.path.join(img_dir, name + '_L.png')
    R_path = os.path.join(img_dir, name + '_R.png')

    if os.path.exists(L_path) and os.path.exists(R_path) and len(date) ==8:
        print 'patitent Code : {} , date : {}'.format(pat_code,  date)
        files = {'file1': open(L_path), 'file2': open(R_path)}
        data = {"patient_id":pat_code,"exam_date":date}
        response = s.post(url,files=files,data=data)
        print response
exit()
"""
for path in paths:
    files = {'file1': open('/Users/mac-pc/Downloads/activationmap3.png'),'file2': open(path)}

data = {"patient_id":"9394849","exam_date":"20180606"}

response = s.post(url,files=files,data=data)
print response.json()


###################################
"""