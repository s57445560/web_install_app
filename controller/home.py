#!/usr/bin/python
# coding=utf8

import tornado.ioloop
import tornado.web
import hashlib
import time
import tornado.escape
import uuid, json
import os.path,copy
import pickle
import threading
import ConfigParser
import tornado.websocket

from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

# 获取上一层模块路径并且添加到python环境变量中
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(BASE)
import settings

WEB_CONFIG = settings.WEB_CONFIG
INFORMATION = settings.INFORMATION
APP_TYPE = settings.APP_TYPE


log_status = True
log_seek = 0
container = {}
message_list = ['欢迎使用部署系统']
num = 0
pid = 1
join_str = '>>log/tornado.log 2>&1;sleep 3;echo "{number}" > log/run.pid'
run_dict = {
    'check':'fab -f install.py test callback >>/dev/null;',
}

# 这个与上面的 run_dict 是对应关系,说明了前端显示的执行到哪一个步骤了 {'1':0,'2':0}
cookie_dic = {}
web_left = []
web_right = []

# 处理web左右显示数据
WEB_CONFIG_LEN = len(WEB_CONFIG)
if WEB_CONFIG_LEN%2 == 1:
    left = WEB_CONFIG_LEN/2+1
else:
    left = WEB_CONFIG_LEN/2

WEB_CONFIG_COUNT = 1
for line in WEB_CONFIG:
    run_dict[str(line[0])] = "".join([line[2],join_str.format(number=line[0])])
    cookie_dic[str(line[0])] = 0
    if WEB_CONFIG_COUNT <= left:
        web_left.append(line)
    else:
        web_right.append(line)
    WEB_CONFIG_COUNT += 1


class myconf(ConfigParser.ConfigParser):

    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


app_ip = myconf()



app_ip.read('conf/app_ip.conf')


class Session:									# 自定义一个session类专门来处理session相关
    # self.r_str 当前用户的随机字符串
    # handler 相当于是传递过来的业务类
    def __init__(self,handler):
        self.handler = handler							# 这个是传递过来的self
        self.random_str = self.handler.get_cookie('session_id', None)		# 获取cookie
        # 存在session_id 的cookie
        if self.random_str:
            # 合法cookie
            if self.random_str in container:
                self.r_str = self.random_str
            else:
                # 非法cookie
                self.add_session()
        else:
            # 不存在 session_id 的cookie
            self.add_session()
        # 设置cookie并且设置超时时间
        self.handler.set_cookie('session_id', self.random_str, expires=time.time() + 10000)

    @staticmethod
    def md5():							# 随机字符串生成
        m = hashlib.md5()
        m.update(bytes(str(time.time())))
        return m.hexdigest()

    def add_session(self):					# 生成随机字符串 然后添加到 字典中（也可以是redis）
        self.random_str = Session.md5()
        container[self.random_str] = {}
        self.r_str = self.random_str

    def set_seesion(self,key,value):				# 设置session函数
        container[self.r_str][key] = value

    def get_seesion(self,key,):					# 获取session函数
        return container[self.r_str].get(key, None)

    def del_seesion(self, key, ):				# 删除session函数
        if container[self.r_str].get(key, None):
            del container[self.r_str][key]
        else:
            raise KeyError('%s non-existent'% key)



##########################################################################



user_info =[]

class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session_obj = Session(self)

    def get(self):
        host_dic = {}
        app_type_dic = {}
        install_status = True
        app_install = myconf()
        app_install.read('conf/install.conf') 
        for key in APP_TYPE:
            app_type_dic[key] = []
        for ip in app_install.sections():
            host_dic[ip] = copy.deepcopy(app_type_dic)
        for ip in host_dic.keys():
            for k,v in app_install.items(ip):
                host_dic[ip][v].append(k)
                print(ip,k,v)
            print("--------------")
        install_cookie = self.session_obj.get_seesion('install_cookie')
        if not install_cookie:
            install_cookie = cookie_dic
            self.session_obj.set_seesion('install_cookie',install_cookie)
        ip_status = self.session_obj.get_seesion('ip_status')
        if not ip_status:
            ip_status = {}
            with open('ip.conf') as f:
                for i in f.readlines():
                    if i.rstrip() == '':
                        continue
                    ip = i.rstrip().split()[0]
                    ip_status[ip] = 0
            self.session_obj.set_seesion('ip_status',ip_status)
        print(install_cookie)
        print(host_dic)
        for num in range(1,len(install_cookie)+1):
            if install_cookie[str(num)] == 0:
                install_num = num - 1
                break
        else:
            install_num = num - 1
            install_status = False
        self.render('index.html',ip_status=ip_status, install_cookie=install_cookie,message_log=message_list,host_dic=host_dic,web_left=web_left,app_type=APP_TYPE,
                                              web_right=web_right,web_config=WEB_CONFIG,install_num=install_num,install_status=install_status,information=INFORMATION)





class MessageNewHandler(tornado.websocket.WebSocketHandler):                        # 前端POST发送信息的类
    clients = set()

    def initialize(self):
        self.session_obj = Session(self)

    def open(self):						# 客户端打开websocket的时候调用此函数
        self.num = 0
        self.status = True
        print('open')
        MessageNewHandler.clients.add(self)

    def on_close(self):						# 关闭请求的时候调用此函数
        MessageNewHandler.clients.remove(self)
        self.status = False


    def on_message(self, message):				# 当发过来客户端 send请求的时候才调用此函数
        log_list = []
        print('send',message)
        file_num = self.session_obj.get_seesion('file_num')
        if file_num == None:
            file_num = 0
        with open('log/tornado.log', 'r') as w_file:
            w_file.seek(file_num)
            for i in w_file:
                log_list.append(i.rstrip())
            self.session_obj.set_seesion('file_num', w_file.tell())
        global message_list
        message_list.extend(log_list)
        message_num = len(message_list)
        if message_num > 200:
            message_list = message_list[message_num - 200::]
        self.write_message(json.dumps({"message":log_list}))




class Checkhost(tornado.web.RequestHandler):
    def initialize(self):
        self.session_obj = Session(self)

    def post(self):
        status = False
        os.system("rm -rf log/run.pid")
        run_status = os.system(run_dict['check'])
        if run_status == 0:
            status = True
            p_file = open('log/pp.pkl','rb')
            ip_status = pickle.load(p_file)
            p_file.close()
            self.session_obj.set_seesion('ip_status',ip_status)
        self.write(json.dumps({'status':status}))

    def get(self):
        install_cookie = self.session_obj.get_seesion('install_cookie')
        message = self.get_argument('message',None)
        install_cookie[message] = 1
        self.session_obj.set_seesion('install_cookie',install_cookie)
        self.write(json.dumps({'status':True}))


class Runfabric(tornado.web.RequestHandler):

    def initialize(self):
        self.session_obj = Session(self)
#    
#    def post(self):
#        self.num = message = self.get_argument('num',None)
#        os.remove("log/run.pid")
#        f1 = threading.Thread(target=self.thread_run)
#        f1.start()
#        self.write(json.dumps({'status':True}))
#
#    def thread_run(self):
#        self.run_status = os.system(run_dict[self.num])
    executor = ThreadPoolExecutor(1)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        install_cookie = self.session_obj.get_seesion('install_cookie')
        self.num = message = self.get_argument('num',None)
        if int(self.num) > len(install_cookie):
            self.write(json.dumps({'status':False}))
        else:
            os.system("rm -rf log/run.pid")
            res = yield self.sleep()
            with open("log/run.pid",'rb') as f:
                file_num = f.read()
            print(file_num,"file_num")
            install_cookie[str(file_num.rstrip())] = 1
            self.session_obj.set_seesion('install_cookie',install_cookie)
            jump_id = int(file_num.rstrip())+1
            print(WEB_CONFIG[int(file_num.rstrip())-1][1])
            if int(self.num) == len(WEB_CONFIG):
                list_id = len(WEB_CONFIG) - 1
            else:
                list_id = int(file_num.rstrip())
            self.write(json.dumps({'status':True,'id': file_num.rstrip(),'jump_id':jump_id,'web_info':WEB_CONFIG[list_id][1]}))
            self.finish()

    @run_on_executor
    def sleep(self):
        self.num = message = self.get_argument('num',None)
        os.system(run_dict[self.num])
        return True
