#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
特征提取
"""

import os
import re
import time
from PIL import Image
from cfg import *
import numpy as np
from compiler.ast import flatten


def get_feature(one_img_dir=None, img_path=None, im=None):
    """
    获取指定图片的特征值, 将image图片转为数组 -> str格式输出
    :param one_img_dir, img_dir, im: 文件夹名字, 文件名字(坐标), Image对象
    :return: str 第一个元素为y 其余为x
    """
    if not im:
        im = Image.open(os.path.join(one_img_dir, img_path))
    x = flatten(np.array(im).tolist())   # 1936 个元素
    """
    使用像素缩放方法,减少了3/4的元素个数,但会对坐标精准度有一定影响
    """
    # arr = np.array(im)
    # w, h = im.size
    # new_arr = []
    # for x in range(0, w, 2):
    #     for y in range(0, h, 2):
    #         mean = arr[x:x+2, y:y+2].mean()
    #         new_arr.append(mean)
    # x = flatten(new_arr)

    if '-' in img_path:
        rule = re.findall(r'(-\d+)', img_path)[0]
        y = int(rule)

    elif '+' in img_path:
        rule = re.findall(r'\+(\d+)', img_path)[0]
        y = int(rule)
    else:
        y = 99

    x = ' '.join(str(i) for i in x)
    yx = ' '.join([str(y), x])
    return yx


def get_train_txt():
    """
    获取训练样本特征集文件
    :return:
    """
    listdir = os.listdir(cut_pic_path)
    train_xy_f = open(knn_train_xy, 'wb')

    for img_dirs in listdir:
        one_img_dir = os.path.join(cut_pic_path, img_dirs)
        if os.listdir(one_img_dir):
            pic_dirs = os.listdir(one_img_dir)
            for img_path in pic_dirs:
                yx = get_feature(one_img_dir, img_path)
                train_xy_f.write(yx)
                train_xy_f.write('\n')


def get_test_txt():
    """
    获取测试样本特征集文件
    :return:
    """
    listdir = os.listdir(test_cut_pic_path)
    train_xy_f = open(knn_test_xy, 'wb')

    for img_dirs in listdir:
        one_img_dir = os.path.join(test_cut_pic_path, img_dirs)
        if os.listdir(one_img_dir):
            pic_dirs = os.listdir(one_img_dir)
            for img_path in pic_dirs:
                yx = get_feature(one_img_dir, img_path)
                train_xy_f.write(yx)
                train_xy_f.write('\n')

    train_xy_f.close()


def get_one_train_feature(img_location, im):
    """
    获取单张图片的特征向量值
    :param im:
    :return: x_test, y_test
    """
    yx = get_feature(img_path=img_location, im=im).split(' ')
    x_list = []
    y_list = [yx[0]]
    x_list.append(yx[1:])
    x_np = np.array(x_list).astype(np.float)
    y_np = np.array(y_list).astype(np.int)
    return x_np, y_np


def get_feature_to_vector(knn_path):
    """
    读取文件,转为向量集
    :return:
    """
    x_list = []
    y_list = []
    with open(knn_path, 'rb') as f:
        lines = f.readlines()
        for line in lines:
            xy = line.split(' ')
            y_list.append(xy[0])
            x_list.append(xy[1:])
    x_np = np.array(x_list).astype(np.float)
    y_np = np.array(y_list).astype(np.int)
    return x_np, y_np


def convert_feature_to_vector(yx):
    """
    转化一条向量
    :param yx:
    :return:
    """
    x_list = []
    y_list = []
    xy = yx.split(' ')
    y_list.append(xy[0])
    x_list.append(xy[1:])
    x_np = np.array(x_list).astype(np.float)
    y_np = np.array(y_list).astype(np.int)
    return x_np, y_np


if __name__ == '__main__':
    start_time = time.time()
    get_train_txt()
    get_test_txt()
    print '获取训练.测试集用时 %s' % str(time.time()-start_time)
