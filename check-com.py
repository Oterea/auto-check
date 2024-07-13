import sys

import requests
import json
import time
from datetime import datetime
import logging as logger
import traceback

# 202.195.224.61
# nxdyjs.nuist.edu.cn
logger.basicConfig(
        filename = 'app.log',
        level = logger.INFO,
        format = '%(asctime)s [%(process)d] [%(levelname)s] - %(message)s',
        datefmt = '%Y年%m月%d日 %H:%M'
        )
# sid = 'ktcoyrmko5pp1jmdlmdortqj'
sid = sys.argv[1]
print(sid)
cookies = {
    '__SINDEXCOOKIE__': 'c2e502fe7bc457b6934d28c4e13d25bf',
    'ASP.NET_SessionId': sid
    }
# 定义要监测的网页URL
# url = 'https://nxdyjs.nuist.edu.cn/gmis5/student/yggl/kwhdbm'
url = 'https://nxdyjs.nuist.edu.cn/gmis5/student/yggl/kwhdbm_list'
bm_url = 'https://nxdyjs.nuist.edu.cn/gmis5/student/yggl/kwhdbm_bm'
qd_url = 'https://nxdyjs.nuist.edu.cn/gmis5/kwhd/hdxxfb_qd?hdid='
qc_url = 'https://nxdyjs.nuist.edu.cn/gmis5/kwhd/hdxxfb_qc?hdid='
# 已经申请的活动列表
selected_url = 'https://nxdyjs.nuist.edu.cn/gmis5/student/yggl/kwhdbm_sqlist'
qmsg_base_url = 'https://qmsg.zendee.cn/send/'
qmsg_key = '5f11aacce283c0baafef2731366248b2'
qmsg_post_url = qmsg_base_url + qmsg_key + '?msg='
xia_post_url = 'https://wx.xtuis.cn/FtHcOPZd3ZiciV2pUgqcsMIlG.send'
# xia_key = 'FtHcOPZd3ZiciV2pUgqcsMIlG'
time_format = '%Y-%m-%d %H:%M'

# 初始化活动数量
last_act_num = 0
# 循环次数
loop_num = 0
# 间隔时间/小时
post_time_offset = 4
# 周期24小时
clock = 24

# 新的打印周期 从小到大
post_message_hour_list = [8,20,21,22]
post_message_hour_dir = {}
for hour in post_message_hour_list:
    post_message_hour_dir[hour] = False

# 开始时间
program_start_time = datetime.now()
# 程序开始推送消息

start_hour = program_start_time.hour
begin_message_hour_dir = {start_hour: False}


def new_post_content(act_list):
    temp_dir = act_list[-1]
    name = str(temp_dir["hdmc"])
    act_time = str(temp_dir["hdsj"])
    act_location = str(temp_dir["hddd"])
    act_bm_begin_time = str(temp_dir["sqkssj"])
    act_num_limit = str(temp_dir["xzrs"])
    act_num = str(temp_dir["bmrs"])
    act_id = temp_dir["id"]
    post_content = (f'<b>活动ID:</b> {act_id}\n'
                    f'<b>活动名称:</b> {name}\n'
                    f'<b>活动时间:</b> {act_time}\n'
                    f'<b>活动地点:</b> {act_location}\n'
                    f'<b>限制人数:</b> {act_num_limit} 人\n'
                    f'<b>已报名人数:</b> {act_num} 人\n'
                    f'<b>报名开始时间:</b> {act_bm_begin_time}\n'
                    )
    return post_content


def get_time_elapse(current_datetime, program_start_time):
    time_elapsed = current_datetime - program_start_time
    total_seconds = time_elapsed.total_seconds()
    days, remainder = divmod(total_seconds, 86400)  # 86400 秒是一天
    hours, remainder = divmod(remainder, 3600)  # 3600 秒是一小时
    minutes, seconds = divmod(remainder, 60)
    time_elapsed_formatted_p = f"{int(days)}天 {int(hours)}小时 {int(minutes)}分钟 {int(seconds)}秒"
    return time_elapsed_formatted_p


class LoginException(Exception):
    def __init__(self, value):
        self.value = value


while True:
    # 重置变量
    response = None
    sys_msg = ''
    error_msg = ''
    exception_flag = False
    # 执行次数
    loop_num += 1

    # 发送GET请求获取页面内容
    try:
        response = requests.session().get(url, cookies = cookies)
        response.keep_alive = False
        response.raise_for_status()  # 检查响应状态
    except requests.exceptions.RequestException:
        sys_msg = traceback.format_exc()
        error_msg = f'服务器断网-{sys_msg}'
        logger.critical(error_msg)
        post_content = (f'<b>异常内容:</b> {error_msg}\n'
                        f'<b>发生时间:</b> {program_start_time.strftime(time_format)}\n'
                        f'<b>执行次数:</b> {loop_num} 次\n')
        xia_post_data = {
            'text': '服务器断网',
            'desp': post_content
            }
        requests.get(xia_post_url, xia_post_data)
        # 服务器断网，结束请求
        break
    try:
        if '登录' in response.text:
            logger.critical('登录失败')
            raise LoginException('SINDEXCOOKIE或者SessionId过期')
        else:
            logger.info("登录成功")
            act_row_string = response.text
            act_row_json = json.loads(act_row_string)
            act_list = act_row_json['rows']  # act_list是一个包含一个字典的列表，你可以访问其中的数据

            if len(act_list) > last_act_num:
                logger.info('有新活动啦！！！')
                temp_dir = act_list[-1]
                act_id = str(temp_dir["id"])

                # 活动报名
                bm_response = requests.session().post(bm_url, data = {'id': act_id}, cookies = cookies)
                # select_dir = json.loads(bm_response.text)
                # zt = int(select_dir['zt'])

                selected_response = requests.session().post(selected_url, cookies = cookies)

                selected_json = json.loads(selected_response.text)
                selected_list = selected_json['rows']
                bm_status = '未报名'
                for selected_dir in selected_list:
                    if selected_dir['hdid'] == act_id:
                        bm_status = '已经报名'
                        break


                # 报名状态推送

                new_act_content = new_post_content(act_list)
                post_content = (f'<b>报名状态:</b> {bm_status}\n'
                                f'{new_act_content}')
                xia_post_data = {
                    'text': '新活动来啦！！！',
                    'desp': post_content
                    }
                requests.post(xia_post_url, data = xia_post_data)


                last_act_num = len(act_list)

            else:
                logger.info("无新活动")

            last_act_num = len(act_list)
    except LoginException:
        sys_msg = traceback.format_exc()
        exception_flag = True
        error_msg = f'登录异常-{sys_msg}'
        logger.critical(error_msg)
    except requests.exceptions.SSLError:
        sys_msg = traceback.format_exc()
        exception_flag = True
        error_msg = f'推送请求异常-{sys_msg}'
        logger.critical(error_msg)
    # except requests.exceptions.RequestException:
    #     sys_msg = traceback.format_exc()
    #     exception_flag = True
    #     error_msg = f'推送请求异常-{sys_msg}'
    #     logger.critical(error_msg)

        # 在这里可以添加处理网络请求异常的代码
    except json.JSONDecodeError:
        sys_msg = traceback.format_exc()
        exception_flag = True
        error_msg = f'JSON解析异常-{sys_msg}'
        logger.critical(error_msg)
    except Exception and requests.exceptions.RequestException:
        sys_msg = traceback.format_exc()
        exception_flag = True
        error_msg = f'未知异常-{sys_msg}'
        logger.critical(error_msg)

    finally:
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime(time_format)
        time_elapsed_formatted = get_time_elapse(current_datetime, program_start_time)
        if exception_flag:
            # 异常信息推送
            post_content = (f'<b>异常内容:</b> {error_msg}\n'
                            f'<b>发生时间:</b> {formatted_datetime}\n'
                            f'<b>执行次数:</b> {loop_num} 次\n')
            xia_post_data = {
                'text': '异常信息',
                'desp': post_content
                }
            requests.get(xia_post_url, data = xia_post_data)
            # break
        else:
            # 正常消息
            post_content = (f"<b>报告时间:</b> {formatted_datetime}\n"
                            f"<b>已运行时间:</b> {time_elapsed_formatted}\n"
                            f"<b>执行时间:</b> {loop_num} 次")
            xia_post_data = {
                'text': '正常报告',
                'desp': post_content
                }
            # 推送消息周期 当前小时在推送列表中 且 未推送过
            current_hour = current_datetime.hour
            if current_hour in begin_message_hour_dir and begin_message_hour_dir[current_hour] is False:
                # 推送消息
                first_xia_post_data = {
                    'text': '程序正常启动',
                    'desp': post_content
                    }
                requests.get(xia_post_url, data = first_xia_post_data)
                begin_message_hour_dir[current_hour] = True

            if current_hour in post_message_hour_list and post_message_hour_dir[current_hour] is False:
                # 推送消息
                requests.get(xia_post_url, data = xia_post_data)
                post_message_hour_dir[current_hour] = True
                # 上一个hour变为False
                index = post_message_hour_list.index(current_hour)
                previous_index = (index - 1) % len(post_message_hour_list)
                last_hour = post_message_hour_list[previous_index]
                post_message_hour_dir[last_hour] = False



    time.sleep(300)  # 5min
