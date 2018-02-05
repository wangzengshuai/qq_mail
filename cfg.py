#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
路径配置文件
"""
from os.path import join

base_path = '/code/persion/python/small_identity_code/qq_mail/data'
origin_path = join(base_path, 'origin_img')
bin_path = join(base_path, 'bin_img')
cut_pic_path = join(base_path, 'cut_pic')
svm_root = join(base_path, 'svm_train')

knn_root = join(base_path, 'knn_train')
knn_train_xy = join(knn_root, 'train_xy.txt')
knn_test_xy = join(knn_root, 'test_xy.txt')
knn_model_file = join(knn_root, 'knn_model_file')
svm_model_file = join(knn_root, 'svm_model_file')
log_model_file = join(knn_root, 'log_model_file')



test_root = join(base_path, 'test')
test_cut_pic_path = join(base_path, 'test_pic')
