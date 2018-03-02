#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Created on 2018/2/2 9:18
 
@author: 'mike.liu' 
'''
import configparser


class BrowserConfigure:
    '''配置运行测试所用的浏览器类型'''
    def __init__(self,browser_conf):
        config = configparser.ConfigParser()
        config.read(browser_conf,encoding='utf-8')
        #获取需要运行的浏览器类型
        self.browser_type_need_test = config.get('BROWSER','browser_type')

    def get_browser_type_to_test(self):
        return self.browser_type_need_test