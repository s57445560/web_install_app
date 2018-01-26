#!/usr/bin/python
# coding=utf8

import tornado.ioloop
import tornado.web
import hashlib
import time
import tornado.escape
import uuid, json
import os.path
import pickle
import threading
import ConfigParser

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

# 前台配置信息的时候的 下拉选择列表对应信息 /views/install_install.html 内对应
APP_CODE = settings.APP_CODE
APP_INSTALL_CONFIG = settings.APP_INSTALL_CONFIG
INFORMATION = settings.INFORMATION
container = {}
ip_list = []




class Session:                                                                  # 自定义一个session类专门来处理session相关
    # self.r_str 当前用户的随机字符串
    # handler 相当于是传递过来的业务类
    def __init__(self,handler):
        self.handler = handler                                                  # 这个是传递过来的self
        self.random_str = self.handler.get_cookie('session_id', None)           # 获取cookie
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
        self.handler.set_cookie('session_id', self.random_str, expires=time.time() + 600)

    @staticmethod
    def md5():                                                  # 随机字符串生成
        m = hashlib.md5()
        m.update(bytes(str(time.time())))
        return m.hexdigest()
                                                                                                                                                     
    def add_session(self):                                      # 生成随机字符串 然后添加到 字典中（也可以是redis）                                  
        self.random_str = Session.md5()                                                                                                              
        container[self.random_str] = {}                                                                                                              
        self.r_str = self.random_str                                                                                                                 
                                                                                                                                                     
    def set_seesion(self,key,value):                            # 设置session函数                                                                    
        container[self.r_str][key] = value                                                                                                           
                                                                                                                                                     
    def get_seesion(self,key,):                                 # 获取session函数                                                                    
        return container[self.r_str].get(key, None)                                                                                                  
                                                                                                                                                     
    def del_seesion(self, key, ):                               # 删除session函数                                                                    
        if container[self.r_str].get(key, None):                                                                                                     
            del container[self.r_str][key]                                                                                                           
        else:                                                                                                                                        
            raise KeyError('%s non-existent'% key)


class myconf(ConfigParser.ConfigParser):

    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults=None)                                                                                      
                                                                                                                                                     
    def optionxform(self, optionstr):                                                                                                                
        return optionstr  


app_ip = myconf()



app_ip.read('conf/app_ip.conf')                                                                                                                      

##################################################


class Install_ip(tornado.web.RequestHandler):
    def initialize(self):
        self.session_obj = Session(self)

    def get(self):
        self.render('install_ip.html',information=INFORMATION)

    def post(self):
        status = False
        print('11111')
        data_json = self.get_argument('message', None)
        data = json.loads(data_json)
        if data:
            status = True
            data_num = len(data)/3
            start = 0
            end = 3
            ip_file = open('ip.conf','w+')
            ip_file.truncate()
            for i in range(data_num):
                if i == 0:
                    print(data[start:end])
                    ip_file.write(' '.join(data[start:end])+"\n")
                    ip_list.append(data[start:end][0])
                else:
                    start = start + 3
                    end = end + 3
                    ip_file.write(' '.join(data[start:end])+"\n")
                    ip_list.append(data[start:end][0])
                    print(data[start:end])
            ip_file.close()
        print(data,ip_list)
        self.write(json.dumps({'status':status}))


class Install_app_ip(tornado.web.RequestHandler):
    def initialize(self):
        self.session_obj = Session(self)

    def get(self):
        self.render('install_app_ip.html',app_install_config=APP_INSTALL_CONFIG,information=INFORMATION)

    def post(self):
        status = False
        data_json = self.get_argument('message', None)
        data = json.loads(data_json)
        print(data)
        if data:
            status = True
            for key,value in data.items():
                app_ip.set("config", key, value)
            app_ip.write(open("conf/app_ip.conf", "w"))
        self.write(json.dumps({'status':status}))



class Install_install(tornado.web.RequestHandler):
    def initialize(self):
        self.session_obj = Session(self)

    def get(self):
        id_list = range(1,len(APP_CODE)+1)
        self.render('install_install.html',data=ip_list,app_code=APP_CODE,id_list=id_list,information=INFORMATION)

    def post(self):
        app_install = myconf()
        app_install.read('conf/install.conf')                                                                                                                
        status = False
        message = self.get_argument('message', None)
        if message:
            message = json.loads(message)
            print(message)
            for i in app_install.sections():
                app_install.remove_section(i)
                app_install.write(open("conf/install.conf", "w"))
            for key in message.keys():
                if message[key]:
                    app_install.add_section(key)
                    for app_num in message[key]:
                        app_install.set(key, APP_CODE[app_num][0], APP_CODE[app_num][1]) 
            app_install.write(open("conf/install.conf", "w")) 
            status = True
        self.write(json.dumps({'status':status}))

