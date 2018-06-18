import dicom
from PIL import Image
import numpy as np
import time
def check_LR():
    pass;


def dicom_checker(path):
    assert type(path) == str , 'path type is must be str '
    return path.endswith('.dcm')

def check_image(path):
    try:
        Image.open(path)
        return True
    except:
        return False

def get_patinfo(path): #
    assert dicom_checker(path)
    dc=dicom.read_file(path)
    exam_date = dc.StudyDate # yyyymmdd
    exam_time = dc.StudyTime # hhmmss
    pat_id = dc.PatientID
    np_img = dc.pixel_array.astype('uint8')
    ch, h, w =np.shape(np_img)
    np_img=np.reshape(np_img ,[h, w ,ch] )
    img = Image.fromarray(np_img)
    return pat_id , exam_date , exam_time , img


def crop_margin_fundus(im):
    debug_flag=False
    """
    file name =1002959_20130627_L.png
    """
    np_img = np.asarray(im)
    mean_pix = np.mean(np_img)
    pix = im.load()
    height, width = im.size  # Get the width and hight of the image for iterating over
    # pix[1000,1000] #Get the RGBA Value of the a pixel of an image
    c_x, c_y = (int(height / 2), int(width / 2))

    for y in range(c_y):
        if sum(pix[c_x, y]) > mean_pix:
            left = (c_x, y)
            break;

    for x in range(c_x):
        if sum(pix[x, c_y]) > mean_pix:
            up = (x, c_y)
            break;
    diameter_height = up[1] - left[1]
    diameter_width = left[0] - up[0]

    crop_img = im.crop((up[0], left[1], left[0] + diameter_width, up[1] + diameter_height))
    return crop_img

def fundus_laterality(img):
    img = np.asarray(img)
    h, w, ch = np.shape(img)
    a_img = img[:, :int(w * 0.5), :]
    b_img = img[:, int(w * 0.5):, :]
    if a_img.mean() > b_img.mean():
        return 0 # Left
    else:
        return 1 # Right



