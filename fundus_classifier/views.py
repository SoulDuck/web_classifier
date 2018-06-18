# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
import web_classifier.settings as settings
from forms import *
from PIL import Image
import numpy as np
import os
import json
from eval import  load_model  , get_pred , eval_inspect_cam , clahe_equalized
from utils import get_patinfo , dicom_checker , fundus_laterality , crop_margin_fundus

# Create your views here.
#/Users/seongjungkim/PycharmProjects/web_classifier/models
#/home/ubuntu/web_classifier
model_path_ret= '/home/ubuntu/web_classifier/web_classifier/models/step_23300_acc_0.892063558102/model'
model_path_gla= '/home/ubuntu/web_classifier/web_classifier/models/step_34200_acc_0.882777810097/model'
model_path_cat= '/home/ubuntu/web_classifier/web_classifier/models/step_6300_acc_0.966666698456/model'
sess_ret_ops= load_model(model_path_ret)
sess_gla_ops= load_model(model_path_gla)
sess_cat_ops= load_model(model_path_cat)

#sess ,pred_ , x_ , is_training_ , top_conv

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = UploadForm(request.POST , request.FILES)
        sess_ret, pred_op_ret, x_ret, y_ret, is_training_ret, top_conv_ret, cam_ret, cam_ind_ret, logits_ret = sess_ret_ops
        if form.is_valid():
            form.save()
            fname=str(request.FILES['file'])
            # load Image
            f_path=os.path.join(settings.MEDIA_ROOT , fname)
            pat_id, exam_date, exam_time = 'None' , 'None' , 'None'
            # dicom check
            if dicom_checker(f_path):
                pat_id, exam_date, exam_time , img = get_patinfo(f_path)
            else: # PNG , JPEG , JPG ...etc
                img = Image.open(f_path)
            # LR_checker
            LR = fundus_laterality(img) # 0 : LEFT , 1 L RIGHT
            print LR

            img = crop_margin_fundus(img)
            # Multiple Images
            img = np.asarray(img.resize([300, 300], Image.ANTIALIAS).convert('RGB'))
            img = clahe_equalized(img)

            value_ret, value_gla , value_cat = get_pred(img , sess_ret_ops , sess_gla_ops ,sess_cat_ops)

            actmap_dir = '/Users/seongjungkim/PycharmProjects/web_classifier/media/actmap'
            actmap_dir = '/home/ubuntu/web_classifier/media/actmap'
            np_img=np.asarray(img).reshape([1]+list(np.shape(img)))
            actmap_path=eval_inspect_cam(sess_ret, cam_ret, cam_ind_ret, top_conv_ret, np_img, x_ret, y_ret, is_training_ret,
                             logits_ret, actmap_dir)
            print actmap_path
            print 'form is save'
            #return render(request, 'show_acc.html',{'value_ret': value_ret, 'value_gla': value_gla, 'value_cat': value_cat})
            #return HttpResponseRedirect({'value_ret': value_ret, 'value_gla': value_gla, 'value_cat': value_cat})


            ret_values = {'value_ret': str(value_ret), 'value_gla': str(value_gla), 'value_cat': str(value_cat), 'LR': LR,
                 'actmap_path': actmap_path ,'patient_id':pat_id, 'exam_date' :exam_date, 'exam_time':exam_time  , 'is_dicom':str(dicom_checker(f_path))}
            return JsonResponse(ret_values)
    else:
        form = UploadForm()
    return render(request,  'upload.html', {'form' : form})


