#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    : 2018/2/7 16:56
# @Author  : mike.liu
# @File    : runmode.py
import configparser


class RunMode:
    '''配置运行模式'''
    def __init__(self,runmode_config_file):
        config = configparser.ConfigParser()
        config.read(runmode_config_file,encoding = 'utf-8')

        self.runmode = config.get('RUNMODE','runmode')
        self.testplan_list = eval(config.get('TESTPLAN','testplans'))
        self.globalcase_list = eval(config.get('GLOBALCASE','globalcases'))

    def get_runmode(self):
        return self.runmode

    def get_testplans(self):
        return self.testplan_list

    def get_globalcase_list(self):
        return self.globalcase_list