#-*- coding:utf-8 -*-
import os
import numpy as np
import tensorflow as tf
import cam
from PIL import Image
import cv2
import os
import numpy as np
import tensorflow as tf
import cam
import time
import sys
import matplotlib.pyplot as plt
from utils import crop_margin_fundus


def get_class_map(name, x, cam_ind, im_width, w=None):
    out_ch = int(x.get_shape()[-1])
    conv_resize = tf.image.resize_bilinear(x, [im_width, im_width])
    if w is None:
        with tf.variable_scope(name, reuse=True) as scope:
            label_w = tf.gather(tf.transpose(tf.get_variable('w')), cam_ind)
            label_w = tf.reshape(label_w, [-1, out_ch, 1])
    else:
        label_w = tf.gather(tf.transpose(w), cam_ind)
        label_w = tf.reshape(label_w, [-1, out_ch, 1])

    conv_resize = tf.reshape(conv_resize, [-1, im_width * im_width, out_ch])
    classmap = tf.matmul(conv_resize, label_w, name='classmap')
    classmap = tf.reshape(classmap, [-1, im_width, im_width], name='classmap_reshape')
    return classmap


def load_model(model_path):
    graph=tf.Graph()
    session_conf = tf.ConfigProto(
        intra_op_parallelism_threads=1,
        inter_op_parallelism_threads=1)
    #
    sess = tf.Session(graph = graph)
    with graph.as_default():
        saver = tf.train.import_meta_graph(meta_graph_or_file=model_path+'.meta' , clear_devices=True) #example model path ./models/fundus_300/5/model_1.ckpt
        saver.restore(sess, save_path=model_path) # example model path ./models/fundus_300/5/model_1.ckpt
        x_ = tf.get_default_graph().get_tensor_by_name('x_:0')
        y_ = tf.get_default_graph().get_tensor_by_name('y_:0')
        pred_ = tf.get_default_graph().get_tensor_by_name('softmax:0')
        is_training_=tf.get_default_graph().get_tensor_by_name('is_training:0')
        top_conv = tf.get_default_graph().get_tensor_by_name('top_conv:0')
        logits = tf.get_default_graph().get_tensor_by_name('logits:0')
        try:
            cam_ = tf.get_default_graph().get_tensor_by_name('classmap:0')
            cam_ind = tf.get_default_graph().get_tensor_by_name('cam_ind:0')
        except:
            final_w = tf.get_default_graph().get_tensor_by_name('final/w:0')
            try:
                cam_ind = tf.get_default_graph().get_tensor_by_name('cam_ind:0')
            except Exception as e:
                print "CAM 이 구현되어 있지 않은 모델입니다."

            cam_imgSize=int(x_.get_shape()[1])
            cam_= get_class_map('final', top_conv, 1, cam_imgSize, final_w)
        #gap_w= tf.get_default_graph().get_tensor_by_name('gap/w:0')

        return sess ,pred_ , x_ , y_ , is_training_ , top_conv ,cam_ , cam_ind , logits

def eval(test_img , sess , pred_op , x_  , is_training_):
    pred = sess.run(pred_op , feed_dict={x_ : test_img , is_training_:False})
    return pred


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

def get_pred(img, sess_ret_info, sess_gla_info, sess_cat_info):

    sess_ret, pred_op_ret, x_ret, y_ret, is_training_ret, top_conv_ret, cam_ret, cam_ind_ret ,logits_ret = sess_ret_info
    sess_gla, pred_op_gla, x_gla, y_gla, is_training_gla, top_conv_gla, cam_gla, cam_ind_gla, logits_gla = sess_gla_info
    sess_cat, pred_op_cat, x_cat, y_cat, is_training_cat ,top_conv_cat ,cam_cat, cam_ind_cat, logits_cat = sess_cat_info
    #img = crop_margin_fundus(img)
    # Multiple Images
    #img = np.asarray(img.resize([300, 300], Image.ANTIALIAS).convert('RGB'))
    #img = clahe_equalized(img)
    h, w, ch = np.shape(img)
    img = img.reshape([1, h, w, ch])
    img = img / 255.

    # img = img.reshape([1,] + list(np.shape(img)))
    # model_path = './models/step_38300_acc_0.890909016132/model'
    # Eval Image
    pred_list_ret = eval(img, sess_ret, pred_op_ret, x_ret, is_training_ret)
    pred_list_gla = eval(img, sess_gla, pred_op_gla, x_gla, is_training_gla)
    pred_list_cat = eval(img, sess_cat, pred_op_cat, x_cat, is_training_cat)

    print 'glaucoma ', pred_list_gla
    print 'retina', pred_list_ret
    print 'cataract', pred_list_cat

    return pred_list_ret[0][1], pred_list_gla[0][1], pred_list_cat[0][1]


def diagnose_image(prediction):
    ret_list= []
    if prediction[0] > 0.5: # e.g) prediction [normal_possibility , abnormal_possibility ]
        value = 'NORMAL'
    else:
        value = 'ABNORMAL'
    return value


def diagnose_images(predictions):
    ret_list = []
    for pred in predictions:
        ret_list.append(diagnose_image(pred))
    return ret_list

def overlay(actmap , ori_img ,save_path , factor):
    assert factor <= 1 and factor >= 0
    cmap = plt.cm.jet
    tmp_path='/Users/seongjungkim/PycharmProjects/web_classifier/media/tmp.png'
    tmp_path='/home/ubuntu/web_classifier/media/tmp.png'
    plt.imsave(fname=tmp_path, arr=cmap(actmap))
    cam_img=Image.open(tmp_path)
    #np_cam_img=np.asarray(cam_img).astype('uint8') #img 2 numpy
    ori_img=Image.fromarray(ori_img.astype('uint8')).convert("RGBA")
    overlay_img = Image.blend(ori_img, cam_img, factor).convert('RGB')
    #return np.asarray(overlay_img)
    overlay_img.save(save_path)

    #plt.imsave(save_path, overlay_img)
    save_dir,name=os.path.split(save_path)
    name=os.path.splitext(name)[0]+'_ori.png'
    #plt.imsave(os.path.join(save_dir ,name), ori_img)
    ori_img.save(os.path.join(save_dir ,name))
    plt.close();
    os.remove(tmp_path)

    return np.asarray(overlay_img)

def eval_inspect_cam(sess, cam ,cam_ind, top_conv ,test_imgs , x, y_ ,phase_train, y , save_root_folder):

    """
    for img in test_imgs:
        img=Image.fromarray(img)
        crop_margin_fundus(img)
    """
    if test_imgs.max() > 1 :
        test_imgs=test_imgs/255.



    num_images=len(test_imgs[:])
    ABNORMAL_LABEL =np.asarray([[0,1]])
    NORMAL_LABEL = np.asarray([[1,0]])
    ABNORMAL_CLS=np.argmax(ABNORMAL_LABEL , axis=1)
    NORMAL_CLS = np.argmax(ABNORMAL_LABEL , axis=1)
    try:
        os.mkdir('./out');
    except Exception as e :
        print e
        pass;
    if not os.path.isdir(save_root_folder):
        os.mkdir(save_root_folder)

    folder_n = 0
    while(True):
        save_dir = '{}/{}'.format(save_root_folder, folder_n)
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
            break
        else:
            folder_n +=1


    for s in range(num_images):
        msg='\r {}/{}'.format(s , num_images)
        sys.stdout.write(msg)
        sys.stdout.flush()
        save_dir='{}/{}/img_{}'.format(save_root_folder,folder_n,s)
        # Make Folder
        try:
            os.mkdir(save_dir);
        except Exception as e :
            print e;

        # Check Image Channel
        if test_imgs[s].shape[-1]==1:
            plt.imsave('{}/original_image.png'.format(save_dir) ,test_imgs[s].reshape([test_imgs[s].shape[0] \
                                                                                      , test_imgs.shape[1]]))
        else :
            img=Image.fromarray((test_imgs[s]*255).astype('uint8'))
            print np.max(img)

            #plt.imsave('{}/image_test.png'.format(save_dir), test_imgs[s])
            img.save('{}/original_image.png'.format(save_dir))

        # Image Reshape
        if test_imgs[s].max() <= 1 :
            img=(test_imgs[s] * 255).astype('uint8')
        else:
            img=test_imgs[s]
        img_h, img_w, img_ch = np.shape(img)
        img = np.asarray(Image.fromarray(img).resize((300,300) , Image.ANTIALIAS))
        img = np.reshape(img, (1, 300, 300, 3))
        #img=test_imgs[s].reshape(1 ,test_imgs[s].shape[0] ,test_imgs[s].shape[1] ,-1 )
        conv_val , output_val =sess.run([top_conv , y] , feed_dict={x:img , phase_train:False})
        cam_ans_abnormal = sess.run(cam, feed_dict={y_: ABNORMAL_LABEL, cam_ind: ABNORMAL_CLS[0], top_conv: conv_val,
                                                    phase_train: False})
        cam_ans_normal = sess.run(cam, feed_dict={y_: NORMAL_LABEL, cam_ind: NORMAL_CLS[0], top_conv: conv_val,
                                                  phase_train: False})

        # Actmap Resize From (300 , 300 ) to Original Image Size
        cam_ans_abnormal, = map(lambda x: np.squeeze(x), [cam_ans_abnormal]) # (1,90000,1)

        cam_ans_abnormal = cam_ans_abnormal.reshape([img.shape[1], img.shape[2]]) # (300,300)
        #bilinear resize image
        cam_ans_abnormal = Image.fromarray(cam_ans_abnormal).resize((test_imgs[s].shape[1], test_imgs[s].shape[0]),
                                                                    Image.ANTIALIAS)
        cam_ans_abnormal = np.asarray(cam_ans_abnormal)

        # Normalize Actmap
        cam_vis_abnormal =(cam_ans_abnormal - np.min(cam_ans_abnormal))/(np.max(cam_ans_abnormal) - np.min(cam_ans_abnormal))
        #cam_vis_abnormal=map(lambda x: (x-x.min())/(x.max()-x.min()) , cam_ans_abnormal)
        #plt.imsave('/Users/seongjungkim/PycharmProjects/web_classifier/media/actmap/img_0/tmp.png' , cam_vis_abnormal  )

        # Blend Images
        blend_img=overlay(cam_vis_abnormal, test_imgs[s]*255, '{}/blend_actmap.png'.format(save_dir) , 0.2)
        cmap = plt.cm.jet

        #plt.imshow(cam_vis_abnormal, cmap=plt.cm.jet, alpha=0.5, interpolation='nearest', vmin=0, vmax=1)
        cam_vis_abnormal=cmap(cam_vis_abnormal)

        # Blend Images
        print np.shape(cam_vis_abnormal)
        print np.max(cam_vis_abnormal)
        #Image.fromarray(cam_vis_abnormal.astype('uint8')).save('{}/abnormal_actmap.png'.format(save_dir))
        #plt.imsave('{}/abnormal_actmap.png'.format(save_dir), cam_vis_abnormal)
        #plt.imsave('{}/normal_actmap.png'.format(save_dir), cam_vis_normal)
        #plt.imsave('{}/blend_img.png'.format(save_dir), Image.fromarray(blend_img))
        return '{}/blend_actmap.png'.format(save_dir) ,'{}/original_image.png'.format(save_dir)
def detect_brigthArtifact(np_img):

    img = np_img
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    mark = (gray > 220).astype(np.uint8)

    # inside　기준을　ratio = 0.8로　잡음

    part = np.ones(gray.shape, dtype=np.uint8)
    center_pos = np.array(gray.shape[:2]) // 2
    radius = int(center_pos.min() * 0.8)
    cv2.circle(part, tuple(center_pos), radius, 0, -1)

    blank = np.zeros_like(img)
    mark = cv2.bitwise_and(mark, mark, mask=part)
    # artifact가　총　면적의　２％　이상이면　검출되었다고　판단
    #artfect 검출
    artifact_ratio = mark.sum() / (mark.shape[0] * mark.shape[1])


    return artifact_ratio


"""
# Bright Spot imag except outside
# 외곽의　기준을　ratio = 0.99로　잡음　（ 대부분　이미지가　외각의　경우　좀　더　밝게　찍힘　그래서　그건　무시）
part = np.zeros(gray.shape, dtype=np.uint8)
center_pos = np.array(gray.shape[:2]) // 2
radius = int(center_pos.min() * 0.99)
cv2.circle(part, tuple(center_pos), radius, 1, -1)

mark = cv2.bitwise_and(mark, mark, mask=part)
"""

def detect_darkArtifact(np_img):
    img = np_img
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.GaussianBlur(img, (11, 11), 0)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    mark = (gray < 40).astype(np.uint8)

    # 외곽의　기준을　ratio = 0.99로　잡음　（ 대부분　이미지가　외각의　경우　좀　더　밝게　찍힘　그래서　그건　무시）
    part = np.zeros(gray.shape, dtype=np.uint8)
    center_pos = np.array(gray.shape[:2]) // 2
    radius = int(center_pos.min() * 0.99)
    cv2.circle(part, tuple(center_pos), radius, 1, -1)

    mark = cv2.bitwise_and(mark, mark, mask=part)

    # artifact가　총　면적의　２％　이상이면　검출되었다고　판단
    dark_ratio = mark.sum() / (mark.shape[0] * mark.shape[1])

    return dark_ratio


# Session Start , load graph
tf.reset_default_graph()
model_path_ret= '/home/ubuntu/web_classifier/models/step_23300_acc_0.892063558102/model'
model_path_gla= '/home/ubuntu/web_classifier/models/step_34200_acc_0.882777810097/model'
model_path_cat= '/home/ubuntu/web_classifier/models/step_6300_acc_0.966666698456/model'
model_path_cat_advance= '/home/ubuntu/web_classifier/models/cata_advance/model-15840'


sess_ret_ops= load_model(model_path_ret)
sess_gla_ops= load_model(model_path_gla)
sess_cat_ops= load_model(model_path_cat_advance)

