#-*- coding:utf-8 -*-
import os
import numpy as np
import tensorflow as tf
import cam

#-*- coding:utf-8 -*-
import os
import numpy as np
import tensorflow as tf
import cam
import time


def load_model(model_path):
    sess = tf.Session()
    saver = tf.train.import_meta_graph(meta_graph_or_file=model_path+'.meta') #example model path ./models/fundus_300/5/model_1.ckpt
    saver.restore(sess, save_path=model_path) # example model path ./models/fundus_300/5/model_1.ckpt
    x_ = tf.get_default_graph().get_tensor_by_name('x_:0')
    y_ = tf.get_default_graph().get_tensor_by_name('y_:0')
    pred_ = tf.get_default_graph().get_tensor_by_name('softmax:0')
    is_training_=tf.get_default_graph().get_tensor_by_name('is_training:0')
    top_conv = tf.get_default_graph().get_tensor_by_name('top_conv:0')
    logits = tf.get_default_graph().get_tensor_by_name('logits:0')
    cam_ = tf.get_default_graph().get_tensor_by_name('classmap:0')
    cam_ind = tf.get_default_graph().get_tensor_by_name('cam_ind:0')
    return sess ,pred_ , x_ , is_training_

def eval(test_img , sess , pred_op , x_  , is_training_):
    pred = sess.run(pred_op , feed_dict={x_ : test_img , is_training_:False})
    return pred


"""
def eval(model_path ,test_images , batch_size  , actmap_folder , ):
    print '########## EVAL ##########'
    # Normalize
    if np.max(test_images) > 1:
        test_images = test_images / 255.
    # Reconstruct Model
    start_time = time.time()
    sess = tf.Session()
    saver = tf.train.import_meta_graph(meta_graph_or_file=model_path+'.meta') #example model path ./models/fundus_300/5/model_1.ckpt
    saver.restore(sess, save_path=model_path) # example model path ./models/fundus_300/5/model_1.ckpt
    x_ = tf.get_default_graph().get_tensor_by_name('x_:0')
    y_ = tf.get_default_graph().get_tensor_by_name('y_:0')
    pred_ = tf.get_default_graph().get_tensor_by_name('softmax:0')
    is_training_=tf.get_default_graph().get_tensor_by_name('is_training:0')
    top_conv = tf.get_default_graph().get_tensor_by_name('top_conv:0')
    logits = tf.get_default_graph().get_tensor_by_name('logits:0')
    cam_ = tf.get_default_graph().get_tensor_by_name('classmap:0')
    cam_ind = tf.get_default_graph().get_tensor_by_name('cam_ind:0')

    print 'Session load time : {} '.format(start_time - time.time())

    # Get Predictions from model.
    start_time = time.time()
    if not actmap_folder is None:
        if not os.path.isdir(actmap_folder):
            os.makedirs(actmap_folder)
        cam.eval_inspect_cam(sess, cam_, cam_ind, top_conv, test_images[:], x_, y_, is_training_, logits, actmap_folder)
    share=len(test_images)/batch_size
    remainder=len(test_images)%batch_size
    predList=[]
    for s in range(share):
        pred = sess.run(pred_ , feed_dict={x_ : test_images[s*batch_size:(s+1)*batch_size],is_training_:False})
        predList.extend(pred)
    if not remainder == 0:
        pred = sess.run(pred_, feed_dict={x_: test_images[-1*remainder:], is_training_: False})
        predList.extend(pred)
    assert len(predList) == len(test_images), '# pred : {} # imgaes : {} should be SAME!'.format(len(predList),
                                                                                                 len(test_images))
    print 'Eval time : {} '.format(start_time - time.time())
    # Reset Graph
    tf.reset_default_graph()
    return np.asarray(predList)
"""
