from PIL import Image
import numpy as np
import os
from eval import  load_model  , get_pred , eval_inspect_cam
from utils import get_patinfo , dicom_checker , fundus_laterality
model_path_ret= '../models/step_23300_acc_0.892063558102/model'
sess_ret_ops= load_model(model_path_ret)
sess_ret, pred_op_ret, x_ret, y_ret, is_training_ret, top_conv_ret, cam_ret, cam_ind_ret, logits_ret = sess_ret_ops
f_path = './5217696_20141224_L.png'
if dicom_checker(f_path):
    pat_id, exam_date, exam_time, img = get_patinfo(f_path)
else:  # PNG , JPEG , JPG ...etc
    img = Image.open(f_path)
# LR_checker
LR = fundus_laterality(img)  # 0 : LEFT , 1 L RIGHT
print LR

np.shape(img)
np_img=np.asarray(img).reshape([1]+list(np.shape(img)))
actmap_path = eval_inspect_cam(sess_ret, cam_ret, cam_ind_ret, top_conv_ret, np_img, x_ret, y_ret, is_training_ret,
                             logits_ret, '../media/actmap')

