#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import traceback
import uuid
from StringIO import StringIO
import logging
import requests
import time
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

"""
    qq邮箱登陆和验证码循环下载
"""

reload(sys)
sys.setdefaultencoding("utf-8")

current_file_path = os.path.abspath(__file__)
current_dir_file_path = os.path.dirname(__file__)

from selenium import webdriver


def get_cookie(driver):
    cookie = [item["name"] + ":" + item["value"] for item in driver.get_cookies()]
    cookiestr = ';'.join(item for item in cookie)
    cook_map = {}
    for item in cookie:
        str = item.split(':')
        cook_map[str[0]] = str[1]


    print cook_map
    cookies = requests.utils.cookiejar_from_dict(cook_map, cookiejar=None, overwrite=True)
    return cookies


def refresh_img(driver):
    """
    刷新验证码图片
    :param driver:
    :return:
    """
    refresh_button = driver.find_element_by_css_selector('[class="tcaptcha-embed-refresh show-reload"]')
    refresh_button.click()
    time.sleep(5)
    driver.implicitly_wait(5)


def main():
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--window-size=800,600')
    # chrome_options.add_argument('--window-position=0,0')
    # driver = webdriver.Chrome(r'E:\driver\chrome\2.30\chromedriver.exe', chrome_options=chrome_options)

    # driver = webdriver.PhantomJS()
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get('https://mail.qq.com')
    iframe_login = driver.find_element_by_id('login_frame')
    login_location = iframe_login.location
    print '登录框坐标', login_location

    # 跳转到登录框iframe
    driver.switch_to.frame(iframe_login)
    time.sleep(1)
    driver.find_element_by_id('switcher_plogin').click()    # 点击帐号密码登录

    try:
        name_input = WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'u')))
        if name_input:
            name_input.clear()
            name_input.send_keys('454g54845@qq.com')
        else:
            print '页面出错,定位不到账户输入框'
            return
        pass_input = driver.find_element_by_id('p')
        if pass_input:
            pass_input.clear()
            pass_input.send_keys('rfdduivjm')
        else:
            print '页面出错,定位不到密码输入框'
    except Exception as e:
        traceback.format_exc()

    login_button = driver.find_element_by_id('login_button')
    if login_button.get_attribute('value'):
        print '定位到登录按钮'
        login_button.click()
    else:
        print '没有定位到登录按钮'

    print '点击登录,睡眠5秒'
    time.sleep(5)
    div_code = driver.find_element_by_xpath('//div[@id="newVcodeIframe"]')
    count = 0
    while div_code.get_attribute('innerHTML'):
        print div_code.get_attribute('innerHTML')
        iframe = div_code.find_element_by_tag_name('iframe')
        if iframe:
            print '存在验证码iframe'
            driver.switch_to.frame(iframe)

            for x in range(5):
                slideBkg_img = driver.find_element_by_id('slideBkg')
                slideBkg_img_src = slideBkg_img.get_attribute('src')
                print '验证码图片地址为:'
                print slideBkg_img_src
                requests.cookies = get_cookie(driver)
                conn = requests.get(slideBkg_img_src, stream=True, verify=False)

                im = Image.open(StringIO(conn.content))
                count +=1
                print '获取到图片: %s' % count
                if count > 500:
                    return
                # im.show()
                im.save('data/origin_img/%s.png' % str(uuid.uuid1()).replace('-', ''))
                refresh_img(driver)
            driver.switch_to.parent_frame()
            div_code = driver.find_element_by_xpath('//div[@id="newVcodeIframe"]')
        else:
            print '不存在验证码iframe'
    else:
        print '验证码div框不存在内容'
        return
    print '程序结束,关闭浏览器'
    driver.close()


if __name__ == '__main__':
    main()

