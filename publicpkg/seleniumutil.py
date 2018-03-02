#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    : 2018/2/7 17:06
# @Author  : mike.liu
# @File    : seleniumutil.py
import time
from selenium import webdriver

from publicpkg.mylogger import logger


class SeleniumUtil:
    def __init__(self):
        self.driver = None

    #设置驱动
    def set_driver(self,browser_type):
        try:
            browser_type = browser_type.lower()
            if 'ie' == browser_type:
                self.browser_type = 'Ie'
                self.driver = webdriver.Ie()
            elif 'chrome' == browser_type:
                self.browser_type = 'Chrome'
                self.driver = webdriver.Chrome()
            elif 'firefox' == browser_type:
                self.browser_type = 'Firefox'
                self.driver = webdriver.Firefox()
        except Exception as e:
            logger.error('设置浏览器驱动出错:%s' %e)

    def get_driver(self):
        return self.driver

    #智能等待
    def implicitly_wait(self,second):
        try:
            self.driver.implicitly_wait(second)
            return ('Pass','run_success')
        except Exception as e:
            return ('Fail',e)

    # 休眠
    def sleep(self, second):
        try:
            time.sleep(second)
            return ('Pass', 'run success')
        except Exception as e:
            return ('Fail', e)

    #浏览器最大化
    def maximize_window(self):
        try:
            self.driver.maximize_window()
            return ('Pass', 'run_success')
        except Exception as e:
            return ('Fail', e)

    #打开web站点
    def get(self,web_url):
        self.driver.get(web_url)

    #切换到iframe里面
    def switch_to_frame(self,frame):
        try:
            self.driver.swith_to_frame(frame)
            logger.info('切换至frame（id/name/xpath = %s）成功' % frame)
            return ('Pass', 'run success')
        except Exception as e:
             logger.error('切换至frame（id/name/xpath = %s）失败' % frame)
             return ('Fail', e)

    #根据id查找元素
    def find_element_by_id(self, id):
        return self.driver.find_element_by_id(id)


    # 根据xpath查找元素
    def find_element_by_xpath(self, xpath):
        return self.driver.find_element_by_xpath(xpath)


    # 根据name查找元素
    def find_element_by_name(self, name):
         return self.driver.find_element_by_name(name)


    # 根据link查找元素
    def find_element_by_link(self, link):
        return self.driver.find_element_by_link(link)


    # 根据link_text查找元素
    def find_element_by_link_text(self, link_text):
        return self.driver.find_element_by_link_text(link_text)


    # 根据partial_link_text查找元素
    def find_element_by_link_text(self, partial_link_text):
        return self.driver.find_element_by_partial_link_text(partial_link_text)

    # 根据css selector查找元素
    def find_element_by_css_selector(self, css_selector):
        return self.driver.find_element_by_css_selector(css_selector)

    # 根据tag_name查找元素
    def find_element_by_tag_name(self, tag_name):
       return self.driver.find_element_by_tag_name(tag_name)

    # 根据标签class name查找(查找单个)
    def find_element_by_class_name(self, class_name):
        return self.driver.find_element_by_class_name(class_name)

    # 根据标签class name查找，查找多个
    def find_element_by_class_name(self, class_name):
        return self.driver.find_elements_by_class_name(class_name)

    # 截图
    def get_screenshot_as_file(self, filepath):
        try:
           self.driver.get_screenshot_as_file(filepath)
           return ('Pass', '截图成功')
        except Exception as e:
           return ('Fail', e)

    # 断言页面源码是否存在某关键字或关键字字符串
    def assert_string_in_pagesource(self,assertString):


        try:
            assert assertString in self.driver.page_source, "%s not found in page source!" % assertString
            logger.info('断言信息为：%s' % assertString)
            return ('Pass', '断言成功')
        except Exception as e:
            return ('Fail', '断言失败')

