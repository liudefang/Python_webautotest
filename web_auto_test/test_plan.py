#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    : 2018/2/9 9:00
# @Author  : mike.liu
# @File    : test_plan.py

'''
1.输入一个新测试计划的id，对该测试计划进行首轮测试（注：运行模式--run_tp，生成新测试计划报告）
2.输入一个旧测试计划的id，对该测试计划进行新一轮测试（注：运行模式--run_tp，生成新测试计划报告）
3.输入一个旧测试计划的id，只对该测试计划中所有失败的用例进行新一轮测试(注：运行模式--run_tp_fail_tc，不生成新测试计划报告)
'''
import threading
import time

from publicpkg.mylogger import logger
from web_auto_test.test_case import TestCase

class TestPlan:
    def __init__(self):
        pass

    def run_test_plan(self, browser_type, db, run_mode, tp_run_history_id, test_plan_id=0):
        '''运行测试用例或测试计划

        其中，run_mode为运行模式: run_tp - 运行测试计划， run_tp_fail_tc--运行测试计划中，所有失败的用例'''
        # 获取测试需要执行的测试用例ID列表
        test_case_list = []
        logger.info('正在获取本次测试需要执行的测试用列ID列表，测试计划名称')
        query_select = 'SELECT testcase_list, test_round_name FROM testcase_runround WHERE id = %s '
        query_value = (test_plan_id,)
        result = db.select_one_record(query_select, query_value)

        if result[1] != True or not result[0]:
            logger.warn('没找到归属于该测试计划的用例,停止运行计划')
            return 'Block'
        testcases_str = result[0][0]
        testplan_name = result[0][1]

        if testcases_str:
            test_case_str_list = testcases_str.split('~') # 形如 3~7~10~11
            test_case_map = map(int, test_case_str_list)
            for id in test_case_map:
                test_case_list.append(id)
            logger.info('获取到的的测试用例id列表为: %s' % test_case_list)
        else:
            logger.warn('未获取到测试用例ID列表,请检查测试计划id(test_plan_id = %d)是否输入正确' % test_plan_id)

        logger.info('####################### 开始运行测试计划 #######################')
        # 构造测试用例对象
        testcase_objects_list = []
        for test_case_id in test_case_list:
            test_case = TestCase(browser_type, db, test_case_id, tp_run_history_id,run_mode, test_plan_id, testplan_name)
            testcase_objects_list.append(test_case)

        run_time ='%d-%02d-%02d %d:%d:%d' % time.localtime()[0 : 6]  # 记录执行时间
        mutex_lock = threading.RLock()
        mutex_lock.acquire()
        for test_case in testcase_objects_list:
            # 运行用例
            test_case.start()
            # 等待用例运行完成
            test_case.join()
        mutex_lock.release()

        logger.info('####################### 测试计划已运行完毕 #######################')
        logger.info('正在统计测试计划执行的用例总数')
        query_select = 'SELECT count(testcaseId)  FROM testcase_reporter  WHERE runHistoryId = %s'
        query_value = (tp_run_history_id,)
        result = db.select_one_record(query_select, query_value)
        if result[1] != True or not result[0]:
            logger.error('没找到执行过的用例')
            run_testcase_total = 0
        else:
            run_testcase_total = result[0][0]
        logger.info('正在统计测试计划执行成功的用例总数')
        query_select = 'SELECT count(testcaseId)  FROM testcase_reporter WHERE runHistoryId = %s AND runResult=\'Pass\''
        query_value = (tp_run_history_id,)
        result = db.select_one_record(query_select, query_value)
        if result[1] != True or not result[0]:
            logger.warn('没找到执行成功的用例')
            run_testcase_passed_total = 0
        else:
            run_testcase_passed_total = result[0][0]

        logger.info('正在统计测试计划执行失败的用例总数')
        query_select = 'SELECT count(testcaseId)  FROM testcase_reporter WHERE runHistoryId = %s AND runResult=\'Fail\''
        query_value = (tp_run_history_id,)
        result = db.select_one_record(query_select, query_value)
        if result[1] != True or not result[0]:
            logger.info('没找到执行失败的用例')
            run_testcase_failed_total = 0
        else:
            run_testcase_failed_total = result[0][0]

        logger.info('正在统计测试计划执行被阻塞的用例总数')
        query_select = 'SELECT count(testcaseId)  FROM testcase_reporter WHERE runHistoryId = %s AND runResult=\'Block\''
        query_value = (tp_run_history_id,)
        result = db.select_one_record(query_select, query_value)
        if result[1] != True or not result[0]:
            logger.info('没找到执行被阻塞的用例')
            run_testcase_blocked_total = 0
        else:
            run_testcase_blocked_total = result[0][0]

        logger.info('正在统计测试计划执行成功的用例')
        query_select = 'SELECT testcaseId  FROM testcase_reporter WHERE runHistoryId = %s AND runResult=\'Pass\''
        query_value = (tp_run_history_id,)
        result = db.select_many_record(query_select, query_value)
        if result[1] != True or not result[0]:
            logger.warn('没找到执行成功的用例')
            run_testcase_passed = ''
        else:
            run_testcase_passed = str(result[0][0])

        logger.info('正在统计测试计划执行失败的用例')
        query_select = 'SELECT testcaseId  FROM testcase_reporter WHERE runHistoryId = %s AND runResult=\'Fail\''
        query_value = (tp_run_history_id,)
        result = db.select_many_record(query_select, query_value)
        if result[1] != True or not result[0]:
            logger.info('没找到执行失败的用例')
            run_testcase_failed = ''
        else:
            run_testcase_failed = str(result[0][0])

        logger.info('正在统计测试计划执行被阻塞的用例')
        query_select = 'SELECT testcaseId  FROM testcase_reporter WHERE runHistoryId = %s AND runResult=\'Block\''
        query_value = (tp_run_history_id,)
        result = db.select_many_record(query_select, query_value)
        if result[1] != True or not result[0]:
            logger.info('没找到计划执行被阻塞的用例')
            run_testcase_blocked = ''
        else:
            run_testcase_blocked = str(result[0][0])

        if  '运行流水' == run_mode:# 更新测试计划运行记录历史结果表
            logger.info('正在更新测试计划运行记录历史结果报表')
            query_update = 'UPDATE testplan_reporter SET browserType=\'%s\', runTc_total=%s,  runPassedTc_total=%s, runFailedTc_total=%s,' \
                                                                         'runBlockedTc_total=%s, runPassedTc=\'%s\', runFailedTc=\'%s\', runBlockedTc=\'%s\', runTime=\'%s\' WHERE runHistoryId= %s'
            query_value = (browser_type, run_testcase_total, run_testcase_passed_total, run_testcase_failed_total, run_testcase_blocked_total,
            run_testcase_passed, run_testcase_failed, run_testcase_blocked, run_time, tp_run_history_id)
            result = db.execute_update(query_update, query_value)
            if result[1] != True:
                logger.error('更新测试计划运行到测试计划运行报表失败:%s' % result[0])
                return
        elif '运行计划' == run_mode: #新增历史记录
            query_insert = 'INSERT INTO testplan_reporter' +'(testPlanId, testPlanName, runHistoryId, browserType, runTc_total, runPassedTc_total, runFailedTc_total,' \
                                                                         'runBlockedTc_total, runPassedTc, runFailedTc, runBlockedTc, runTime)'\
                            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            query_value = (test_plan_id, testplan_name, tp_run_history_id, browser_type, run_testcase_total, run_testcase_passed_total, run_testcase_failed_total, run_testcase_blocked_total,
                           run_testcase_passed, run_testcase_failed, run_testcase_blocked, run_time)
            logger.info('正在记录测试计划运行结果到测试计划报表')
            result = db.execute_insert(query_insert, query_value)
            if result[1] != True:
                logger.error('记录测试计划运行结果失败')




