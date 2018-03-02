#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    : 2018/2/8 9:04
# @Author  : mike.liu
# @File    : htmlreporter.py
import os


from publicpkg.mylogger import logger
from publicpkg.pyh import *


class HtmlReport:
    def __init__(self,title, head):
        self.title = title                    # 网页标签名称
        self.head = head                      # 标题
        self.filename = ''                    # 结果文件名
        self.dir =  './testreport/'           # 结果文件目录
        self.time_took = '00:00:00'           # 测试耗时
        self.success_num = 0                  # 测试通过的用例数
        self.fail_num = 0                     # 测试失败的用例数
        self.error_num = 0                    # 运行出错的用例数
        self.block_num = 0                    # 未运行的测试用例总数
        self.case_total = 0                   # 运行测试用例总数

    # 生成HTML报告
    def generate_html(self, file, run_history_info_list, report_id, db, run_mode):
        page = PyH(self.title)
        page << h1(self.head, align='center')  # 标题居中
        for run_history_info in run_history_info_list:
            run_history_id = run_history_info[0]
            browser_type = run_history_info[1]
            time_took = str(run_history_info[2])
            if run_mode != '运行用例':     #运行计划，计划中失败的用例
                logger.info('正在查询测试计划执行统计信息（执行总数，成功数，失败数，被阻塞数）')
                query = 'SELECT runTc_total, runPassedTc_total, runFailedTc_total, runBlockedTc_total, testPlanName, testPlanId FROM testplan_reporter WHERE runHistoryId = %s'
                data = (run_history_id,)
                result = db.select_one_record(query, data)
                if result[1] != True or not result[0]:
                    logger.warn('没查询到记录')
                    self.case_total = 0
                    self.success_num = 0
                    self.fail_num = 0
                    self.block_num = 0
                    testplan_name = '无计划'
                    testplan_id = 0
                else:
                    self.case_total = result[0][0]
                    self.success_num = result[0][1]
                    self.fail_num = result[0][2]
                    self.block_num = result[0][3]
                    testplan_name = result[0][4]
                    testplan_id = result[0][5]
            else:
                logger.info('正在查询测试用例执行统计信息')
                query = 'SELECT runResult FROM testcase_reporter WHERE runHistoryId = %s'
                data = (run_history_id, )
                result = db.select_one_record(query, data)
                if result[1] != True or not result[0]:
                    logger.warn('没有查询到记录')
                    self.case_total = 0
                    self.success_num = 0
                    self.fail_num = 0
                    self.block_num = 0
                else:
                    self.case_total = 1
                    self.success_num = 0
                    self.fail_num = 0
                    self.block_num = 0
                    case_run_result = result[0][0]
                    if case_run_result == 'Pass':
                        self.success_num = 1
                    elif case_run_result == 'Fail':
                        self.fail_num = 1
                    elif case_run_result == 'Block':
                        self.block_num = 1
                testplan_name = '无计划'
                testplan_id = 0

            if self.fail_num != 0:
                self.fail_num = '<font color="red">'+ str(self.fail_num) + '</font>'

            if self.block_num != 0:
                self.block_num = '<font color="red">' + str(self.block_num) + '</font>'

            page << p('<br/>####################################################【 '+ browser_type +'浏览器:计划执行摘要 】####################################################<br/>')
            page << p('测试总耗时：' + time_took)
            page << p('<br/>计划名称：' + testplan_name)
            page << p('用例执行统计：执行用例总数：' + str(self.case_total) + '&nbsp'*10 + '成功用例数(Pass)：' + str(self.success_num) +\
                          '&nbsp'*10 + '失败用例数(Fail)：' + str(self.fail_num) + '&nbsp'*10 + \
                          '&nbsp'*10 +  '未执行用例数(Block)：' + str(self.block_num))

        for run_history_info in run_history_info_list:
            run_history_id = run_history_info[0]
            browser_type = run_history_info[1]
            page << p('<br/>####################################################【 '+ browser_type +'浏览器:用例执行摘要 】####################################################<br/>')
            #  表格标题caption 表格边框border 单元格边缘与其内容之间的空白cellpadding 单元格之间间隔为cellspacing
            tab = table(border='1', cellpadding='1', cellspacing='0', cl='table')
            tab1 = page << tab
            tab1 << tr(td('ID', bgcolor='#ABABAB', align='center')
                       + td('执行编号', bgcolor='#ABABAB', align='center')
                       + td('用例ID', bgcolor='#ABABAB', align='center')
                       + td('用例名称', bgcolor='#ABABAB', align='center')
                       + td('所属计划', bgcolor='#ABABAB', align='center')
                       + td('计划ID', bgcolor='#ABABAB', align='center')
                       + td('运行浏览器', bgcolor='#ABABAB', align='center')
                       + td('运行结果', bgcolor='#ABABAB', align='center')
                       + td('运行时间', bgcolor='#ABABAB', align='center')
                       + td('操作', bgcolor='#ABABAB', align='center'))

            logger.info('正在查询测试计划：%s 运行的的测试用例' % testplan_name)
            query = 'SELECT id, runHistoryId, testcaseId, testplanId, browserType, runResult, runTime FROM testcase_reporter WHERE testplanId=%s AND runHistoryId = %s ORDER BY id ASC'
            data = (testplan_id, run_history_id)
            result = db.select_many_record(query, data)
            if result[1] != True or not result[0]:
                logger.warn('未查询到用例')
                continue

            testcases = result[0]

            logger.info('正在记录测试计划[名称：%s]的测试用例运行结果到测试报告' % testplan_name)
            testcase_id_name_dic = {}   # 记录测试用例id-名称键值对
            for row in testcases:
                #查询测试用例名称
                query = 'SELECT test_name FROM testcases WHERE id=%s'
                data = (row[2], )
                query_result = db.select_one_record(query, data)
                if query_result[1] != True or not query_result[0]:
                    logger.warn('未查询到测试用例')
                    testcase_name = ''
                else:
                    testcase_name = query_result[0][0]
                    key = str(row[2])
                    testcase_id_name_dic[key] = testcase_name

                if row[5] != 'Pass':
                    td5 = td(row[5], align='center', bgcolor = 'red')
                else:
                    td5 = td(row[5], align='center')

                tab1 << tr(td(str(row[0]), align='center') + td(str(row[1]), align='center')  + td(str(row[2]), align='center') +
                               td(testcase_name, align='center') + td(testplan_name, align='center') +
                               td(str(row[3]), align='center') + td(row[4],align='center') + td5 + td(row[6], align='center') +
                               td('<a name=\"first' + str(row[0]) +'\" href=\"#second' + str(row[0]) + '\">点击查看详情</a>'))

        for run_history_info in run_history_info_list:
            run_history_id = run_history_info[0]
            browser_type = run_history_info[1]
            page << p('<br/>####################################################【 '+ browser_type +'浏览器:用例执行明细 】####################################################<br/>')

            logger.info('正在查询测试计划：%s 运行的的测试用例' % testplan_name)
            query = 'SELECT id, runHistoryId, testcaseId, testplanId, browserType, runResult, runTime  FROM testcase_reporter WHERE testplanId=%s AND runHistoryId = %s ORDER BY id ASC'
            data = (testplan_id, run_history_id)
            result = db.select_many_record(query, data)
            if result[1] != True or not result[0]:
                logger.warn('未查询到测试用例')
                continue

            testcases = result[0]
            for row in testcases:
                #获取测试用例名称
                testcase_name = testcase_id_name_dic[str(row[2])]

                query = ('SELECT id, stepOrder, runHistoryId, elementName, command, inparams, stepRunResult, expectedResult, stepRunResultDesc, browserType, runTime, screenshotUrl FROM case_step_run_detail' + \
                         ' WHERE testcaseId=%s AND runHistoryId = %s '\
                         ' ORDER BY id ASC')
                data = (str(row[2]), run_history_id)
                logger.info('正在查询测试用例[id=%s, name=%s]对应的测试步骤执行明细' % (row[2], testcase_name))
                result = db.select_many_record(query, data)
                if result[1] != True or not result[0]:
                    logger.warn('未查询到所属测试用例[id=%s]的执行步骤' % str(row[2]))

                page << p('>>>测试用例【testcaseID：' + str(row[2]) + ' 名称：' + testcase_name + '】    <a name=\"second'+ str(row[0]) + '\"' + \
                                  'href=\"#first' + str(row[0]) +'\"> 点击返回</a>')
                tab = table(border='1', cellpadding='1', cellspacing='0', cl='table')
                tab2 = page << tab
                tab2 << tr(td('ID', bgcolor='#ABABAB', align='center')
                           + td('步序', bgcolor='#ABABAB', align='center')
                           + td('执行编号', bgcolor='#ABABAB', align='center')
                           + td('所属用例', bgcolor='#ABABAB', align='center')
                           + td('元素名称', bgcolor='#ABABAB', align='center')
                           + td('操作', bgcolor='#ABABAB', align='center')
                           + td('输入参数', bgcolor='#ABABAB', align='center')
                           + td('运行结果', bgcolor='#ABABAB', align='center')
                           + td('预期结果', bgcolor='#ABABAB', align='center')
                           + td('结果描述', bgcolor='#ABABAB', align='center')
                           + td('运行浏览器', bgcolor='#ABABAB', align='center')
                           + td('运行时间', bgcolor='#ABABAB', align='center')
                           + td('操作', bgcolor='#ABABAB', align='center'))
                for step_row in result[0]: # 遍历测试用例的测试步骤执行结果
                    testcase_name = testcase_id_name_dic[str(row[2])]

                    if step_row[6] != 'Pass':
                        td6 = td(step_row[6], align='center', bgcolor='red')
                    else:
                        td6 = td(step_row[6], align='center')

                    if step_row[11] != '' and step_row[11].find('.') != -1 : # 存在截图
                        td11 = td('<a href=\"' + step_row[11] + '\" tagert=\"_blank\">查看截图</a>')
                    else:
                        td11 = td('')

                    tab2 << tr(td(str(step_row[0]), align='center') + td(step_row[1], align='center') + td(str(step_row[2]), align='center') +
                               td(testcase_name, align='center') + td(step_row[3], align='center') +  td(step_row[4], align='center') + td(step_row[5], align='left') +
                               td6 + td(step_row[7], align='left') + td(step_row[8], align='left') + td(step_row[9], align='center') + td(step_row[10], align='center') +
                               td11)


        page << p('<br/>')

        logger.info('正在设置测试报告结果文件名')
        self.__set_result_filename(file, report_id)

        logger.info('正在生产测试报告')
        page.printOut(self.filename)
        return True

    #设置结果文件名
    def __set_result_filename(self, filename, report_id):
        parent_path, ext = os.path.splitext(filename)
        self.filename = self.dir + parent_path + str(report_id) + ext
        logger.info('测试报告文件名所在路径为：%s' % self.filename)

    # 创建报告保存目录
    def mkdir_of_report(self, path, other_tools):
        other_tools.mkdirs_once_many(path)
        self.dir = path

    def get_filename(self):
        return self.filename

    #统计运行耗时
    def set_time_took(self, time):
        self.time_took = time
        return self.time_took

