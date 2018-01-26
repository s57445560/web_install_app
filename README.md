# 可配置的 通用部署平台

```
有什么问题可以联系我 QQ：247435333
欢迎大家可以提出宝贵意见。

```
---

## 安装与运行方法
		cd install/python27
		bash python_install.sh
		# 启动方法
		# python app.py
		# http://192.168.2.192:9999/install  配置 ip.conf文件 页面 (开始页)
		# http://192.168.2.192:9999/install/app_ip 配置 conf/app_ip.conf
		# http://192.168.2.192:9999/install/start 配置 conf/install.conf
		# http://192.168.2.192:9999 主安装页面
		# 前面url的打开顺序没有做限制，可以根据需求打开
		#
		# 如果使用页面配置方式，对文件编辑熟悉规则的话可以直接编辑如下3个文件：
		#     ip.conf conf/app_ip.conf conf/install.conf
		# 这样可以直接进入http://192.168.2.192:9999 安装页面


#### 从配置登陆服务器地址开始

![image](https://github.com/s57445560/img-all/raw/master/img-all/web_install/web_install01.png)

---

## settings.py 配置说明

#### 配置web头部信息

```
INFORMATION = "第三方项目部署平台"
```

#### 任务的设置

```
列表内的含义[ 页面上的任务序号(请按照顺序填写), 任务的中文名称, fabric的任务执行 ]

WEB_CONFIG = [
    [1,"查看网卡", "fab -f install.py ifconfig"],
    [2,"查看pwd", "fab -f install.py pwd"],
    [3,"查看/root/ls", "fab -f install.py ls"],
    [4,"查看主机hostname", "fab -f install.py hm"]

]
```

#### 安装应用时的配置文件关系填写

```
# 次修改的配置文件是 conf/app_ip.conf
#
# 列表内的含义[ 配置文件的key, 页面上的中文解释 ]

APP_INSTALL_CONFIG = [
    ['local_redis','本地redis地址'],
    ['mysql', 'mysql地址'],
    ['kafka', 'kafka所有地址'],
    ['zookeeper','zookeeper所有ip地址'],
    ['flume','flume其中一台ip地址'],

]
```

![image](https://github.com/s57445560/img-all/raw/master/img-all/web_install/web_install02.png)


#### 配置应用安装选择 

```
# 次修改的配置文件是 conf/install.conf
# 
# 配置要在 /install/start 安装的应用名称，用包名来定义，并且分类
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
# web标签id号(顺序填写)   应用名     应用类型
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
```
![image](https://github.com/s57445560/img-all/raw/master/img-all/web_install/web_install03.png)


#### 配置查看应用的类型分配

```
APP_TYPE = {
    'supp': 'java服务',
    'mid': '第三方服务',
    'comm': '前置机服务',
    'web': 'web服务',

}
```
![image](https://github.com/s57445560/img-all/raw/master/img-all/web_install/web_install04.png)

#### 第一次运行任务时候点击检查主机状态

可以看出那台服务器可以正常连接那台不可以，建议处理好不能正常连接的服务器后再开始任务<br>

![image](https://github.com/s57445560/img-all/raw/master/img-all/web_install/web_install05.png)

![image](https://github.com/s57445560/img-all/raw/master/img-all/web_install/web_install06.png)

