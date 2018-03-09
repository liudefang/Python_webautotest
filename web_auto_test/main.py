#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    : 2018/2/8 15:25
# @Author  : mike.liu
# @File    : main.py
import time
import datetime
import  os
from publicpkg.globalvar import *
from publicpkg.mylogger import logger
from web_auto_test.test_plan import TestPlan
from web_auto_test.test_case import TestCase

if __name__ == '__main__':
    try:
        for test_plan_id in testplan_list:
            testreport_filename_list = []   # 记录测试报告文件名，供发送邮件使用
            run_history_info_list = []      # 用于存储运行历史信息(执行编号，运行浏览器, 运行耗时)
            if run_mode == '运行用例':      # 运行指定测试用例
                test_case_id = int(input('请输入要进行测试的测试用例ID：'))
                logger.info('正在查询用例是否存在')
                query_select = 'SELECT id FROM testcases WHERE id = %s'
                query_value = (test_case_id, )
                qresult = db.select_one_record(query_select, query_value)
                if qresult[1] != True or not qresult[0]:
                    logger.warn('用例id：%s不存在' % test_case_id)
                    break
                logger.info('####################### 开始测试 #######################')
                for browser_type in browser_type_to_test:
                    start_time = datetime.datetime.now()
                    selenium_util.set_driver(browser_type)
                    driver = selenium_util.get_driver()
                    driver.get(web_site.get_web_url())
                    driver.implicitly_wait(30)  #页面等待
                    driver.maximize_window()    #浏览器最大化

                    tc_run_history_id = int(time.time())   # 作为运行测试用例的流水编号
                    logger.info('优先运行全局初始化用例 %s' % globalcase_list)
                    for globalcase_id in globalcase_list:
                        logger.info('正在查询全局用例[id=%s]是否存在' % globalcase_id)
                        query_select = 'SELECT id FROM testcases WHERE id = %s'
                        query_value = (globalcase_id, )
                        qresult = db.select_one_record(query_select, query_value)
                        if qresult[1] != True or not qresult[0]:
                            logger.warn('用例id:%s不存在' % test_case_id)
                            break
                        test_case = TestCase(browser_type, db, globalcase_id, tc_run_history_id, run_mode)
                        test_case.run()
                    test_case = TestCase(browser_type, db, test_case_id, tc_run_history_id, run_mode)
                    test_case.run()

                    logger.info('用例执行完成，正在关闭浏览器')
                    driver.close()
                    driver.quit()
                    logger.info('####################### 测试结束 #######################')

                    end_time = datetime.datetime.now()    #记录测试结束时间
                    time_took = end_time - start_time
                    run_history_info_list.append([tc_run_history_id,browser_type,time_took])
            elif run_mode == '运行计划': # 运行测试计划
                logger.info('####################### 开始测试 #######################')
                test_plan = TestPlan()
                for browser_type in browser_type_to_test:
                    start_time = datetime.datetime.now()   #记录测试开始时间
                    selenium_util.set_driver(browser_type)
                    driver = selenium_util.get_driver()
                    driver.get(web_site.get_web_url())
                    driver.implicitly_wait(30)   #页面等待
                    driver.maximize_window()      #浏览器最大化

                    tp_run_history_id = int(time.time())     # 作为运行测试计划流水编号
                    run_result = test_plan.run_test_plan(browser_type, db, run_mode, tp_run_history_id, test_plan_id)
                    if 'Block' == run_result:
                        logger.error('未找到测试计划[id=%s]的用例，提前终止用例' % test_plan_id)
                        logger.info('计划运行完成，正在关闭浏览器')
                        driver.close()
                        driver.quit()
                        break
                    logger.info('计划运行完成，正在关闭浏览器')
                    #driver.close()
                    driver.quit()
                    logger.info('####################### 测试结束 #######################')

                    end_time = datetime.datetime.now()     # 记录测试结束时间
                    time_took = end_time - start_time
                    run_history_info_list.append([tp_run_history_id, browser_type, time_took])
            elif run_mode == '运行流水': # 运行测试计划中，所有失败的用例
                 tp_run_history_id = int(input('请输入测试计划对应的流水号ID：'))
                 logger.info('####################### 开始测试 #######################')
                 start_time = datetime.datetime.now()      #记录测试开始时间
                 test_plan = TestPlan()
                 logger.info('正在获取测试计划流水记录对应的运行浏览器类型，所属测试计划')
                 query_select = 'SELECT browserType, testPlanId FROM testplan_reporter WHERE runHistoryId= %s GROUP BY runHistoryId'
                 query_value = (tp_run_history_id, )
                 result = db.select_one_record(query_select, query_value)
                 if result[1] != True or not result[0]:
                     logger.warn('没查询到计划执行流水记录，停止执行')
                     exit()
                 browser_type = result[0][0]
                 test_plan_id = result[0][1]
                 selenium_util.set_driver(browser_type)
                 driver = selenium_util.get_driver()
                 driver.get(web_site.get_web_url())
                 driver.implicitly_wait(30)   #页面等待
                 driver.maximize_window()     #浏览器最大化

                 test_plan.run_test_plan(browser_type, db, run_mode,tp_run_history_id, test_plan_id)

                 logger.info('已执行完计划中失败用例，正在关闭浏览器')
                 driver.close()
                 driver.quit()
                 logger.info('####################### 测试结束 #######################')

                 end_time = datetime.datetime.now()     # 记录测试结束时间

                 time_took = end_time - start_time
                 run_history_info_list.append([tp_run_history_id, browser_type, time_took])
            else:
                logger.error('获取运行模式失败或者获取了错误的run_mode,烦检查运行模式配置文件run_mode.conf')
                exit()    #退出

            if run_history_info_list == []:
                logger.info('运行计划/用例/流水失败，提前结束')
                break

            logger.info('运行完成,准备生成测试报告')
            report_id = time.strftime('%Y%m%d%H%M%S', time.localtime())   # 作为报告编号
            result = html_report.generate_html(report_name, run_history_info_list, report_id, db, run_mode)
            if result:
                logger.info('生成测试报告成功')
            else:
                logger.error('生成测试报告失败')

            logger.info('运行完成,准备上传截图')
            ftp.connect()
            ftp.login()

            logger.info('正在获取要上传的截图文件')
            screenshot_filelist = []
            for run_history_info in run_history_info_list:
                run_history_id = run_history_info[0]
                for root, dirs, files in os.walk(screenshot_dir_path):
                    temp_filepath_list = other_tools.get_filepath_with_specific_feature(root, files, str(run_history_id))
                    screenshot_filelist.extend(temp_filepath_list)

            logger.info('正在上传图片到ftp服务器')
            try:
                for file in screenshot_filelist:
                    remote_file_name = os.path.basename(file)
                    logger.info('正在上传文件：%s 到远程服务器：%s' % (file, remote_file_name))
                    ftp.upload_file(file, remote_file_name)
            except Exception as e:
                logger.error('上传截图到ftp服务器出错：%s' % e)
            ftp.quit()

            logger.info('运行完成，准备发送邮件')
            mymail.connect()
            mymail.login()
            mail_content =  'Hi，附件为web自动化测试报告，烦请查阅'
            mail_tiltle = '【测试报告】web自动化测试报告' + str(report_id)
            attachments = set([html_report.get_filename()])
            logger.info('邮件标题为：%s邮件内容为：%s，待发送邮件附件有 %s' % (mail_content, attachments, mail_tiltle))
            logger.info('正在发送测试报告邮件...')
            mymail.send_mail(mail_tiltle, mail_content, attachments)
            mymail.quit()
            logger.info('发送邮件成功')
            if run_mode != '运行计划':# 不为运行计划，只执行一次
                 exit()
    except Exception as e:
        logger.info('运行出错: %s' % e)
    finally:
        logger.info('正在关闭数据库')
        db.close()









