# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
import web_classifier.settings as settings
from forms import *
from PIL import Image
import numpy as np
import time
import os
import json
import tensorflow as tf
from django.core import serializers
from eval import  load_model  , get_pred , eval_inspect_cam , clahe_equalized , sess_ret_ops , sess_gla_ops , sess_cat_ops
from utils import get_patinfo , dicom_checker , fundus_laterality , crop_margin_fundus
import dicom
# Create your views here.
#/Users/seongjungkim/PycharmProjects/web_classifier/models
#/home/ubuntu/web_classifier
from django.views.decorators.csrf import csrf_exempt

def handle_uploaded_file(f , savepath):
    with open(savepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = UploadForm(request.POST , request.FILES)
        sess_ret, pred_op_ret, x_ret, y_ret, is_training_ret, top_conv_ret, cam_ret, cam_ind_ret, logits_ret = sess_ret_ops
        if form.is_valid():
            form.save()
            ret_json = []
            #fnames=str(request.FILES['file']) for f in request.FILES.getlist('file'):
            fnames = [ ]
            """
            for i ,key in enumerate(request.FILES):
                fname = str(request.FILES[key])
                fnames.append(fname)


            assert fnames == 3, '{}'.format(fnames)
            """
            for i,key in enumerate(request.FILES):
                fname=str(request.FILES[key])
                file=request.FILES[key]
                # load Image
                f_path=os.path.join(settings.MEDIA_ROOT , fname)

                pat_id, pat_name , exam_date, exam_time = None , None , None ,None
                # dicom check
                handle_uploaded_file(f=file, savepath=f_path)
                if dicom_checker(f_path):
                    pat_id, pat_name ,exam_date, exam_time , img = get_patinfo(f_path)
                else: # PNG , JPEG , JPG ...etc
                    img = Image.open(request.FILES[key])
                    #img.save(f_path)
                    img = Image.open(f_path)
                # LR_checker
                LR = fundus_laterality(img) # 0 : LEFT , 1 L RIGHT
                print LR

                img = crop_margin_fundus(img)
                # Multiple Images
                img = np.asarray(img.resize([300, 300], Image.ANTIALIAS).convert('RGB'))
                img = clahe_equalized(img)

                #value_ret, value_gla, value_cat = 0.3 , 0.7 ,0.3
                value_ret, value_gla , value_cat = get_pred(img , sess_ret_ops , sess_gla_ops ,sess_cat_ops)


                actmap_dir = '/Users/seongjungkim/PycharmProjects/web_classifier/media/actmap'
                actmap_dir = '/home/ubuntu/web_classifier/media/actmap'
                np_img=np.asarray(img).reshape([1]+list(np.shape(img)))
                actmap_path , origina_path =eval_inspect_cam(sess_ret, cam_ret, cam_ind_ret, top_conv_ret, np_img, x_ret, y_ret, is_training_ret,
                                 logits_ret, actmap_dir)
                #original_path = './delteme.png'
                #actmap_path = './delteme.png'

                actmap_path=actmap_path.replace(actmap_dir, 'http://52.79.122.106:8000/media/actmap')
                original_path=original_path.replace(actmap_dir, 'http://52.79.122.106:8000/media/actmap')
                ret_values = {'value_ret': float(value_ret), 'value_gla': float(value_gla), 'value_cat': float(value_cat), 'LR': LR,
                     'actmap_path': actmap_path ,'patient_id':pat_id, 'patient_name':pat_name , 'exam_date' :exam_date, 'exam_time':exam_time  ,
                              'is_dicom':dicom_checker(f_path) , 'origin_path':original_path , 'fname':str(fname)}
                ret_json.append(ret_values)
            ret_json=json.dumps(ret_json)


            return JsonResponse(ret_json , safe = False)
    else:
        form = UploadForm()
    return render(request,  'upload.html', {'form' : form})


