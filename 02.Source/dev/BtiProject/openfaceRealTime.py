# -----------------------
import tensorflow as tf
from keras.models import Model, Sequential
from keras.layers import Input, Conv2D, ZeroPadding2D, MaxPooling2D, Flatten, Dense, Dropout, Activation, concatenate
from keras.layers.pooling import MaxPooling2D, AveragePooling2D
from keras.layers.core import Dense, Activation, Lambda, Flatten
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.image import load_img, save_img, img_to_array
from keras.applications.imagenet_utils import preprocess_input
from keras.preprocessing import image
from keras.models import model_from_json
from keras.layers.merge import Concatenate
from keras import backend as K

import os, platform, re, site
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt

# -----------------------

class openfaceRealTime():

    def __init__(self):
        if platform.system() == "Linux":
            self.osName = "Linux"
            self.employee_pictures = "/home/bit/Downloads/blackpink_crop"
            # self.employee_pictures = "/home/bit/Downloads/crop_twice"
            self.videoFilePath = "/home/bit/Downloads/test5.mp4"

        elif platform.system() == "Windows":
            self.osName = "Windows"
            self.employee_pictures = "C:/Users/bit/Downloads/blackpink_crop"
            # self.employee_pictures = "F:/sampleData/crop_twice"
            self.videoFilePath = "./videoLIst/test5.mp4"

        self.face_cascade = ""
        self.dump = False
        self.model = ""
        self.color = (255, 0, 0)

        self.employees = dict()
        self.metric = "euclidean"
        self.threshold = 0.45

    def preprocess_image(self, image_path):
        img = load_img(image_path, target_size=(96, 96))
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        return img
    # ------------------------

    def builtModel(self):
        myInput = Input(shape=(96, 96, 3))

        x = ZeroPadding2D(padding=(3, 3), input_shape=(96, 96, 3))(myInput)
        x = Conv2D(64, (7, 7), strides=(2, 2), name='conv1')(x)
        x = BatchNormalization(axis=3, epsilon=0.00001, name='bn1')(x)
        x = Activation('relu')(x)
        x = ZeroPadding2D(padding=(1, 1))(x)
        x = MaxPooling2D(pool_size=3, strides=2)(x)
        x = Lambda(lambda x: tf.nn.lrn(x, alpha=1e-4, beta=0.75), name='lrn_1')(x)
        x = Conv2D(64, (1, 1), name='conv2')(x)
        x = BatchNormalization(axis=3, epsilon=0.00001, name='bn2')(x)
        x = Activation('relu')(x)
        x = ZeroPadding2D(padding=(1, 1))(x)
        x = Conv2D(192, (3, 3), name='conv3')(x)
        x = BatchNormalization(axis=3, epsilon=0.00001, name='bn3')(x)
        x = Activation('relu')(x)
        Lambda(lambda x: tf.nn.lrn(x, alpha=1e-4, beta=0.75), name='lrn_2')(x)
        x = ZeroPadding2D(padding=(1, 1))(x)
        x = MaxPooling2D(pool_size=3, strides=2)(x)

        # Inception3a
        inception_3a_3x3 = Conv2D(96, (1, 1), name='inception_3a_3x3_conv1')(x)
        inception_3a_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_3x3_bn1')(inception_3a_3x3)
        inception_3a_3x3 = Activation('relu')(inception_3a_3x3)
        inception_3a_3x3 = ZeroPadding2D(padding=(1, 1))(inception_3a_3x3)
        inception_3a_3x3 = Conv2D(128, (3, 3), name='inception_3a_3x3_conv2')(inception_3a_3x3)
        inception_3a_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_3x3_bn2')(inception_3a_3x3)
        inception_3a_3x3 = Activation('relu')(inception_3a_3x3)

        inception_3a_5x5 = Conv2D(16, (1, 1), name='inception_3a_5x5_conv1')(x)
        inception_3a_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_5x5_bn1')(inception_3a_5x5)
        inception_3a_5x5 = Activation('relu')(inception_3a_5x5)
        inception_3a_5x5 = ZeroPadding2D(padding=(2, 2))(inception_3a_5x5)
        inception_3a_5x5 = Conv2D(32, (5, 5), name='inception_3a_5x5_conv2')(inception_3a_5x5)
        inception_3a_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_5x5_bn2')(inception_3a_5x5)
        inception_3a_5x5 = Activation('relu')(inception_3a_5x5)

        inception_3a_pool = MaxPooling2D(pool_size=3, strides=2)(x)
        inception_3a_pool = Conv2D(32, (1, 1), name='inception_3a_pool_conv')(inception_3a_pool)
        inception_3a_pool = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_pool_bn')(inception_3a_pool)
        inception_3a_pool = Activation('relu')(inception_3a_pool)
        inception_3a_pool = ZeroPadding2D(padding=((3, 4), (3, 4)))(inception_3a_pool)

        inception_3a_1x1 = Conv2D(64, (1, 1), name='inception_3a_1x1_conv')(x)
        inception_3a_1x1 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_1x1_bn')(inception_3a_1x1)
        inception_3a_1x1 = Activation('relu')(inception_3a_1x1)

        inception_3a = concatenate([inception_3a_3x3, inception_3a_5x5, inception_3a_pool, inception_3a_1x1], axis=3)

        # Inception3b
        inception_3b_3x3 = Conv2D(96, (1, 1), name='inception_3b_3x3_conv1')(inception_3a)
        inception_3b_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_3x3_bn1')(inception_3b_3x3)
        inception_3b_3x3 = Activation('relu')(inception_3b_3x3)
        inception_3b_3x3 = ZeroPadding2D(padding=(1, 1))(inception_3b_3x3)
        inception_3b_3x3 = Conv2D(128, (3, 3), name='inception_3b_3x3_conv2')(inception_3b_3x3)
        inception_3b_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_3x3_bn2')(inception_3b_3x3)
        inception_3b_3x3 = Activation('relu')(inception_3b_3x3)

        inception_3b_5x5 = Conv2D(32, (1, 1), name='inception_3b_5x5_conv1')(inception_3a)
        inception_3b_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_5x5_bn1')(inception_3b_5x5)
        inception_3b_5x5 = Activation('relu')(inception_3b_5x5)
        inception_3b_5x5 = ZeroPadding2D(padding=(2, 2))(inception_3b_5x5)
        inception_3b_5x5 = Conv2D(64, (5, 5), name='inception_3b_5x5_conv2')(inception_3b_5x5)
        inception_3b_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_5x5_bn2')(inception_3b_5x5)
        inception_3b_5x5 = Activation('relu')(inception_3b_5x5)

        inception_3b_pool = Lambda(lambda x: x ** 2, name='power2_3b')(inception_3a)
        inception_3b_pool = AveragePooling2D(pool_size=(3, 3), strides=(3, 3))(inception_3b_pool)
        inception_3b_pool = Lambda(lambda x: x * 9, name='mult9_3b')(inception_3b_pool)
        inception_3b_pool = Lambda(lambda x: K.sqrt(x), name='sqrt_3b')(inception_3b_pool)
        inception_3b_pool = Conv2D(64, (1, 1), name='inception_3b_pool_conv')(inception_3b_pool)
        inception_3b_pool = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_pool_bn')(inception_3b_pool)
        inception_3b_pool = Activation('relu')(inception_3b_pool)
        inception_3b_pool = ZeroPadding2D(padding=(4, 4))(inception_3b_pool)

        inception_3b_1x1 = Conv2D(64, (1, 1), name='inception_3b_1x1_conv')(inception_3a)
        inception_3b_1x1 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_1x1_bn')(inception_3b_1x1)
        inception_3b_1x1 = Activation('relu')(inception_3b_1x1)

        inception_3b = concatenate([inception_3b_3x3, inception_3b_5x5, inception_3b_pool, inception_3b_1x1], axis=3)

        # Inception3c
        inception_3c_3x3 = Conv2D(128, (1, 1), strides=(1, 1), name='inception_3c_3x3_conv1')(inception_3b)
        inception_3c_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3c_3x3_bn1')(inception_3c_3x3)
        inception_3c_3x3 = Activation('relu')(inception_3c_3x3)
        inception_3c_3x3 = ZeroPadding2D(padding=(1, 1))(inception_3c_3x3)
        inception_3c_3x3 = Conv2D(256, (3, 3), strides=(2, 2), name='inception_3c_3x3_conv' + '2')(inception_3c_3x3)
        inception_3c_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3c_3x3_bn' + '2')(inception_3c_3x3)
        inception_3c_3x3 = Activation('relu')(inception_3c_3x3)

        inception_3c_5x5 = Conv2D(32, (1, 1), strides=(1, 1), name='inception_3c_5x5_conv1')(inception_3b)
        inception_3c_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3c_5x5_bn1')(inception_3c_5x5)
        inception_3c_5x5 = Activation('relu')(inception_3c_5x5)
        inception_3c_5x5 = ZeroPadding2D(padding=(2, 2))(inception_3c_5x5)
        inception_3c_5x5 = Conv2D(64, (5, 5), strides=(2, 2), name='inception_3c_5x5_conv' + '2')(inception_3c_5x5)
        inception_3c_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3c_5x5_bn' + '2')(inception_3c_5x5)
        inception_3c_5x5 = Activation('relu')(inception_3c_5x5)

        inception_3c_pool = MaxPooling2D(pool_size=3, strides=2)(inception_3b)
        inception_3c_pool = ZeroPadding2D(padding=((0, 1), (0, 1)))(inception_3c_pool)

        inception_3c = concatenate([inception_3c_3x3, inception_3c_5x5, inception_3c_pool], axis=3)

        # inception 4a
        inception_4a_3x3 = Conv2D(96, (1, 1), strides=(1, 1), name='inception_4a_3x3_conv' + '1')(inception_3c)
        inception_4a_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_4a_3x3_bn' + '1')(inception_4a_3x3)
        inception_4a_3x3 = Activation('relu')(inception_4a_3x3)
        inception_4a_3x3 = ZeroPadding2D(padding=(1, 1))(inception_4a_3x3)
        inception_4a_3x3 = Conv2D(192, (3, 3), strides=(1, 1), name='inception_4a_3x3_conv' + '2')(inception_4a_3x3)
        inception_4a_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_4a_3x3_bn' + '2')(inception_4a_3x3)
        inception_4a_3x3 = Activation('relu')(inception_4a_3x3)

        inception_4a_5x5 = Conv2D(32, (1, 1), strides=(1, 1), name='inception_4a_5x5_conv1')(inception_3c)
        inception_4a_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_4a_5x5_bn1')(inception_4a_5x5)
        inception_4a_5x5 = Activation('relu')(inception_4a_5x5)
        inception_4a_5x5 = ZeroPadding2D(padding=(2, 2))(inception_4a_5x5)
        inception_4a_5x5 = Conv2D(64, (5, 5), strides=(1, 1), name='inception_4a_5x5_conv' + '2')(inception_4a_5x5)
        inception_4a_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_4a_5x5_bn' + '2')(inception_4a_5x5)
        inception_4a_5x5 = Activation('relu')(inception_4a_5x5)

        inception_4a_pool = Lambda(lambda x: x ** 2, name='power2_4a')(inception_3c)
        inception_4a_pool = AveragePooling2D(pool_size=(3, 3), strides=(3, 3))(inception_4a_pool)
        inception_4a_pool = Lambda(lambda x: x * 9, name='mult9_4a')(inception_4a_pool)
        inception_4a_pool = Lambda(lambda x: K.sqrt(x), name='sqrt_4a')(inception_4a_pool)

        inception_4a_pool = Conv2D(128, (1, 1), strides=(1, 1), name='inception_4a_pool_conv' + '')(inception_4a_pool)
        inception_4a_pool = BatchNormalization(axis=3, epsilon=0.00001, name='inception_4a_pool_bn' + '')(inception_4a_pool)
        inception_4a_pool = Activation('relu')(inception_4a_pool)
        inception_4a_pool = ZeroPadding2D(padding=(2, 2))(inception_4a_pool)

        inception_4a_1x1 = Conv2D(256, (1, 1), strides=(1, 1), name='inception_4a_1x1_conv' + '')(inception_3c)
        inception_4a_1x1 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_4a_1x1_bn' + '')(inception_4a_1x1)
        inception_4a_1x1 = Activation('relu')(inception_4a_1x1)

        inception_4a = concatenate([inception_4a_3x3, inception_4a_5x5, inception_4a_pool, inception_4a_1x1], axis=3)

        # inception4e
        inception_4e_3x3 = Conv2D(160, (1, 1), strides=(1, 1), name='inception_4e_3x3_conv' + '1')(inception_4a)
        inception_4e_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_4e_3x3_bn' + '1')(inception_4e_3x3)
        inception_4e_3x3 = Activation('relu')(inception_4e_3x3)
        inception_4e_3x3 = ZeroPadding2D(padding=(1, 1))(inception_4e_3x3)
        inception_4e_3x3 = Conv2D(256, (3, 3), strides=(2, 2), name='inception_4e_3x3_conv' + '2')(inception_4e_3x3)
        inception_4e_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_4e_3x3_bn' + '2')(inception_4e_3x3)
        inception_4e_3x3 = Activation('relu')(inception_4e_3x3)

        inception_4e_5x5 = Conv2D(64, (1, 1), strides=(1, 1), name='inception_4e_5x5_conv' + '1')(inception_4a)
        inception_4e_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_4e_5x5_bn' + '1')(inception_4e_5x5)
        inception_4e_5x5 = Activation('relu')(inception_4e_5x5)
        inception_4e_5x5 = ZeroPadding2D(padding=(2, 2))(inception_4e_5x5)
        inception_4e_5x5 = Conv2D(128, (5, 5), strides=(2, 2), name='inception_4e_5x5_conv' + '2')(inception_4e_5x5)
        inception_4e_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_4e_5x5_bn' + '2')(inception_4e_5x5)
        inception_4e_5x5 = Activation('relu')(inception_4e_5x5)

        inception_4e_pool = MaxPooling2D(pool_size=3, strides=2)(inception_4a)
        inception_4e_pool = ZeroPadding2D(padding=((0, 1), (0, 1)))(inception_4e_pool)

        inception_4e = concatenate([inception_4e_3x3, inception_4e_5x5, inception_4e_pool], axis=3)

        # inception5a
        inception_5a_3x3 = Conv2D(96, (1, 1), strides=(1, 1), name='inception_5a_3x3_conv' + '1')(inception_4e)
        inception_5a_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_5a_3x3_bn' + '1')(inception_5a_3x3)
        inception_5a_3x3 = Activation('relu')(inception_5a_3x3)
        inception_5a_3x3 = ZeroPadding2D(padding=(1, 1))(inception_5a_3x3)
        inception_5a_3x3 = Conv2D(384, (3, 3), strides=(1, 1), name='inception_5a_3x3_conv' + '2')(inception_5a_3x3)
        inception_5a_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_5a_3x3_bn' + '2')(inception_5a_3x3)
        inception_5a_3x3 = Activation('relu')(inception_5a_3x3)

        inception_5a_pool = Lambda(lambda x: x ** 2, name='power2_5a')(inception_4e)
        inception_5a_pool = AveragePooling2D(pool_size=(3, 3), strides=(3, 3))(inception_5a_pool)
        inception_5a_pool = Lambda(lambda x: x * 9, name='mult9_5a')(inception_5a_pool)
        inception_5a_pool = Lambda(lambda x: K.sqrt(x), name='sqrt_5a')(inception_5a_pool)

        inception_5a_pool = Conv2D(96, (1, 1), strides=(1, 1), name='inception_5a_pool_conv' + '')(inception_5a_pool)
        inception_5a_pool = BatchNormalization(axis=3, epsilon=0.00001, name='inception_5a_pool_bn' + '')(inception_5a_pool)
        inception_5a_pool = Activation('relu')(inception_5a_pool)
        inception_5a_pool = ZeroPadding2D(padding=(1, 1))(inception_5a_pool)

        inception_5a_1x1 = Conv2D(256, (1, 1), strides=(1, 1), name='inception_5a_1x1_conv' + '')(inception_4e)
        inception_5a_1x1 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_5a_1x1_bn' + '')(inception_5a_1x1)
        inception_5a_1x1 = Activation('relu')(inception_5a_1x1)

        inception_5a = concatenate([inception_5a_3x3, inception_5a_pool, inception_5a_1x1], axis=3)

        # inception_5b
        inception_5b_3x3 = Conv2D(96, (1, 1), strides=(1, 1), name='inception_5b_3x3_conv' + '1')(inception_5a)
        inception_5b_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_5b_3x3_bn' + '1')(inception_5b_3x3)
        inception_5b_3x3 = Activation('relu')(inception_5b_3x3)
        inception_5b_3x3 = ZeroPadding2D(padding=(1, 1))(inception_5b_3x3)
        inception_5b_3x3 = Conv2D(384, (3, 3), strides=(1, 1), name='inception_5b_3x3_conv' + '2')(inception_5b_3x3)
        inception_5b_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_5b_3x3_bn' + '2')(inception_5b_3x3)
        inception_5b_3x3 = Activation('relu')(inception_5b_3x3)

        inception_5b_pool = MaxPooling2D(pool_size=3, strides=2)(inception_5a)

        inception_5b_pool = Conv2D(96, (1, 1), strides=(1, 1), name='inception_5b_pool_conv' + '')(inception_5b_pool)
        inception_5b_pool = BatchNormalization(axis=3, epsilon=0.00001, name='inception_5b_pool_bn' + '')(inception_5b_pool)
        inception_5b_pool = Activation('relu')(inception_5b_pool)

        inception_5b_pool = ZeroPadding2D(padding=(1, 1))(inception_5b_pool)

        inception_5b_1x1 = Conv2D(256, (1, 1), strides=(1, 1), name='inception_5b_1x1_conv' + '')(inception_5a)
        inception_5b_1x1 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_5b_1x1_bn' + '')(inception_5b_1x1)
        inception_5b_1x1 = Activation('relu')(inception_5b_1x1)

        inception_5b = concatenate([inception_5b_3x3, inception_5b_pool, inception_5b_1x1], axis=3)

        av_pool = AveragePooling2D(pool_size=(3, 3), strides=(1, 1))(inception_5b)
        reshape_layer = Flatten()(av_pool)
        dense_layer = Dense(128, name='dense_layer')(reshape_layer)
        norm_layer = Lambda(lambda x: K.l2_normalize(x, axis=1), name='norm_layer')(dense_layer)

        # Final Model
        model = Model(inputs=[myInput], outputs=norm_layer)
        return model

    # ------------------------
    def findCosineDistance(self, source_representation, test_representation):
        a = np.matmul(np.transpose(source_representation), test_representation)
        b = np.sum(np.multiply(source_representation, source_representation))
        c = np.sum(np.multiply(test_representation, test_representation))
        return 1 - (a / (np.sqrt(b) * np.sqrt(c)))


    def l2_normalize(self, x, axis=-1, epsilon=1e-10):
        output = x / np.sqrt(np.maximum(np.sum(np.square(x), axis=axis, keepdims=True), epsilon))
        return output


    def findEuclideanDistance(self, source_representation, test_representation):
        euclidean_distance = source_representation - test_representation
        euclidean_distance = np.sum(np.multiply(euclidean_distance, euclidean_distance))
        euclidean_distance = np.sqrt(euclidean_distance)
        # euclidean_distance = l2_normalize(euclidean_distance)
        return euclidean_distance

    def loadFaces(self, dirPath):
        """
        # 데이터셋 내 이미지의 어레이를 리턴한다
        """
        face = list()
        for fileName in os.listdir(dirPath):
            path = dirPath + fileName
            img = Image.open(path)
            faceArray = np.asarray(img)
            face.append(faceArray)
        return face

    def representationFileSetting(self, employees):
        """
        사진이미지를 이용하여 모델 설정
        :return: dict
        """
        # ------------------------
        self.model = self.builtModel()
        print("model built")
        # ------------------------

        # https://drive.google.com/file/d/1LSe1YCV1x-BfNnfb7DFZTNpv_Q9jITxn/view
        self.model.load_weights('./00.Resource/weights/openface_weights.h5')
        print("weights loaded")
        # ------------------------
        # cosine, euclidean
        if self.metric == "cosine":
            self.threshold = 0.45
        else:
            self.threshold = 0.95
        # ------------------------

        for subDir in os.listdir(self.employee_pictures):
            path = self.employee_pictures + '/' + subDir + '/'
            # path = employee_pictures + '/' + subDir
            if not os.path.isdir(path):
                continue

            # faceImgs = self.loadFaces(path)
            for file in os.listdir(path):
                if not os.path.isdir(file):
                    employee, extension = file.split(".")
                    # print("===== search file name :: ", employee)
                    # print("===== filePath :: {}/{}.{}".format(path,employee, extension))
                    img = self.preprocess_image(path + '%s.%s' % (employee, extension))
                    representation = self.model.predict(img)[0, :]
                    employees[employee] = representation

        print("employees build success")
        return employees


    def defaultSetOpenface(self):
        """
        openface 구동을 위한 초기 설정
        순서 : defaultSetOpenface -> runPredictOpenface
        :return:
        """
        self.employees = dict()
        self.employees = self.representationFileSetting(self.employees)

    def runPredictOpenface(self, img):
        """
        openface 구동
        :param img:
        :return: img
        """
        if self.osName == "Windows":
            # self.face_cascade = cv2.CascadeClassifier('C:\\Users\\JK\\Documents\\GitHub\\bitproject\\haarcascade_frontface.xml')
            self.face_cascade = cv2.CascadeClassifier(
                os.path.join(site.getsitepackages()[1],"cv2/data/haarcascade_frontalface_default.xml"))
        elif self.osName == "Linux":
            # self.face_cascade = cv2.CascadeClassifier('/home/bit/anaconda3/envs/faceRecognition/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml')
            self.face_cascade = cv2.CascadeClassifier(
                os.path.join(site.getsitepackages()[0],"cv2/data/haarcascade_frontalface_default.xml"))

        faces = self.face_cascade.detectMultiScale(img, 1.3, 5)
        extList = list()    # 결과 데이터 리스트
        extDict = dict()  # 결과 데이터 딕셔너리

        # 클래스명에서 숫자를 제거하기위한 정규식
        expText = re.compile('[^0-9%.() ]')

        if len(faces) != 0:
            for (x, y, w, h) in faces:
                extDict = dict()
                if w > 60:  # discard small detected faces
                    cv2.rectangle(img, (x, y), (x + w, y + h), self.color, 1)  # draw rectangle to main image

                    detected_face = img[int(y):int(y + h), int(x):int(x + w)]  # crop detected face
                    detected_face = cv2.resize(detected_face, (96, 96))  # resize to 96x96

                    img_pixels = image.img_to_array(detected_face)
                    img_pixels = np.expand_dims(img_pixels, axis=0)
                    # employee dictionary is using preprocess_image and it normalizes in scale of [-1, +1]
                    img_pixels /= 127.5
                    img_pixels -= 1

                    captured_representation = self.model.predict(img_pixels)[0, :]

                    # print("captured_representation :: ")
                    # print(captured_representation)

                    distances = []

                    for i in self.employees:
                        employee_name = i
                        source_representation = self.employees[i]

                        if self.metric == "cosine":
                            distance = self.findCosineDistance(captured_representation, source_representation)
                        elif self.metric == "euclidean":
                            distance = self.findEuclideanDistance(captured_representation, source_representation)

                        if self.dump:
                            print("(employee_name)=" + employee_name, " : (distance)=", distance)
                        distances.append(distance)

                    # print("distances :: ")
                    # print(distances)

                    label_name = 'Unknown'
                    similarity = 0
                    index = 0
                    for i in self.employees:
                        employee_name = i
                        if index == np.argmin(distances):
                            if distances[index] < self.threshold:
                                # print("detected: ",employee_name)
                                if self.metric == "euclidean":
                                    similarity = 100 + (90 - 100 * distance)
                                elif self.metric == "cosine":
                                    similarity = 100 + (40 - 100 * distance)

                                # print("similarity :: ", similarity)
                                if similarity > 99.99:
                                    similarity = 99.99

                                label_name = "%s (%s%s)" % (employee_name, str(round(similarity, 2)), '%')
                                break
                            else:
                                label_name = "?"
                                similarity = 00.00

                        index = index + 1

                    print("======================================================")
                    print("label_name :: {}".format(label_name))
                    print("Percent :: {} %".format(str(round(similarity, 2))))

                    if similarity != 0 and label_name != "Unknown":
                        cv2.putText(img, label_name, (int(x + w + 15), int(y - 64)), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 3)

                        if self.dump:
                            print("call dump----------------------")

                        # connect face and text
                        cv2.line(img, (x + w, y - 64), (x + w - 25, y - 64), self.color, 3)
                        cv2.line(img, (int(x + w / 2), y), (x + w - 25, y - 64), self.color, 3)

                        # 검출 결과 데이터 저장
                        extDict['x'] = x
                        extDict['y'] = y
                        extDict['w'] = w
                        extDict['h'] = h
                        extDict['percent'] = str(round(similarity, 2))
                        extDict['labelname'] = "".join(expText.findall(employee_name))
                        extList.append(extDict)

            # 프레임 이미지(박스:Y), 결과데이터(박스좌표, 검출결과(이름,정확도))
        return img, extList


    def runVideo(self):
        # ------------------------
        self.model = self.builtModel()
        print("model built")
        # ------------------------

        # https://drive.google.com/file/d/1LSe1YCV1x-BfNnfb7DFZTNpv_Q9jITxn/view
        self.model.load_weights('./00.Resource/weights/openface_weights.h5')
        print("weights loaded")
        # ------------------------
        metric = "cosine"  # cosine, euclidean
        if metric == "cosine":
            threshold = 0.45
        else:
            threshold = 0.95
        # ------------------------


        employees = dict()

        for subDir in os.listdir(self.employee_pictures):
            path = self.employee_pictures + '/' + subDir + '/'
            # path = employee_pictures + '/' + subDir
            if not os.path.isdir(path):
                continue

            # faceImgs = self.loadFaces(path)
            for file in os.listdir(path):
                if not os.path.isdir(file):
                    employee, extension = file.split(".")
                    # print("===== search file name :: ", employee)
                    # print("===== filePath :: {}/{}.{}".format(path,employee, extension))
                    img = self.preprocess_image(path + '%s.%s' % (employee, extension))
                    representation = self.model.predict(img)[0, :]

                    # print("representation :: ")
                    # print(representation)

                    employees[employee] = representation

        # print("employee representations retrieved successfully")
        # print("employees :: ")
        # print(employees)

        # ------------------------


        cap = cv2.VideoCapture(self.videoFilePath)  # webcam

        while (True):
            ret, img = cap.read()
            faces = self.face_cascade.detectMultiScale(img, 1.3, 5)

            for (x, y, w, h) in faces:
                if w > 60:  # discard small detected faces
                    cv2.rectangle(img, (x, y), (x + w, y + h), self.color, 1)  # draw rectangle to main image

                    detected_face = img[int(y):int(y + h), int(x):int(x + w)]  # crop detected face
                    detected_face = cv2.resize(detected_face, (96, 96))  # resize to 96x96

                    img_pixels = image.img_to_array(detected_face)
                    img_pixels = np.expand_dims(img_pixels, axis=0)
                    # employee dictionary is using preprocess_image and it normalizes in scale of [-1, +1]
                    img_pixels /= 127.5
                    img_pixels -= 1

                    captured_representation = self.model.predict(img_pixels)[0, :]

                    distances = []

                    for i in employees:
                        employee_name = i
                        source_representation = employees[i]

                        if metric == "cosine":
                            distance = self.findCosineDistance(captured_representation, source_representation)
                        elif metric == "euclidean":
                            distance = self.findEuclideanDistance(captured_representation, source_representation)

                        if self.dump:
                            print(employee_name, ": ", distance)
                        distances.append(distance)

                    label_name = 'unknown'
                    index = 0
                    for i in employees:
                        employee_name = i
                        if index == np.argmin(distances):
                            if distances[index] <= threshold:
                                # print("detected: ",employee_name)

                                if metric == "euclidean":
                                    similarity = 100 + (90 - 100 * distance)
                                elif metric == "cosine":
                                    similarity = 100 + (40 - 100 * distance)

                                print("similarity :: ",similarity)
                                if similarity > 99.99: similarity = 99.99

                                label_name = "%s (%s%s)" % (employee_name, str(round(similarity, 2)), '%')

                                break

                        index = index + 1

                    cv2.putText(img, label_name, (int(x + w + 15), int(y - 64)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),2)

                    if self.dump:
                        print("----------------------")

                    # connect face and text
                    cv2.line(img, (x + w, y - 64), (x + w - 25, y - 64), self.color, 1)
                    cv2.line(img, (int(x + w / 2), y), (x + w - 25, y - 64), self.color, 1)

            cv2.imshow('img', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # press q to quit
                break

        # kill open cv things
        cap.release()
        cv2.destroyAllWindows()

# if __name__ == "__main__":
#
#     openFace = openfaceRealTime()
#     openFace.runVideo()