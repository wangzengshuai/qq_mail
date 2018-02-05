#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型训练.测试
"""
import time
import re
import requests
from PIL import Image
from StringIO import StringIO
import numpy as np
from feature import get_feature_to_vector, get_feature, convert_feature_to_vector, get_one_train_feature
from sklearn.externals import joblib
from cfg import *
import os
from imgs_tools import to_bin, to_split
import mx_model

model = None
models = {
    'knn': knn_model_file,
    'svm': svm_model_file,
    'log': log_model_file,
}


def get_model(model_type='knn'):
    """
    加载模型
    :return:
    """
    global model
    if not model:
        mx = joblib.load(models.get(model_type))
    return mx


def train_model(model_type='knn'):
    x_train, y_train = get_feature_to_vector(knn_train_xy)
    fun = getattr(mx_model, 'mx_' + model_type)
    mx = fun(x_train, y_train)
    joblib.dump(mx, models.get(model_type))


def test_model(model_type='knn'):
    mx = get_model(model_type)
    listdir = os.listdir(test_cut_pic_path)
    a = 0
    b = 0
    for dir in listdir:  # 一张图片文件夹
        print '开始图片 %s' % dir
        imgs_path = os.listdir(os.path.join(test_cut_pic_path, dir))
        yes = 0
        no = 0
        succ_points = []
        need_point = 0
        for im_path in imgs_path:
            yx = get_feature(os.path.join(test_cut_pic_path, dir), im_path)
            x_test, y_test = convert_feature_to_vector(yx)
            y_pred = mx.predict(x_test)

            if not need_point and y_test[0] != 99:  # 获取实际坐标
                point = int(im_path.split(',')[0].split('(')[1])
                need_point = point + y_test[0]

            if y_pred[0] != 99:  # 获取猜测坐标集合
                point = int(im_path.split(',')[0].split('(')[1])
                succ_points.append(y_pred[0] + point)

            if y_pred[0] == y_test[0]:
                if y_test[0] not in [99, '99']:
                    print '猜对了一张目标图片 %s' % im_path
                    yes += 1
            else:
                no += 1
                if y_test[0] != 99:
                    print '猜错了: 目标图%s猜为错图 %s' % (im_path, y_pred[0])
                else:
                    print '猜错了: 错图%s猜为目标图 %s' % (im_path, y_pred[0])

        middle_point = int(np.mean(succ_points)) if succ_points else 0  # 获取猜测坐标

        print '此图 共猜对了%s个,猜错了%s个,正确率%s,中心点为%s , 猜出的中心点为%s' % (yes, no, yes / (float(yes) + no) * 100, need_point,  middle_point)

        if need_point == middle_point or abs(need_point - middle_point) <= 2:
            a += 1
        else:
            b += 1

    print '最终猜对的有%s个,猜错的有%s个, 正确率%s' % (a, b, float(a) / (a + b) * 100)


def img_forecast(im, start_point=18, model_type='knn'):
    """
    根据图片预测出需要位移距离,
    图片默认大小为(280, 158)
    :param model_type: 模型类型
    :param start_point: 验证图片在大图中的初始坐标
    :param im: 大图
    :return: 预测出的坐标,预测错误返回None
    """
    w, h = im.size
    if w != 280:
        im = im.resize((280, 158))
    im = to_bin(im)
    img_dict_list = to_split(im)
    points = []
    for img_dict in img_dict_list:
        for point, img in img_dict.iteritems():
            x_test, y_test = get_one_train_feature(str(point), img)
            mx = get_model(model_type)
            y_pred = mx.predict(x_test)
            if y_pred[0] != 99:
                points.append(point[0] + y_pred[0])
                print point
    if points:
        std = np.std(points)
        mean = np.mean(points)
        points = filter(lambda x: (x - mean) <= 2*std, points)

    middle_point = int(np.mean(points)) if points else None

    if middle_point:  # 预测出了横坐标

        # 按照图片与真是图片大小比例,计算出需要横移的距离
        need_point = middle_point - start_point
        return int(need_point)

    else:  # 没有预测出结果
        return None


def test_by_request():

    # svm缺点:耗内存,计算过于复杂,计算速度太慢 一张原图的识别用时300s左右
    url = 'https://ssl.captcha.qq.com/cap_union_new_getcapbysig?aid=522005705&asig=&captype=&protocol=https&clientype=2&disturblevel=&apptype=2&curenv=inner&ua=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS82My4wLjMyMzkuODQgU2FmYXJpLzUzNy4zNg==&sess=6ABY3A2-oKuXnhxziu-0LAfxZx_uThQLgkdl-Tl5juMNkI6SPiCdd34Mu_m3A-yojvp99LS8hdKE2Md_6q0nOEoHsTV42K_8N9HU5PqScqOCqIpHcEP6chsyw94if9vVSTHenJVyxEkSRdMGihfdRHrTtqDV8UAXhtLlCicD9iXVkAhsG2D4w2uws522wL-HueepCJeX4xY*&theme=&sid=6517843182398749354&noBorder=noborder&fb=1&forcestyle=undefined&showtype=embed&uid=54940987%40qq.com&cap_cd=hrCDtRYP9zrvCsZC10dGg1ssxL8CrFDkeKCEzT6ggPcqI93PmmB-GA**&lang=2052&rnd=342571&rand=0.7411912977283364&vsig=c01gL0cMwSNJp-lNrhhfaViON3Nai4hW0TwERdJC3O76mDrPKtuAXOKryJq1f9hL0lY_LwQziMjEaN1wLuW_JC-i1zKOmwjhCpRZsNdUzk2dGsq5de7sj7uM6UGH0gyCEETXbqLUq5IDC21WMCIAhvJRzfFJb6x6rbNWAyJJaxPsGDc2MYDhy-7oQ**&img_index=1',
    conn = requests.get('https://ssl.captcha.qq.com/cap_union_new_getcapbysig?aid=522005705&asig=&captype=&protocol=https&clientype=2&disturblevel=&apptype=2&curenv=inner&ua=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS82My4wLjMyMzkuODQgU2FmYXJpLzUzNy4zNg==&sess=6ABY3A2-oKuXnhxziu-0LAfxZx_uThQLgkdl-Tl5juMNkI6SPiCdd34Mu_m3A-yojvp99LS8hdKE2Md_6q0nOEoHsTV42K_8N9HU5PqScqOCqIpHcEP6chsyw94if9vVSTHenJVyxEkSRdMGihfdRHrTtqDV8UAXhtLlCicD9iXVkAhsG2D4w2uws522wL-HueepCJeX4xY*&theme=&sid=6517843182398749354&noBorder=noborder&fb=1&forcestyle=undefined&showtype=embed&uid=54940987%40qq.com&cap_cd=hrCDtRYP9zrvCsZC10dGg1ssxL8CrFDkeKCEzT6ggPcqI93PmmB-GA**&lang=2052&rnd=342571&rand=0.5236171646472287&vsig=c01A3Zto28RCk-px39_pZD5pApAUElyoetL3ZZa6-cYqaEOip-Q44nURYDcBRUyq8_EWBBj3uvaVZUzclr1tEY803Dt3JoX3CZynu5wdw_Gk4-eABVmrSfvSSJryBgHPCyQpXkzkxcafFm-vSRgfLDdZuM1LY5nDOY_r67zxnj6F-O5iOJtkngXuQ**&img_index=1', stream=True, verify=False)
    im = Image.open(StringIO(conn.content))
    im = im.resize((280, 158))
    im.save('a.png')
    need_point = img_forecast(im, model_type='log')
    print '位移坐标:%s' % need_point


if __name__ == '__main__':
    start_time = time.time()

    # train_model('log')  # 训练模型
    # test_model('log')  # 测试模型

    test_by_request()  # 在线下载测试

    print '用时 %s' % str(time.time() - start_time)


