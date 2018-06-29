import requests
import dicom
from PIL import Image
import glob
import os , shutil
url = "http://52.79.122.106:8000/upload"
retina_paths=glob.glob('/Users/seongjungkim/Desktop/retina_test/*.png')
cataract_path=glob.glob('/Users/seongjungkim/Desktop/cataract_test/*.png')
glau_paths=glob.glob('/Users/seongjungkim/Desktop/glau_Test/*.png')
normal_paths=glob.glob('/Users/seongjungkim/Desktop/normal_training/*.png')

#cataract_path=glob.glob('/Users/seongjungkim/Desktop/retinal/*.png')


files={}
result={}
f=open('retina_test.txt','w')
neg_count  =0
paths = normal_paths
for i,path in enumerate(paths[:]):


    files = {'file': open(path)}
    post_value=requests.post(url, files=files)
    result_cat = float(post_value.json().split('"value_cat": ')[1][:5].replace(',' ,''))
    result_gla = float(post_value.json().split('"value_gla": ')[1][:5].replace(',' ,''))
    result_ret = float(post_value.json().split('"value_ret": ')[1][:5].replace(',' ,''))
    print result_gla , result_cat , result_ret
    name=os.path.splitext(os.path.split(path)[-1])[0]
    f.write('path: {} \tcataract : {} glaucoma : {} retina : {}\n'.format(name , result_cat , result_gla , result_ret))

    result_ret, result_cat, result_gla=map(float , [result_ret , result_cat , result_gla])
    # negative sampels
    if float(result_ret) > 0.5 and float(result_cat) < 0.5 and float(result_gla) < 0.5 : # retina negative
        savedir ='/Users/seongjungkim/Desktop/negative/retina'
        neg_count +=1
    elif float(result_ret) < 0.5 and float(result_cat) > 0.5 and float(result_gla) < 0.5 : # cataract negative
        savedir = '/Users/seongjungkim/Desktop/negative/cataract'
        neg_count += 1
    elif float(result_ret) < 0.5 and float(result_cat) < 0.5 and float(result_gla) > 0.5: # glaucoma negative
        savedir = '/Users/seongjungkim/Desktop/negative/glaucoma'
        neg_count += 1
    elif float(result_ret) > 0.5 and float(result_cat) > 0.5 and float(result_gla) < 0.5: # retina cataract
        savedir = '/Users/seongjungkim/Desktop/negative/retina_cataract'
        neg_count += 1
    elif float(result_ret) > 0.5 and float(result_cat) < 0.5 and float(result_gla) > 0.5:  # retina glaucoma
        savedir = '/Users/seongjungkim/Desktop/negative/retina_glaucoma'
        neg_count += 1
    elif float(result_ret) < 0.5 and float(result_cat) > 0.5 and float(result_gla) > 0.5 : # cataract glaucoma
        savedir = '/Users/seongjungkim/Desktop/negative/cataract_glaucoma'
        neg_count += 1
    else:
        savedir = '/Users/seongjungkim/Desktop/negative/normal'
        pass; # normal
    dst_path= os.path.join(savedir, name+'.png')
    shutil.copy(path , dst_path)
print "Accuracy : {} ".format(neg_count/float(len(paths)))
print "negative : {}  / total : {}".format(neg_count , len(paths))
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
