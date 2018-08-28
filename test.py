#-*- coding:utf-8 -*-
import tensorflow as tf

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


if __name__ == '__main__':
    model_path_ret = './models/step_23300_acc_0.892063558102/model'
    model_path_gla = './models/step_34200_acc_0.882777810097/model'
    model_path_cat = './models/step_6300_acc_0.966666698456/model'

    load_model(model_path_cat)
    load_model(model_path_gla)
    load_model(model_path_ret)
