# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import web_classifier.settings as settings

from forms import *
from PIL import Image
import numpy as np
import os
import eval
import cv2
# Create your views here.

print 'Load Session'

model_path_ret= '../web_classifier/models/step_23300_acc_0.892063558102/model'
model_path_gla= '../web_classifier/models/step_34200_acc_0.882777810097/model'
model_path_cat= '../web_classifier/models/step_6300_acc_0.966666698456/model'
sess_ret ,pred_op_ret , x_ret, is_training_ret = eval.load_model(model_path_ret)
sess_gla ,pred_op_gla , x_gla , is_training_gla = eval.load_model(model_path_gla)
sess_cat ,pred_op_cat , x_cat , is_training_cat = eval.load_model(model_path_cat)

def clahe_equalized(img):
    if len(img.shape) == 2:
        img=np.reshape(img, list(np.shape(img)) +[1])
    assert (len(img.shape)==3)  #4D arrays
    img=img.copy()
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    if img.shape[-1] ==3: # if color shape
        for i in range(3):
            img[:, :, i]=clahe.apply(np.array(img[:,:,i], dtype=np.uint8))
    elif img.shape[-1] ==1: # if Greys,
        img = clahe.apply(np.array(img, dtype = np.uint8))
    return img


def upload_file(request):
    if request.method == 'POST':
        form = UploadForm(request.POST , request.FILES)
        if form.is_valid():
            form.save()
            fname=str(request.FILES['file'])
            # load Image
            f_path=os.path.join(settings.MEDIA_ROOT , fname)
            img = np.asarray(Image.open(f_path).resize([300, 300], Image.ANTIALIAS).convert('RGB'))
            img=clahe_equalized(img)
            img=img/255.
            h,w,ch=np.shape(img)
            img=img.reshape([1,h,w,ch])

            #img = img.reshape([1,] + list(np.shape(img)))
            #model_path = './models/step_38300_acc_0.890909016132/model'
            # Eval Image
            pred_list_ret = eval.eval(img, sess_ret, pred_op_ret, x_ret, is_training_ret)
            pred_list_gla = eval.eval(img, sess_gla, pred_op_gla, x_gla, is_training_gla)
            pred_list_cat = eval.eval(img, sess_cat, pred_op_cat, x_cat, is_training_cat)

            if pred_list_ret[0][0] > 0.5 :
                value_ret = 'NORMAL'
            else:
                value_ret = 'ABNORMAL'


            if pred_list_cat[0][0] > 0.5 :
                value_cat = 'NORMAL'
            else:
                value_cat = 'ABNORMAL'

            if pred_list_gla[0][0] > 0.5 :
                value_gla = 'NORMAL'
            else:
                value_gla = 'ABNORMAL'
            print 'glaucoma ' , pred_list_gla
            print 'retina' , pred_list_ret
            print 'cataract' , pred_list_cat

            print 'form is save'
            return render(request, 'show_acc.html',{'value_ret': value_ret, 'value_gla': value_gla, 'value_cat': value_cat})
    else:
        form = UploadForm()
    return render(request,  'upload.html', {'form' : form})