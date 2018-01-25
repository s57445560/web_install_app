#!/usr/bin/python
# coding:utf-8


# 页面头部信息自定义

INFORMATION = "第三方项目部署平台"


# 任务的设置
WEB_CONFIG = [
    [1,"查看网卡", "fab -f install.py ifconfig"],
    [2,"查看pwd", "fab -f install.py pwd"],
    [3,"查看/root/ls", "fab -f install.py ls"],
    [4,"查看主机hostname", "fab -f install.py hm"]

]


# 安装应用所需要的配置文件信息

APP_INSTALL_CONFIG = [
    ['local_redis','本地redis地址'],
    ['mysql', 'mysql地址'],
    ['kafka', 'kafka所有地址'],
    ['zookeeper','zookeeper所有ip地址'],
    ['flume','flume其中一台ip地址'],

]


# 要在 /install/start 安装的应用名称，用包名来定义，并且分类
# 
# supp 是存放java服务器目录
# web 是存放web相关的服务
# comm 存放前置机类型服务
# mid 存放第三方软件
# 目录规范如下 /opt/supp_app /opt/web_app /opt/comm_app /opt/mid_app
#
# 可以跟据自己需求来自定义
#
# 
# web标签id号   应用名     应用类型
# '1': ['alarmservice','supp']
#
APP_CODE = {
    '1': ['alarmservice','supp'],
    '2': ['saveservice','supp'],
    '3': ['synservice','supp'],
    '4': ['admin','web'],
    '5': ['duboo','web'],
    '6': ['openservice','web'],
    '7': ['nginx','mid'],
    '8': ['term_gb_svr','comm'],
    '9': ['plat_gb_svr','comm'],
    '10': ['plat_gb_cli','comm'],
    '11': ['redis','mid'],
    '12': ['sunyang','mid']
}


# 配置 index.html内的 查看配置信息

APP_TYPE = {
    'supp': 'java服务',
    'mid': '第三方服务',
    'comm': '前置机服务',
    'web': 'web服务',

}


