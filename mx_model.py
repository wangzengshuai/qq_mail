#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
sklearn 里面的算法实现模块
"""

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC


def mx_knn(train_x, train_y):
    # KNN近邻算法，函数名，KNeighborsClassifier
    mx = KNeighborsClassifier()
    mx.fit(train_x, train_y)
    return mx


def mx_svm(train_x, train_y):
    # SVM向量机算法，函数名，SVC
    mx = SVC(kernel='rbf', probability=True)
    mx.fit(train_x, train_y)
    return mx


def mx_log(train_x, train_y):
    # 逻辑回归算法，函数名，LogisticRegression
    mx = LogisticRegression(penalty='l2')
    mx.fit(train_x, train_y)
    return mx