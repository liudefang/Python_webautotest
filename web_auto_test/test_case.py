#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    : 2018/2/8 17:19
# @Author  : mike.liu
# @File    : test_case.py


import threading
import time

from publicpkg.mylogger import logger
from web_auto_test.test_case_step import TestCaseStep

#运行具体测试用例
class TestCase(threading.Thread):
    def __init__(self, browser_type, db, test_case_id, run_history_id, runmode, test_plan_id=0, testplan_name='无计划'):
        logger.info('正在构造并初始化测试用例对象[id=%s]' % test_case_id)
        threading.Thread.__init__(self)
        self.test_case_id = test_case_id
        self.test_plan_id = test_plan_id
        self.browser_type = browser_type
        self.db = db
        self.run_history_id = run_history_id
        self.runmode = runmode
        self.testplan_name = testplan_name
        logger.info('初始测试用例完毕')

    def run(self):
        run_time = '%d-%02d-%02d %d:%d:%d' % time.localtime()[0 : 6]  # 记录执行时间
        testcase_run_result = 'Block'

        # 运行具体的用例步骤
        # 1.获取用例所有测试步骤
        test_case_steps = self.get_test_case_steps()
        if test_case_steps == []:
            logger.warn('未查找到归属用例[id=%s]的步骤' % self.test_case_id)
            return

        # 2.运行测试用例步骤
        test_case_step = TestCaseStep(self.test_case_id, self.test_plan_id)
        logger.info('开始执行测试步骤')
        for tc_step in test_case_steps:
            step_run_result = test_case_step.run_tc_step(self.browser_type, self.db, tc_step, self.run_history_id, self.runmode)
            testcase_run_result = step_run_result
            if step_run_result != 'Pass': #步骤运行失败，提前终止
                logger.info('用例[id：%s]步骤[步序：%s] 运行失败，停止运行用例' % (self.test_case_id, tc_step[0]))
                break

        if self.runmode == '运行流水': # 更新记录
            logger.info('测试步骤执行完毕，正在更新用例运行结果')
            query_update = 'UPDATE testcase_reporter SET browserType=\'%s\', runTime=\'%s\', runResult=\'%s\' WHERE runHistoryId=\'%s\' AND testcaseId=\'%s\''
            query_data = (self.browser_type, run_time, testcase_run_result, self.run_history_id, self.test_case_id)
            result = self.db.execute_update(query_update, query_data)
            if result[1] != True:
                logger.error('更新用例运行结果到测试用例运行报表失败:%s' % result[0])
                return
        else: #新增记录
            logger.info('测试步骤执行完毕，正在记录用例运行结果到测试用例运行报表')
            query_insert = 'INSERT INTO testcase_reporter' + '(runHistoryId, browserType, testcaseId, testplanId, runTime, runResult) ' \
                               'VALUES(%s, %s, %s, %s, %s, %s)'
            query_value = (self.run_history_id, self.browser_type, self.test_case_id, self.test_plan_id, run_time, testcase_run_result)
            restult = self.db.execute_insert(query_insert, query_value)
            if restult[1] != True:
                logger.error('记录用例运行结果到测试用例运行报表失败:%s' % restult[0])
                return

    def get_test_case_steps(self):
        '''获取测试用例步骤'''

        logger.info('正在获取测试用例所有测试步骤')
        # 先获取只包含页面元素操作的普通步骤，接着获取只包含组件的步骤，然后获取只含命令、函数的步骤，最后union all三者，按步骤升序排序
        query_select = "(SELECT a.StepOrder AS StepOrder," \
                       "c.PageName AS PageName," \
                       "b.ElementName AS ElementName," \
                       "b.ElementSelector AS ElementSelector," \
                       "b.ElementSelector02 AS ElementSelector02," \
                       "a.Command AS Command, " \
                       "a.InParas AS InParas," \
                       "a.OutParas AS OutParas," \
                       "a.compid AS compid," \
                       "a.compFolderid AS comFolderid," \
                       "'' AS comName" \
                       " FROM testcases_steps AS a, page_elements AS b,pagesobject AS c " \
                       "WHERE a.TestcaseID = %s AND a.ElementId = b.Id AND b.PageId = c.Id)" \
                       "UNION ALL" \
                       "(SELECT a.steporder AS steporder," \
                       "'' AS PageName," \
                       "'' AS ElementSelector," \
                       "'' AS ElementSelector02," \
                       "'' AS ElementName," \
                       "a.Command AS Command, " \
                       "a.InParas AS InParas," \
                       "a.OutParas AS OutParas," \
                       "a.compid AS compid," \
                       "a.compFolderid AS comFolderid," \
                       "tc.test_name AS comName" \
                       " FROM testcases_steps AS a, testcases AS tc " \
                       "WHERE a.TestcaseID = %s AND a.compid = tc.id)" \
                       "UNION ALL" \
                       "(SELECT a.steporder AS steporder," \
                       "'' AS PageName," \
                       "'' AS ElementSelector," \
                       "'' AS ElementSelector02," \
                       "'' AS ElementName," \
                       "a.Command AS Command, " \
                       "a.InParas AS InParas," \
                       "a.OutParas AS OutParas," \
                       "'' AS compid," \
                       "'' AS comFolderid," \
                       "'' AS comName" \
                       " FROM testcases_steps AS a " \
                       "WHERE a.TestcaseID = %s " \
                       "AND NOT ISNULL(a.stepOrder)" \
                       "AND NOT ISNULL(a.Command) " \
                       "AND ISNULL(compid) " \
                       "AND ElementId='')" \
                       "ORDER BY steporder"

        query_value = (self.test_case_id, self.test_case_id, self.test_case_id)
        result = self.db.select_many_record(query_select, query_value)
        if result[1] == True and result[0]:
            test_case_steps = result[0]
            logger.info('获取的测试步骤为： %s' % test_case_steps)
        else:
            logger.warn('获取的测试步骤出错 %s' % result[0])
            test_case_steps = []
        return test_case_steps


