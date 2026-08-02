import os
import re
from functools import partial
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import json
from itertools import islice
import logging
from logging.handlers import TimedRotatingFileHandler
import time
import datetime
import pandas as pd
import random
import webbrowser
import subprocess
subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')


class Log_week():
    def get_logger(self):
        self.logger = logging.getLogger(__name__)
        # 日志格式
        formatter = '[%(asctime)s-%(filename)s][%(funcName)s-%(lineno)d]--%(message)s'
        # 日志级别
        self.logger.setLevel(logging.DEBUG)
        # 控制台日志
        sh = logging.StreamHandler()
        log_formatter = logging.Formatter(formatter, datefmt='%Y-%m-%d %H:%M:%S')
        # info日志文件名
        info_file_name = time.strftime("%Y-%m-%d") + '.log'
        # 将其保存到特定目录
        case_dir = r'./logs/'
        info_handler = TimedRotatingFileHandler(filename=case_dir + info_file_name,
                                                when='MIDNIGHT',
                                                interval=1,
                                                backupCount=7,
                                                encoding='utf-8')
        self.logger.addHandler(sh)
        sh.setFormatter(log_formatter)
        self.logger.addHandler(info_handler)
        info_handler.setFormatter(log_formatter)
        return self.logger


class YouTubeCommentSpider:
    def __init__(self, comment_num, order_type, txt_msglist, logger):
        self.comment_num = comment_num
        self.order_type = order_type
        self.txt_msglist = txt_msglist
        self.logger = logger
        self.describe = []
        self.result_file1 = 'ytb评论_{}.csv'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        self.result_file2 = str(self.result_file1).replace('csv', 'xlsx')

    def tk_show(self, context):
        self.logger.info(context)
        self.txt_msglist.delete('1.0', 'end')
        self.describe.append(context)
        self.txt_msglist.insert('insert', '\n'.join(self.describe))
        self.txt_msglist.see("end")

    def trans_time(self, v_timestamp):
        """10位时间戳转换为时间字符串"""
        v_timestamp = int(str(v_timestamp)[:10])
        timeArray = time.localtime(v_timestamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime

    def spider(self):
        """[专有代码已移除] YouTube评论采集核心逻辑

        原实现流程：
        1. 从《目标视频.xlsx》读取待爬取的视频URL列表
        2. 解析video_id，逐个视频调用 youtube_comment_downloader 库获取评论
        3. 支持按热门/按日期排序，支持限制评论数量（islice）
        4. 每条评论写入json中间文件（./jsons/{video_id}.json）
        5. json转csv：用pandas读取json，删除无用列（photo/heart/reply/paid），转换时间戳
        6. csv追加写入最终文件，最后将csv转换为xlsx
        7. 填充replies空值为0
        """
        # [专有代码已移除] 详细实现约70行，包含：
        #   - pd.read_excel('目标视频.xlsx') 读取视频列表
        #   - islice 控制评论数量
        #   - json/csv/xlsx 格式转换与数据清洗
        self.tk_show('[专有代码已移除] YouTube评论采集功能需要专有实现')


class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
        self.setDaemon(True)
        self.start()  # 在这里开始

    def run(self):
        self.func(*self.args)


def open_sugg():
    webbrowser.open("https://docs.qq.com/sheet/DVGxzT0VVSkVzSW1u?tab=57hu3z", new=0)


def task(comment_num, order_type, txt_msglist):
    cn = comment_num.get()
    ot = order_type.get()
    log = Log_week()
    logger = log.get_logger()
    YouTubeCommentSpider(cn, ot, txt_msglist, logger).spider()


def show_about():
    messagebox.showinfo("关于软件",
                        '\nv3.0: 分期版本发布\nv3.1: 删除paid，防止错列\nv3.2: 修复=开头的video_id\nv3.3: 新增注册入口 & 修复转换时间df[\'time2\']，防止报错invalid literal for int() with base 10: \'nan\' \n\n最新版软件获取：\n公众号"老男孩的平凡之路"后台回复: 爬油管评论')


def show_agreement():
    messagebox.showinfo("使用协议",
                        """欢迎使用本软件！在使用前，请仔细阅读以下使用协议：

授权与许可：本软件仅授权用户用于合法的个人或商业用途。禁止使用本软件进行任何违法活动，包括但不限于未经授权的数据采集、侵犯知识产权和侵犯隐私权等。
责任限制：本软件开发者不对用户因使用本软件而导致的任何直接或间接损失负责。用户在使用过程中应遵守相关法律法规，并自行承担因使用本软件而产生的风险和责任。
数据隐私：本软件不会收集、存储或分享用户的个人数据。用户采集的数据应严格遵守数据保护法律和目标网站的使用政策。
更新与维护：我们有权随时对本软件进行更新和维护，用户应及时下载并安装更新，以确保软件的正常使用。
协议修改：我们保留随时修改本使用协议的权利，修改后的协议将在发布后立即生效。用户继续使用本软件即表示接受新的协议条款。

作为软件使用者，您默认接受以上协议条款。感谢理解与支持。如有疑问，请联系作者。"""
                        )


def create_spider_root():
    global comment_num, order_type
    # 创建日志目录
    work_path = os.getcwd()
    if not os.path.exists(work_path + "/logs"):
        os.makedirs(work_path + "/logs")
    # 创建json文件目录
    if not os.path.exists(work_path + "/jsons"):
        os.makedirs(work_path + "/jsons")
    # 创建主窗口
    root = tk.Tk()
    root.title('爬油管评论软件v3.3 | 马哥python说 | 公众号：老男孩的平凡之路')
    # 设置窗口大小
    root.minsize(width=850, height=650)
    # 左上角图标
    try:
        root.iconbitmap('mage.ico')
    except:
        pass
    # 菜单
    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="关于软件", command=show_about)
    file_menu.add_command(label="使用协议", command=show_agreement)
    if 'open_sugg' in globals():
        file_menu.add_command(label="意见收集", command=open_sugg)
    menu_bar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menu_bar)

    # ========== UI布局区域 ==========
    # 输出项 - 运行日志区域（包含Scrollbar + Text控件）
    # 原实现约15行Tkinter布局代码，此处用pass替代
    pass

    # 输入项 - 参数设置区域（包含：目标视频说明、爬取数量Spinbox、排序方式Combobox）
    # 原实现约20行Tkinter布局代码，此处用pass替代
    pass

    # 执行按钮 & 退出按钮
    # 原实现约5行Tkinter布局代码，此处用pass替代
    pass

    # 免责声明
    claim = tk.Label(root,
                     text='免责声明: 禁止使用该软件从事任何违法活动，否则由此产生的一切法律后果由软件使用者自行承担，与软件开发作者无关！',
                     font=('微软', 10), fg='red')
    claim.place(x=50, y=550)

    # 版权信息
    copyright = tk.Label(root, text='@马哥python说 All rights reserved.', font=('仿宋', 10), fg='grey')
    copyright.place(x=290, y=625)

    # 循环消息
    root.mainloop()


def create_login_root():
    # 创建主窗口
    root_login = tk.Tk()
    root_login.title('爬油管评论软件v3.3')
    # 设置窗口大小
    root_login.minsize(width=400, height=300)
    # 左上角图标
    try:
        root_login.iconbitmap('mage.ico')
    except:
        pass
    # 菜单
    menu_bar = tk.Menu(root_login)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="关于软件", command=show_about)
    file_menu.add_command(label="使用协议", command=show_agreement)
    if 'open_sugg' in globals():
        file_menu.add_command(label="意见收集", command=open_sugg)
    menu_bar.add_cascade(label="File", menu=file_menu)
    root_login.config(menu=menu_bar)
    # 标题标签
    label_title = ttk.Label(root_login, text="用户登录", font=("Helvetica", 20, "bold"), background="#f0f4f7")
    label_title.pack(pady=20)
    # 控件
    # 用户名标签和输入框
    frame_username = ttk.Frame(root_login)
    frame_username.pack(pady=10)
    label_username = ttk.Label(frame_username, text="账号:", font=("Helvetica", 12), width=10)
    label_username.pack(side="left", padx=5)
    entry_username = ttk.Entry(frame_username, font=("Helvetica", 12), width=20)
    entry_username.pack(side="right")
    # 密码标签和输入框
    frame_password = ttk.Frame(root_login)
    frame_password.pack(pady=10)
    label_password = ttk.Label(frame_password, text="密码:", font=("Helvetica", 12), width=10)
    label_password.pack(side="left", padx=5)
    entry_password = ttk.Entry(frame_password, font=("Helvetica", 12), width=20, show="*")
    entry_password.pack(side="right")
    # 读取上次登录用户（开源版本跳过远程验证）
    if os.path.exists('./userinfo.txt'):
        try:
            with open('./userinfo.txt', 'r') as f:
                userinfos = f.readlines()
                last_username = str(userinfos[0]).strip()
                last_password = str(userinfos[1]).strip()
                entry_username.insert(0, last_username)
                entry_password.insert(0, last_password)
        except:
            pass

    def login():
        """[专有代码已移除] 原实现通过 check_user() 连接远程数据库验证许可证"""
        # 开源版本：直接跳过登录进入主界面
        username = entry_username.get()
        print('username:', username)
        password = entry_password.get()
        print('password:', password)
        # [专有代码已移除] 远程许可证验证
        messagebox.showinfo('登录成功', '开源版本无需验证，直接进入主界面')
        root_login.destroy()
        create_spider_root()

    # 按钮框架
    frame_buttons = ttk.Frame(root_login)
    frame_buttons.pack(pady=20)
    # 登录按钮
    btn_login = ttk.Button(frame_buttons, text="登录", command=login, width=10)
    btn_login.grid(row=0, column=0, padx=10)
    # 退出按钮
    btn_quit = ttk.Button(frame_buttons, text="退出", command=root_login.quit, width=10)
    btn_quit.grid(row=0, column=1, padx=10)
    # 新用户注册按钮
    btn_register = tk.Button(frame_buttons, text="新用户注册", font=("Helvetica", 9), fg='blue', bd=0, cursor='hand2',
                             command=lambda: webbrowser.open("https://mgnb.pro/product/youtube_cmt", new=0))
    btn_register.grid(row=1, column=0, columnspan=2, pady=(10, 0))
    # 版权信息
    copyright = tk.Label(root_login, text='@马哥python说 All rights reserved.', font=('仿宋', 10), fg='grey')
    copyright.place(x=80, y=275)

    # 循环消息
    root_login.mainloop()


if __name__ == "__main__":
    # 创建日志目录
    if not os.path.exists('logs'):
        os.mkdir('logs')
    log = Log_week()
    logger = log.get_logger()
    # 开启主程序
    create_login_root()
