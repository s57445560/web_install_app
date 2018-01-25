#!/usr/bin/python

import json
import requests
import ConfigParser


host_dic = {}


app_port = {
    'duboo':7080,
    'admin':7070,
    'openservice': 18080,
    'term_gb_svr': 19006,
    'redis_local': 6480,
    'redis': 6379,
    'hbase': 60020,
    'kafka': 9092,
    'flume': 1463,
    'zookeeper': 2181,
}

class myconf(ConfigParser.ConfigParser):

    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


app_install = myconf()
app_ip = myconf()

app_install.read('conf/install.conf')
app_ip.read('conf/app_ip.conf')


url = "http://192.168.60.13/zabbix/api_jsonrpc.php"
header = {"Content-Type": "application/json"}

jsondata = json.dumps(
    {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": "admin",
            "password": "zabbix"
        },
        "id": 0
    })





r = requests.get(url,headers=header,data=jsondata)


auth = r.json()['result']


hosts_json ={
    "jsonrpc": "2.0",
    "method": "host.get",
    "params": {
        "output": [
            "hostid",
            "host"
        ],
        "selectInterfaces": [
            "interfaceid",
            "ip"
        ]
    },
    "id": 2,
    "auth": auth
}



trigger = {"jsonrpc": "2.0","method": "trigger.create","params": [{"description": "tomcat error {HOST.NAME}",
           "expression": "{browser_master1_10.240.67.20:net.tcp.port[,80].min(5m)}=0","priority": 3,},],
           "auth": "66b61273b4d955a6d179a3932ab5329a","id": 4}


hosts = requests.get(url,headers=header,data=json.dumps(hosts_json))


for host in hosts.json()['result']:
    hostid = host['hostid']
    ip = host['interfaces'][0]['ip']
    id = host['interfaces'][0]['interfaceid']
    host_dic[ip] = [hostid,host['host'],id]


print(host_dic)

for i in app_install.sections():
    for app,v in app_install.items(i):
        if app in app_port:
            
            # port check
            check_port = {"jsonrpc": "2.0","method": "item.create","params": {"name": "%s port check"%app,"key_": "net.tcp.listen[%s]"%app_port[app],
                         "hostid": "%s"%host_dic[i][0],"type": 0,"value_type": 3,"interfaceid": "%s"%host_dic[i][2],"delay": 30},"auth": auth,"id": 1}
            hosts = requests.get(url,headers=header,data=json.dumps(check_port))

            trigger = {"jsonrpc": "2.0","method": "trigger.create","params": [{"description": "%s port down"%app,
                       "expression": "{%s:net.tcp.listen[%s].max(#3)}=0"%(host_dic[i][1],app_port[app]),"priority": 3,},],
                       "auth": auth,"id": 4}
            trig = requests.get(url,headers=header,data=json.dumps(trigger))

        elif app == 'role':

            # local redis
            check_port = {"jsonrpc": "2.0","method": "item.create","params": {"name": "%s port check"%"local_redis","key_": "net.tcp.listen[%s]"%"6380",
                         "hostid": "%s"%host_dic[i][0],"type": 0,"value_type": 3,"interfaceid": "%s"%host_dic[i][2],"delay": 30},"auth": auth,"id": 1}
            hosts = requests.get(url,headers=header,data=json.dumps(check_port))

            trigger = {"jsonrpc": "2.0","method": "trigger.create","params": [{"description": "%s port down"%"local_redis",
                       "expression": "{%s:net.tcp.listen[%s].max(#3)}=0"%(host_dic[i][1],6380),"priority": 3,},],
                       "auth": auth,"id": 4}
            trig = requests.get(url,headers=header,data=json.dumps(trigger))

            # nginx
            check_port = {"jsonrpc": "2.0","method": "item.create","params": {"name": "%s port check"%"nginx","key_": "net.tcp.listen[%s]"%"8000",
                         "hostid": "%s"%host_dic[i][0],"type": 0,"value_type": 3,"interfaceid": "%s"%host_dic[i][2],"delay": 30},"auth": auth,"id": 1}
            hosts = requests.get(url,headers=header,data=json.dumps(check_port))

            trigger = {"jsonrpc": "2.0","method": "trigger.create","params": [{"description": "%s port down"%"nginx",
                       "expression": "{%s:net.tcp.listen[%s].max(#3)}=0"%(host_dic[i][1],8000),"priority": 3,},],
                       "auth": auth,"id": 4}
            trig = requests.get(url,headers=header,data=json.dumps(trigger))

        elif v == 'supp':

            # supp
            check_server = {"jsonrpc": "2.0","method": "item.create","params": {"name": "%s process check"%app,"key_": "proc.num[,,all,%s]"%app,
                         "hostid": "%s"%host_dic[i][0],"type": 0,"value_type": 3,"interfaceid": "%s"%host_dic[i][2],"delay": 30},"auth": auth,"id": 1}
            hosts = requests.get(url,headers=header,data=json.dumps(check_server))

            trigger = {"jsonrpc": "2.0","method": "trigger.create","params": [{"description": "%s process down"%app,
                       "expression": "{%s:proc.num[,,all,%s].max(#3)}=0"%(host_dic[i][1],app),"priority": 3,},],
                       "auth": auth,"id": 4}
            trig = requests.get(url,headers=header,data=json.dumps(trigger))
            
        print(hosts.json())
        print(trig.json())

for app,v in app_ip.items('config'):
    if app in app_port:
        for ip in v.split(','):
            print(app,ip,app_port[app])
            check_port = {"jsonrpc": "2.0","method": "item.create","params": {"name": "%s port check"%app,"key_": "net.tcp.listen[%s]"%app_port[app],
                         "hostid": "%s"%host_dic[ip][0],"type": 0,"value_type": 3,"interfaceid": "%s"%host_dic[ip][2],"delay": 30},"auth": auth,"id": 1}
            hosts = requests.get(url,headers=header,data=json.dumps(check_port))

            trigger = {"jsonrpc": "2.0","method": "trigger.create","params": [{"description": "%s port down"%app,
                       "expression": "{%s:net.tcp.listen[%s].max(#3)}=0"%(host_dic[ip][1],app_port[app]),"priority": 3,},],
                       "auth": auth,"id": 4}
            trig = requests.get(url,headers=header,data=json.dumps(trigger))
            print(hosts.json())
            print(trig.json())
