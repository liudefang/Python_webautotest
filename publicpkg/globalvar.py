#!/usr/bin/env python
# -*- coding:utf-8 -*-

# -*- encoding: utf-8 -*-
# @Time    : 2018/2/6 17:33
# @Author  : mike.liu
# @File    : globalvar.py
import configparser

from publicpkg import database
from publicpkg import othertools
from publicpkg import runmode
from publicpkg import seleniumutil
from publicpkg import web,browserconf,sendmail,ftp
from publicpkg.mylogger import logger
from web_auto_test.htmlreporter import HtmlReport

__all__ = ['web_site', 'db', 'ftp', 'browserconf', 'other_tools', 'run_mode', 'browser_type_to_test', 'selenium_util','html_report', 'report_name'
           ,'mymail', 'screenshot_dir_path', 'remote_screenshot_baselink', 'testplan_list','globalcase_list']



logger.info('#####################正在初始化全局配置#####################')
logger.info('正在选择数据库运行环境和站点运行环境')
# 数据库环境和站点配置
config = configparser.ConfigParser()
config.read('../config/test_env_switch.conf',encoding='utf-8')

web_site = int(config['TEST_ENV']['web_site']) # 获取站点(测试环境，预发布环境等
db_env = int(config['TEST_ENV']['db_env'])  # 获取数据库测试环境（(测试环境数据库，预发布数据库等）

#选择要测试的web站点
if web_site == 1:
    logger.info('在测试环境执行测试，正在获取测试环境的web site')
    web_site = web.Web('../config/web_site/test.properties')  #测试环境的web
elif web_site == 2:
    logger.info('在开发环境执行测试，正在获取开发环境的web site')
    web_site = web.Web('../config/web_site/dev.properties')  #开发环境的web
elif web_site == 3:
    logger.info('在预发布环境执行测试，正在获取预发布环境的web site')
    web_site = web.Web('../config/web_site/release.properties')  # release环境的web

# 选择要测试的数据库环境
if db_env == 1:
    logger.info('在测试环境执行测试，正在获取测试环境的数据库')
    db = database.DataBase('../config/db_env/db_test.conf', 'DATABASE')  #测试环境的db
elif db_env == 2:
    logger.info('在开发环境执行测试，正在获取开发环境的数据库')
    db = database.DataBase('../config/db_env/db_dev.conf', 'DATABASE')   #开发环境的db
elif db_env == 3:
    logger.info('在预发布环境执行测试，正在获取预发布环境的数据库')
    db = database.DataBase('../config/db_env/db_release.conf', 'DATABASE')   #release环境的db

#ftp配置
logger.info('正在进行ftp配置')
ftp = ftp.MyFTP('../config/ftp.conf')

#邮件配置
mymail = sendmail.MyMail('../config/mail.conf')

#运行模式配置
logger.info('正在获取运行模式')
runmode_obj = runmode.RunMode('../config/runmode.conf')
run_mode = runmode_obj.get_runmode()
run_mode = run_mode.lower()
logger.info('运行模式为:%s' % runmode)

testplan_list = runmode_obj.get_testplans() #待测试计划列表
logger.info('测试计划配置:%s' % testplan_list)

globalcase_list = runmode_obj.get_globalcase_list() # 全局初始化用例列表
logger.info('全局初始化用例配置:%s' % globalcase_list)

#浏览器配置
logger.info('正在获取浏览器配置')
browserconf = browserconf.BrowserConfigure('../config/browser.conf')
browser_type_to_test = browserconf.get_browser_type_to_test()
browser_type_to_test = eval(browser_type_to_test)
logger.info('获取需要进行测试的浏览器有：%s' % browser_type_to_test)

#其它工具类和selenium操作封装类
logger.info('正在初始化其它工具对象')
other_tools = othertools.OtherTools()
selenium_util = seleniumutil.SeleniumUtil()

logger.info('正在进行截图基路径配置')
config.read('../config/screenshot.conf', encoding='utf-8')
screenshot_dir_path = config['SCREENSHOT']['dir_path']
remote_screenshot_baselink = config['SCREENSHOT']['remote_screenshot_baselink']
other_tools.mkdirs_once_many(screenshot_dir_path)  # 防止目录不存在，创建目录
logger.info('截图报存基路径为：%s' % screenshot_dir_path)


#测试报告配置
logger.info('正在进行测试报告配置')
logger.info('--1、读取测试报告路径及文件名')
config.read('../config/report.conf', encoding='utf-8')
dir_of_report = config['REPORT']['dir_of_report']
report_name = config['REPORT']['report_name']

logger.info('--2、构造测试报告')
html_report = HtmlReport('test report','web_autotest_report')

logger.info('--3、设置报告生成路径')
html_report.mkdir_of_report(dir_of_report,other_tools)

logger.info('#####################初始化全局配置完毕#####################')

