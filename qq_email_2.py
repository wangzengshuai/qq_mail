#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random
import sys
import traceback
import uuid
from StringIO import StringIO
import requests
import time
from PIL import Image
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from train import img_forecast

"""
    qq邮箱登陆测试
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
    time.sleep(3)


def main():
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--window-size=800,600')
    # chrome_options.add_argument('--window-position=0,0')
    # driver = webdriver.Chrome(r'/driver/chrome/2.30/chromedriver.exe', chrome_options=chrome_options)

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
    driver.find_element_by_id('switcher_plogin').click()  # 点击帐号密码登录

    try:
        name_input = WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located((By.ID, 'u')))
        if name_input:
            name_input.clear()
            name_input.send_keys('789528672@qq.com')
        else:
            print '页面出错,定位不到账户输入框'
            return
        pass_input = driver.find_element_by_id('p')
        if pass_input:
            pass_input.clear()
            pass_input.send_keys('3fddhffygk')
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
    div_code = None
    try:
        div_code = driver.find_element_by_xpath('//div[@id="newVcodeIframe"]')
    except NoSuchElementException as e:
        pass
    while div_code and div_code.get_attribute('innerHTML'):  # 出现验证码
        iframe = div_code.find_element_by_tag_name('iframe')
        if iframe:
            print '存在验证码iframe'
            driver.switch_to.frame(iframe)

            slideBkg_img = driver.find_element_by_id('slideBkg')
            w, h = slideBkg_img.size['width'], slideBkg_img.size['height']
            print '图片大小: (%s,%s)' % (w, h)

            slideBkg_img_src = slideBkg_img.get_attribute('src')
            print '验证码图片地址为:'
            print slideBkg_img_src
            # requests.cookies = get_cookie(driver)
            conn = requests.get(slideBkg_img_src, stream=True, verify=False)
            im = Image.open(StringIO(conn.content)).resize((w, h))
            # im.show()
            im.save('data/origin_img/%s.png' % str(uuid.uuid1()).replace('-', ''))
            need_range = img_forecast(im, model_type='log')
            print '识别结果:%s' % need_range
            # need_range = None
            if need_range:
                # 移动滑块
                svg = driver.find_element_by_xpath('//*[name()="svg"]/*[name()="rect"]')

                # 滑动
                action = ActionChains(driver)
                action.click_and_hold(svg)
                step = 0
                while step < need_range:
                    step_length = random.randint(0, 50)
                    if (step + step_length) < need_range:
                        action.move_by_offset(step_length, 2)
                        step += step_length
                    else:
                        surplus_step = need_range-step
                        action.move_by_offset(surplus_step, -5)
                        step = need_range
                action.release().perform()  # 松开鼠标
                action.reset_actions()
                print '滑动完毕 请验证登录结果'
                time.sleep(100)
                pass
            else:
                # 刷新验证码,重试
                refresh_img(driver)
                driver.switch_to.parent_frame()
                div_code = driver.find_element_by_xpath('//div[@id="newVcodeIframe"]')

        else:
            print '不存在验证码iframe'

    now_title = driver.find_element_by_name('title').text
    if now_title == 'QQ邮箱':
        print '登录成功..'
    elif now_title == '登录QQ邮箱':
        print '登录失败..'
    else:
        print '登录结果未知..'

    print '程序结束,关闭浏览器'
    driver.close()


if __name__ == '__main__':
    main()
