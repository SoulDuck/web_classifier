# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import web_classifier.settings as settings
from forms import *
from PIL import Image
import numpy as np
import os
from eval import  load_model  , get_pred , eval_inspect_cam
from utils import get_patinfo , dicom_checker , fundus_laterality

# Create your views here.

print 'Load Session'
model_path_ret= '../web_classifier/models/step_23300_acc_0.892063558102/model'
model_path_gla= '../web_classifier/models/step_34200_acc_0.882777810097/model'
model_path_cat= '../web_classifier/models/step_6300_acc_0.966666698456/model'
sess_ret_ops= load_model(model_path_ret)
sess_gla_ops= load_model(model_path_gla)
sess_cat_ops= load_model(model_path_cat)

#sess ,pred_ , x_ , is_training_ , top_conv


def upload_file(request):
    if request.method == 'POST':
        form = UploadForm(request.POST , request.FILES)
        sess_ret, pred_op_ret, x_ret, y_ret, is_training_ret, top_conv_ret, cam_ret, cam_ind_ret, logits_ret = sess_ret_ops
        if form.is_valid():
            form.save()
            fname=str(request.FILES['file'])
            # load Image
            f_path=os.path.join(settings.MEDIA_ROOT , fname)

            # dicom check
            if dicom_checker(f_path):
                pat_id, exam_date, exam_time , img = get_patinfo(f_path)
            else: # PNG , JPEG , JPG ...etc
                img = Image.open(f_path)
            # LR_checker
            LR = fundus_laterality(img) # 0 : LEFT , 1 L RIGHT
            print LR

            # Cut out useless part of fundus image
            #cropped_img=crop_margin_fundus(img)
            # Get Probability
            value_ret, value_gla , value_cat = get_pred(img , sess_ret_ops , sess_gla_ops ,sess_cat_ops)
            # Get Actmap
            ret_x = sess_ret_ops[2]

            # CLAHE
            #img = np.asarray(img)
            #img_h, img_w, img_ch = np.shape(img)
            #img = clahe_equalized(img)
            # Normalizae
            #np_img = img.reshape([1, img_h, img_w, img_ch]) / 255.

            np_img=np.asarray(img).reshape([1]+list(np.shape(img)))
            actmap_path=eval_inspect_cam(sess_ret, cam_ret, cam_ind_ret, top_conv_ret, np_img, x_ret, y_ret, is_training_ret,
                             logits_ret, '/Users/seongjungkim/PycharmProjects/web_classifier/media/actmap')
            print actmap_path
            print 'form is save'
            #return render(request, 'show_acc.html',{'value_ret': value_ret, 'value_gla': value_gla, 'value_cat': value_cat})
            return {'value_ret': value_ret, 'value_gla': value_gla, 'value_cat': value_cat}
    else:
        form = UploadForm()
    return render(request,  'upload.html', {'form' : form})


