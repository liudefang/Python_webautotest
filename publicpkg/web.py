#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    : 2018/2/7 18:14
# @Author  : mike.liu
# @File    : web.py
import configparser


class Web:
    '''配置要测试的Web项目的url，登录用户名，登录密码等'''
    def __init__(self,web_config_file):
        config = configparser.ConfigParser()
        # 从配置文件中读取数据库服务器IP、域名，端口
        config.read(web_config_file,encoding='utf-8')
        self.web_url = config['WEB_SITE']['web_url']
        self.username = config['WEB_SITE']['username']
        self.password = config['WEB_SITE']['password']

    def get_web_url(self):
        return self.web_url

    def get_username(self):
        return self.username

    def get_password(self):
        return  self.password