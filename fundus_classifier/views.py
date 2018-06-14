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
model_path = './models/step_38300_acc_0.890909016132/model'
sess ,pred_op , x_ , is_training_ = eval.load_model(model_path)



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
            pred_list=eval.eval(img,sess,pred_op , x_ , is_training_)
            if pred_list[0][0] > 0.5 :
                value = 'NORMAL'
            else:
                value = 'ABNORMAL'

            print 'form is save'
            return render(request , 'show_acc.html' , {'value':value})
    else:
        form = UploadForm()
    return render(request,  'upload.html', {'form' : form})