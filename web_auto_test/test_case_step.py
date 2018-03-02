#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    : 2018/2/23 14:29
# @Author  : mike.liu
# @File    : test_case_step.py
import time
import os

from publicpkg.globalvar import other_tools
from publicpkg.globalvar import selenium_util
from publicpkg.globalvar import screenshot_dir_path
from publicpkg.globalvar import remote_screenshot_baselink
from publicpkg.mylogger import  logger

class TestCaseStep:
    def __init__(self, test_case_id, test_plan_id):
        self.test_case_id = test_case_id
        self.test_plan_id = test_plan_id

    def run_tc_step(self, browser_type, db, test_case_step, testcase_run_history_id, runmode):
        run_time = '%d-%02d-%02d %d:%d:%d' % time.localtime()[0 : 6]
        element_name = test_case_step[2]     # 元素名称
        command = test_case_step[5]          # 操作
        step_order = test_case_step[0]       # 步序
        inparams = test_case_step[6]         # 输入参数
        expected_result = test_case_step[7]     # 预期结果
        logger.info('步骤信息（元素名称：%s, 步序：%s, 操作：%s， 输入参数：%s，预期结果：%s）' % (element_name, step_order, command, inparams, expected_result))

        if (not element_name) and command:  # 执行的步骤为函数操作
            logger.info('正在执行函数操作')
            result = self.run_function_in_step(command, inparams, expected_result)
            if result[0] == 'Fail': # 运行出错，截图
                step_screenshot_name = self.get_screenshot_as_file(step_order, testcase_run_history_id) #截图
                step_screenshot_name = os.path.basename(step_screenshot_name)
            else:
                step_screenshot_name = ''
        else:
            logger.info('正在执行最普通的元素操作')
            # 获取元素选择器
            selector1 = test_case_step[3]
            selector2 = test_case_step[4]
            logger.info('正在对选择器：selector1: %s，selector2: %s 做数据转换处理' % (selector1, selector2))
            selector1 = other_tools.conver_data_from_phppage(selector1)
            selector2 = other_tools.conver_data_from_phppage(selector2)
            logger.info('转换后的选择器：selector1: %s，selector2: %s' % (selector1, selector2))

            logger.info('开始对步骤中的元素操作进行操作')
            result = self.exectue_element_operator_in_step(selector1, selector2, command, inparams, expected_result)

            if result[0] == 'Fail': # 运行出错，截图
                step_screenshot_name = self.get_screenshot_as_file(step_order, testcase_run_history_id) #截图
                step_screenshot_name = os.path.basename(step_screenshot_name)
            else:
                step_screenshot_name = ''

        step_run_result = result[0]      # 运行结果
        step_run_result_desc = result[1] # 运行结果描述
        if step_screenshot_name:
            step_screenshot_url = remote_screenshot_baselink.rstrip('/') + '/' + step_screenshot_name
        else:
            step_screenshot_url = ''

        if '运行流水' == runmode:
            logger.info('正在更新测试步骤结果报表中的测试步骤运行结果')
            query_update = 'UPDATE case_step_run_detail SET elementName=\'%s\', command=\'%s\', inparams=\'%s\', expectedResult=\'%s\', stepRunResult=\'%s\', stepRunResultDesc=\'%s\', '\
                           'browserType=\'%s\', runTime=\'%s\', screenshotUrl=\'%s\'  WHERE runHistoryId=\'%s\' AND testcaseId=\'%s\' AND stepOrder=\'%s\' AND browserType=\'%s\''
            query_data = (element_name, command, inparams, expected_result, step_run_result, step_run_result_desc, browser_type, run_time, step_screenshot_url, testcase_run_history_id, self.test_case_id, step_order, browser_type)
            result = db.execute_update(query_update, query_data)
            if result[1] != True:
                logger.error('更新用例运行结果到测试用例运行报表失败:%s' % result[0])
                return
        else:
            logger.info('正在记录测试步骤运行结果到测试步骤结果报表')
            query_insert = 'INSERT INTO case_step_run_detail' + '(testplanId, testcaseId, runHistoryId, stepOrder, ' \
                           'elementName, command, inparams, expectedResult, stepRunResult, stepRunResultDesc, browserType, runTime, screenshotUrl) ' \
                           'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            query_value = (self.test_plan_id,self.test_case_id, testcase_run_history_id, step_order, element_name, command, inparams, expected_result, step_run_result, step_run_result_desc, browser_type, run_time, step_screenshot_url)
            result = db.execute_insert(query_insert, query_value)

            if result[1] != True:
                logger.error('记录到测试步骤结果报表失败 %s' % result[0])

            logger.info('返回步骤运行结果给测试用例')
        return step_run_result

    # 执行测试用例步骤中的函数操作
    def run_function_in_step(self, command, inparameters, outputparams):
        logger.info('执行函数：%s' % command)

        if inparameters: # 有输入参数
            logger.info('正在对输入参数:%s 进行参数处理' % inparameters)
            inparameters = other_tools.conver_data_from_phppage(inparameters)

            inparameters = inparameters.split('||')  # 输入参数之间以||分隔

        command = command.lower()
        if command == '切换frame':
            result = selenium_util.switch_to_frame(inparameters[0])
            return  result
        elif command == '等待':
            second = int(inparameters[0])
            logger.info('等待%s秒'% second)
            result = selenium_util.sleep(second)
            return result
        elif command == '智能等待':
            second = int(inparameters[0])
            logger.info('等待%s秒'% second)
            result = selenium_util.implicitly_wait(second)
            return result
        elif command == '断言':
            assertString = inparameters[0]
            logger.info('断言的标题为:%s' % assertString)
            result = selenium_util.assert_string_in_pagesource(assertString)
            return result
            logger.info('result:%s' % result)


    # 执行元素操作
    def exectue_element_operator_in_step(self, selector1, selector2, command, inparameters, expected_result):
        logger.info('操作：%s' % command)
        if inparameters: # 有输入参数
            logger.info('正在对输入参数:%s 进行参数处理' % inparameters)
            inparameters = other_tools.conver_data_from_phppage(inparameters)

            inparameters = inparameters.split('||')
            logger.info('处理后的输入参数为:%s ' % inparameters)

        command = command.lower()
        if command == '查找':
            try:
                element = self.find_element(selector1, selector2)
                if element:
                    return ('Pass', '找到元素')
                else:
                    return ('Fail', '未找到元素')
            except Exception as e:
                logger.error('查找元素出错')
                return ('Fail', e)
        elif command == '输入':
            try:
                element = self.find_element(selector1, selector2)
                if type(inparameters) == type([]) and inparameters[0] and element:
                    element.send_keys(inparameters[0])
                    return ('Pass', '输入数据成功')
                else:
                    return ('Fail', '输入数据失败')
            except Exception as e:
                logger.error('执行输入操作出错:%s' % e)
                return ('Fail', e)
        elif command == '清空':
            try:
                element = self.find_element(selector1, selector2)
                if element:
                    element.clear()
                    return ('Pass', '清空数据成功')
                else:
                    return ('Fail', '清空数据失败')
            except Exception as e:
                logger.error('执行输入操作出错:%s' % e)
                return ('Fail', e)
        elif command == '点击':
            try:
                element = self.find_element(selector1, selector2)
                if element:
                    element.click()
                    return ('Pass', '点击成功')
                else:
                    return ('Fail', '点击操作失败')
            except Exception as e:
                logger.error('执行点击操作出错:%s' % e)
                return ('Fail', e)
        else:
            logger.error('command为空,或者填写错误')
            return ('Fail', 'comman为空或者填写错误')

    # 查找元素
    def find_element(self,selector1,selector2):
        # 优先使用selector1查找
        element = self.find_element_by_locator_adapter(selector1)
        if element: #如果找到了
            logger.info('找到元素：%s' % element)
            return element
        else:
            logger.info('利用selector1选择器未找到元素，开始用选择器:%s 查找' % selector2)
            element = self.find_element_by_locator_adapter(selector2)
            if element: #如果找到了
                logger.info('找到元素：%s' % element)
                return element
            else:
                logger.warn('未找到元素')
                return None

    # 根据元素定位器的不同，自动选择适配的定位器，查找元素
    def find_element_by_locator_adapter(self,selector):
        logger.info('开始根据元素定位器：%s 自定位元素' % selector)
        if not selector:
            logger.warn('无法通过非法选择器：%s定位元素' % selector)
            return None

        try:
            if (selector[:3]).lower() == 'id=':
                selector = selector[3:]
                logger.info('find_element_by_id：%s' % selector)
                element =  selenium_util.find_element_by_id(selector)
                return element
            elif (selector[:6]).lower() == 'xpath=':
                selector = selector[6:]
                logger.info('find_element_by_xpath：%s' % selector)
                element =  selenium_util.find_element_by_xpath(selector)
                return element
            elif (selector[:5]).lower() == 'name=':
                selector = selector[5:]
                logger.info('find_element_by_name：%s' % selector)
                element =  selenium_util.find_element_by_name(selector)
                return element
            elif (selector[:5]).lower() == 'link=':
                selector = selector[5:]
                logger.info('find_element_by_link_text：%s' % selector)
                element =  selenium_util.find_element_by_link_text(selector)
                return element
            elif (selector[:10]).lower() == 'link_text=':
                selector = selector[10:]
                logger.info('find_element_by_link_text：%s' % selector)
                element = selenium_util.find_element_by_link_text(selector)
                return element
            elif (selector[:4]).lower() == 'css=':
                selector = selector[4:]
                logger.info('find_element_by_css_selector：%s' % selector)
                element =  selenium_util.find_element_by_css_selector(selector)
                return  element
            elif (selector[:9]).lower() == 'tag_name=':
                selector = selector[9:]
                logger.info('find_element_by_tag_name：%s' % selector)
                element = selenium_util.find_element_by_tag_name(selector)
                return element
            elif (selector[:11]).lower() == 'class_name=':
                selector = selector[11:]
                logger.info('find_element_by_class_name：%s' % selector)
                element = selenium_util.find_element_by_class_name(selector)
                return element
            elif (selector[:17]).lower() == 'partial_link_text=':
                selector = selector[:17]
                logger.info('find_element_by_partial_link_text：%s' % selector)
                element = selenium_util.find_element_by_partial_link_text(selector)
                return element
            else:
                logger.info('error, 非法选择器：%s:' % selector)
                return None
        except Exception as e:
            logger.error('定位元素出错，%s' % e)
            return None

    # 步骤截图
    def get_screenshot_as_file(self, step_order, testcase_run_history_id):
        curr_time = time.strftime('%Y%m%d%H%M%S', time.localtime()) # 截图时间

        sub_path = 'tp' + str(self.test_plan_id)
        image_name =  sub_path + '_tc' + str(self.test_case_id) + '_step' + str(step_order) + '_' + str(testcase_run_history_id)  + '_' + str(curr_time)
        base_path = screenshot_dir_path + sub_path + '\\tc' + str(self.test_case_id) + '\\'
        if not os.path.isdir(base_path):
            other_tools.mkdirs_once_many(base_path)
        screenshot_pic_path = base_path + image_name + '.png'
        result = selenium_util.get_screenshot_as_file(screenshot_pic_path)
        if result[0] == 'Pass':
            logger.info('截图文件保存路径为：%s' % screenshot_pic_path)
            return  screenshot_pic_path
        else:
            logger.error('截图失败:%s' % result[0])
            return ''






