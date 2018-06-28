import requests
import dicom
from PIL import Image
import glob
import os
url = "http://52.79.122.106:8000/upload"
glau_paths=glob.glob('/Users/seongjungkim/Desktop/glau_Test/*.png')
normal_paths=glob.glob('/Users/seongjungkim/Desktop/normal_Test/*.png')
retina_paths=glob.glob('/Users/seongjungkim/Desktop/retina_test/*.png')
cataract_path=glob.glob('/Users/seongjungkim/Desktop/cataract_test/*.png')
#cataract_path=glob.glob('/Users/seongjungkim/Desktop/retinal/*.png')

files={}

result={}

f=open('retina_test.txt','w')
for i,path in enumerate(retina_paths[:]):
    files = {'file': open(path)}
    post_value=requests.post(url, files=files)
    result_cat = float(post_value.json().split('"value_cat": ')[1][:5].replace(',' ,''))
    result_gla = float(post_value.json().split('"value_gla": ')[1][:5].replace(',' ,''))
    result_ret = float(post_value.json().split('"value_ret": ')[1][:5].replace(',' ,''))
    print result_gla , result_cat , result_ret
    name=os.path.splitext(os.path.split(path)[-1])[0]
    f.write('path: {} \tcataract : {} glaucoma : {} retina : {}\n'.format(name , result_cat , result_gla , result_ret))
f.close()

"""
#files = {'file': open('/Users/seongjungkim/PycharmProjects/web_classifier/fundus_classifier/5217696_20141224_L.png')}
post_value=requests.post(url, files=files)
print post_value.json()
print float(post_value.json().split('"value_cat": ')[1][:5])
print float(post_value.json().split('"value_gla": ')[1][:5])
print float(post_value.json().split('"value_ret": ')[1][:5])
save_root_folder='./'
folder_n = 0
"""



"""

dc=dicom.read_file('/Users/seongjungkim/PycharmProjects/web_classifier/SC.1.2.410.200013.6.510.1.20170331115919.1699.1.1')
print dc.PatientName
try:
    dicom.read_file('/Users/seongjungkim/PycharmProjects/web_classifier/fundus_classifier/2659775_20160513_L')
except dicom.errors.InvalidDicomError:
    print 'a'
Image.open('/Users/seongjungkim/PycharmProjects/web_classifier/fundus_classifier/2659775_20160513_L')
"""
