import cv2
import dlib
import numpy as np
import os
import pickle
import warnings
from .color_palette import create_diag_features
from tensorflow.keras.models import load_model

warnings.filterwarnings('ignore')

def count_faces(img_path='results/photo_0.jpg'):
    detector = dlib.get_frontal_face_detector()
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    return len(rects)

def get_pc_result(diag_file='results/photo_0.jpg', n_colors=4):

    wc_model = load_model('personal_color/models/warm_cool.h5', compile=False)
    
    cool_model = pickle.load(open('personal_color/models/cool.pkl', 'rb'))
    warm_model = pickle.load(open('personal_color/models/warm.pkl', 'rb'))

    features, face = create_diag_features(diag_file, n_colors)
    wc_result = wc_model.predict(features)[0][0]
      
    if wc_result < .5:
        result = warm_model.predict(features)[0]
        if result == 0:
            result = 'spr'
        else:
            result = 'fal'
    else:
        result = cool_model.predict(features)[0]
        if result == 0:
            result = 'sum'
        else:
            result = 'win'
    
    print('Diag result:', wc_result, result)


    return result, face

# get_pc_result()
