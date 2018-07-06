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
L_path='/Users/seongjungkim/Desktop/artifact/118920_L.jpg'
R_path='/Users/seongjungkim/Desktop/artifact/118920_R.jpg'

date = '20180101'
pat_code = 1234
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