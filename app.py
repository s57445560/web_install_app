#!/usr/bin/python
# coding=utf8


import tornado.ioloop
import tornado.web
import tornado.iostream
import os

from controller.home import MainHandler, MessageNewHandler, Checkhost, Runfabric
from controller.install_conf import Install_ip, Install_app_ip, Install_install
from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line


os.system(">log/tornado.log")
if os.path.exists('log/run.pid`'):
    os.remove("log/run.pid")

check_app_list = ['alarmservice.tar.gz','lbs.tar.gz','mysql-connector-java.jar','jdk-7u67-linux-x64.tar.gz',
                 'redis.tar.gz','saveservice.tar.gz','synservice.tar.gz','cloudera-manager-el6-cm5.4.3_x86_64.tar.gz',]

########################### check app package
current_app = os.listdir('app/')
not_exist_app = []

for app in check_app_list:
    if app not in current_app:
       not_exist_app.append(app)

#if not_exist_app:
#    print("\033[31m请准备以下程序包放在 app/目录下.\033[0m") 
#    print("%s"%not_exist_app)
#    exit(1)


###########################






parse_command_line()
define("port", default=9999, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")

settings = {
'template_path': 'views',
'static_path': 'static',
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/message/new", MessageNewHandler),
    (r"/check/host", Checkhost),
    (r"/run/fabric", Runfabric),
    (r"/install", Install_ip),
    (r"/install/app_ip", Install_app_ip),
    (r"/install/start", Install_install),
],**settings)

if __name__ == "__main__":
    application.listen(9999)
    # epoll + socket
    print('\033[31m%s\033[0m'%"-"*45)
    print('\033[31m***** please open http://ip:9999/install **** \033[0m')
    print('\033[31m%s\033[0m'%"-"*45)
    tornado.ioloop.IOLoop.instance().start()

