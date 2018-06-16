# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import web_classifier.settings as settings

from forms import *
from PIL import Image
import numpy as np
import os
import eval

# Create your views here.

print 'Load Session'

model_path_ret= '../web_classifier/models/step_38300_acc_0.890909016132/model'
model_path_gla= '../web_classifier/models/step_34200_acc_0.882777810097/model'
model_path_cat= '../web_classifier/models/step_6300_acc_0.966666698456/model'
sess_ret ,pred_op_ret , x_ret, is_training_ret = eval.load_model(model_path_ret)
sess_cat ,pred_op_cat , x_cat , is_training_cat = eval.load_model(model_path_cat)
sess_gla ,pred_op_gla , x_gla , is_training_gla = eval.load_model(model_path_gla)




def upload_file(request):
    if request.method == 'POST':
        form = UploadForm(request.POST , request.FILES)
        if form.is_valid():
            form.save()
            fname=str(request.FILES['file'])
            # load Image
            f_path=os.path.join(settings.MEDIA_ROOT , fname)
            img = np.asarray(Image.open(f_path).resize([300, 300], Image.ANTIALIAS).convert('RGB'))
            h,w,ch=np.shape(img)
            img=img.reshape([1,h,w,ch])

            #img = img.reshape([1,] + list(np.shape(img)))
            #model_path = './models/step_38300_acc_0.890909016132/model'
            # Eval Image
            pred_list_ret=eval.eval(img,sess_ret,pred_op_ret , x_ret  , is_training_ret)
            pred_list_cat = eval.eval(img, sess_cat, pred_op_cat, x_cat, is_training_cat)
            pred_list_gla = eval.eval(img, sess_gla, pred_op_gla, x_gla, is_training_gla)

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
            print 'form is save'
            return render(request , 'show_acc.html' , {'value_ret':value_ret , 'value_cat':value_cat , 'value_gla':value_gla })
    else:
        form = UploadForm()
    return render(request,  'upload.html', {'form' : form})