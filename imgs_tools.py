#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
图片处理
"""
import os
import traceback
import uuid
from os.path import join

import time
from PIL import Image
from PIL import ImageEnhance

from cfg import *


def to_bin(im):
    """
    图片转灰度图
    :param im:
    :return:
    """
    im = im.convert('L')
    w, h = im.size
    if w != 280:
        im = im.resize((280, 158))
    return im


def to_split(im):
    """
    图片切割
    :param im:
    :return: 切割后图片list [{坐标:图片model},...]
    """
    w, h = im.size
    im_list = []
    block_size = int(round(w*0.157))  # 切割图片的尺寸

    step = block_size/3  # 每一步的步长
    start_point = block_size/2  # 初始位置

    for x in range(start_point, w - block_size, step):
        for y in range(0, h - block_size, step):
            try:
                im_crop = im.crop((x, y, x + block_size, y + block_size))
                im_list.append({(x, y): im_crop, })
            except Exception as e:
                traceback.format_exc()
                pass

    return im_list


def save_img_list(imgs, img_dir_path):
    """
    保存切割后的图片
    :param imgs: 图片集合
    :param img_dir_path: 图片文件夹
    :return:
    """
    if not os.path.isdir(img_dir_path):
        os.mkdir(img_dir_path)

    for img_dict in imgs:
        for img_key in img_dict:
            pic_path = join(img_dir_path, str(img_key) + '.png')
            img_dict[img_key].save(pic_path)


if __name__ == '__main__':
    start_time = time.time()
    # 批量转灰度图
    # if os.path.isdir(origin_path):
    #     dirs = os.listdir(origin_path)
    #     index = 0
    #     for path in dirs:
    #         im = Image.open(join(origin_path, path))
    #         index += 1
    #         print 'to bin for img %s' % index
    #         im = to_bin(im)
    #         im.save(join(bin_path, path))

    # 批量分割图片
    if os.path.isdir(bin_path):
        dirs = os.listdir(bin_path)
        index = 0
        for path in dirs:
            index += 1
            im = Image.open(join(bin_path, path))
            # im.save('data/test/%s.png' % str(uuid.uuid1()))
            img_list = to_split(im)
            print 'to split for img %s success' % index
            cut_dir = join(cut_pic_path, path)
            save_img_list(img_list, cut_dir)
    print '用时: %s' % (time.time()-start_time)