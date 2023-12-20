import sys
import threading

import requests
import re
import time
from datetime import datetime
from lxml import etree

import utils
from config import *

# 递归遍历深度遍历列表
def deep_iter(ndim_list):
    ret = []
    def inner_func(n_list):
        for i in n_list:
            if type(i) != list:
                ret.append(i)
            else:
                inner_func(i)
    return ret

class User:
    def __init__(self, username, password, mail_config):
        self.ss = self.login(username, password)
        print("【登录成功!】")
        self.mail_config = mail_config

    @staticmethod
    def login(username, password) -> requests.Session:
        while True:
            try:
                ss = utils.login(username, password)
                return ss
            except ValueError as msg:
                print(f'【{datetime.now()}】')
                print(msg)
            except Exception as e:
                print(f'*******************\n意外报错： {datetime.now()}\n', e)
                sys.exit()

    def send(self, subject, text):
        utils.send(self.mail_config, subject, text)

    # 选课相关方法
    def query_by_course_code(self, code: str) -> list:
        """
        按课程代码查询可选课程，返回可选课程的相关信息
        会去除掉不可选的
        """
        query_url = 'http://jwc.swjtu.edu.cn/vatuu/CourseStudentAction'
        data = {
            'setAction': 'studentCourseSysSchedule',
            'viewType': '',
            'jumpPage': 1,
            'selectAction': 'CourseCode',
            'key1': code,
            'courseType': 'all',
            'key4': '',
            'btn': '执行查询'
        }
        res = self.ss.post(url=query_url, data=data)
        # res.encoding = res.apparent_encoding
        html = etree.HTML(res.text)
        data = html.xpath('//*[@id="table3"]/tr')[1:-1]
        ret = []
        for item in data:
            dic = {
                'teacher': item.xpath('td[9]/a/span/text()')[0].strip(),
                'course': item.xpath('td[4]/a/span/text()')[0].strip(),
                'course_code': item.xpath('td[3]/a/span/text()')[0].strip(),
                'date': item.xpath('td[11]/text()')[0].strip(),
                'selected': item.xpath('td[13]/text()')[0].strip(),  # 如果满了就是''
                'teachId': item.xpath('td[2]/span/text()')[0].strip()  # 选课参数
            }
            ret.append(dic)
        return ret

    def select_course(self, teachId):
        """选课操作"""
        url = f'http://jwc.swjtu.edu.cn/vatuu/CourseStudentAction?setAction=addStudentCourseApply&teachId={teachId}&isBook=1&tt={int(time.time() * 1000)}'
        res = self.ss.get(url=url)
        # res.encoding = res.apparent_encoding
        msg = re.findall('<message>(.*?)</message>', res.text)[0]
        return msg

    def del_course(self, listId, chooseId):
        """
        :param listId: 删除操作那里的一串代码，如482D023D00CC1DF068A414800A650C97
        :param chooseId: 选课编号，如B2639
        :return:
        """
        url = f'http://jwc.swjtu.edu.cn/vatuu/CourseStudentAction?setAction=delStudentCourseList&listId={listId}&teachId={chooseId}&tt={int(time.time() * 1000)}'
        res = self.ss.get(url=url)
        # res.encoding = res.apparent_encoding
        return res.text

    # 根据选课编号定位待选课程提取到teachId，以及要删除选课的teachId和代码

    def select_course_by_chooseId(self, chooseId):
        # 先查询选课编号，找到teachId
        url = 'http://jwc.swjtu.edu.cn/vatuu/CourseStudentAction'
        data = {
            'setAction': 'studentCourseSysSchedule',
            'viewType': '',
            'jumpPage': 1,
            'selectAction': 'TeachID',
            'key1': chooseId,
            'courseType': 'all',
            'key4': '',
            'btn': '执行查询'
        }
        res = self.ss.post(url=url, data=data)
        # res.encoding = res.apparent_encoding
        html = etree.HTML(res.text)
        teachId = html.xpath('//*[@id="table3"]/tr[2]/td[2]/span/text()')[0].strip()
        return self.select_course(teachId)

    # print(select_course_by_chooseId('B1532'))

    def del_course_by_chooseId(self, chooseId):
        url = 'http://jwc.swjtu.edu.cn/vatuu/CourseStudentAction?setAction=studentCourseSysList&viewType=delCourse'
        res = self.ss.get(url)
        html = etree.HTML(res.text)
        elements = html.xpath('//*[@id="table3"]/tr')[1:-1]
        for element in elements:
            # print(element.xpath('td[3]/text()')[0].strip())
            if element.xpath('td[3]/text()')[0].strip() == chooseId:
                break
        listId = element.xpath('td[12]/input/@onclick')[0].strip().split(',')[-2].strip('\'"')
        # print(listId)
        self.del_course(chooseId=chooseId, listId=listId)

    def run_select_course(self, chooseId):
        while True:
            try:
                msg = self.select_course_by_chooseId(chooseId)
                print(f"course {chooseId}: ", end='')
                print(msg)
                if '选课成功' in msg:
                    break
                elif '已选' in msg:
                    break
                elif '冲突' in msg:
                    break
                elif '选课申请成功' in msg:
                    break
            except Exception as e:
                # self.send('全部成绩查询报错', str(e))
                print(f'\nerror: {datetime.now()}】\n', e)
            time.sleep(1)

    def run_select_course_with_teachId(self, teachId, course):
        """
        在第一次选课的时候准备好要选的课的teachId，这样就不用查询了，直接发起选课请求
        注意这个teachId是在<span id="teachIdChooseB2492" style="display:none;">FD4B92598D7377F6</span>这样的里面
        :param teachId:字符串，形如FD4B92598D7377F6
        :return:
        """
        while True:
            try:
                msg = self.select_course(teachId)
                print(f"course {course}: ", end='')
                print(msg)
                if '选课成功' in msg:
                    break
                elif '已选' in msg:
                    break
                elif '冲突' in msg:
                    break
                elif '选课申请成功' in msg:
                    break
            except Exception as e:
                # self.send('全部成绩查询报错', str(e))
                print(f'\n{course} error: {datetime.now()}】\n', e)
            time.sleep(1)


if __name__ == '__main__':
    # USAGE！！！先删除必要的课程，自行确定好要选的课程，收集teachId，然后选课
    user = User(username, password, config)

    # TODO：为了便捷和避免意外因素，可以考虑用cookie登录，临近选课时开冲


    # delete course by chooseId(课程编号，如B2492)
    delete_courses = ['B2498']  # 要删除的课程的课程编号
    for i in delete_courses:
        user.del_course_by_chooseId(i)  # 没有加异常处理，如有需要，请自行添加或选择手动删除课程

    #! 一下为使用teachId不经过查询直接选课
    # # 待选课程teachId，可以自己标注一下teachId代表的是什么课，便于多个选课返回结果时查看
    # li = [
    #     ('D91B30359ED1D4D9', "操作系统"),
    # ]
    # threads = []
    # for teachId, course in li:
    #     t = threading.Thread(target=user.run_select_course_with_teachId, args=(teachId, course))
    #     threads.append(t)

    # ! 以下为使用chooseId(选课编号)经过查询teachId选课
    li = ['B2498', 'B2489', 'B2542', 'B3447', 'B1323', 'B2564', 'B2557', 'B2545', 'B2547', 'B2506', 'B2510', 'B2265', 'B1519']
    threads = []
    for teachId in li:
        t = threading.Thread(target=user.run_select_course, args=(teachId,))
        threads.append(t)

    # 启动线程
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # # 查询某个课程代码
    # result = user.query_by_course_code('SoFL003911')
    # for i in result:
    #     print(i)
