#!/usr/bin/python
# -*- coding: utf-8 -*-

from fabric.api import *
import ConfigParser
import os
import sys
import time
import logging
import socket
import re
import pickle



list_user_ip = []
ip_dict = {}
host_dict = {}
web_list = []
check_dict = {}
web_ip = []

web_path = '/opt/web_app'
supp_path = '/opt/supp_app'
comm_path = '/opt/comm_app'
mid_path = '/opt/mid_app'

fabric_path = os.getcwd()
all_app = []
dict_msg = {}
env.warn_only = True

app_start = {
    'alarmservice':'cd /opt/supp_app/alarmservice;bash services.sh start',
    'saveservice':'cd /opt/supp_app/saveservice;bash saveservice.sh start',
    'synservice':'cd /opt/supp_app/synservice;bash synservice.sh start',
    'openservice':'cd /opt/web_app/api/openservice;bash start.sh',
    'admin':'cd /opt/web_app/admin/bin;bash startup.sh',
    'duboo':'cd /opt/web_app/duboo/bin;bash startup.sh',
    'term_gb_svr':'/opt/comm_app/lbs/bin/term_gb_svr -r/opt/comm_app/lbs&',
    'plat_gb_cli':'',
    'plat_gb_svr':'/opt/comm_app/lbs/bin/plat_gb_svr -r/opt/comm_app/lbs&',
    'nginx':'/opt/mid_app/nginx/sbin/nginx -c /opt/mid_app/nginx/conf/nginx.conf',
    'redis':'cd /opt/mid_app/redis/;bash start.sh'
}



# 检查pickle本地序列化文件是否存在，如果存在则删除
if os.path.exists('log/pp.pkl'):
    os.remove('log/pp.pkl')


class Log:

    def __init__(
        self,
        logname,
        logger,
        level,
        ):
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(level)
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.DEBUG)
        formatter = \
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - message: %(message)s'
                              )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def getlog(self):
        return self.logger



class myconf(ConfigParser.ConfigParser):

    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


app_install = myconf()
app_ip = myconf()
app_port = myconf()

app_install.read('conf/install.conf')
app_ip.read('conf/app_ip.conf')
app_port.read('conf/port.conf')

result = os.popen('ifconfig |grep -Po "(?<=addr:)[\d.]+"|head -1')
this_machine_ip = result.read().rstrip()
print this_machine_ip
###########################################################


# 读取ip.conf 文件 来设置env.hosts 和env.passwords
with open('ip.conf') as f:
    for line in f.readlines():
        if line.rstrip() == '':
            continue
        list_line = line.rstrip().split()
        ip = list_line[0]
        if len(list_line) == 3:
            host = list_line[2]
            host_dict[ip] = host
        passwd = list_line[1]
        check_dict[ip] = 0
        ip_dict['root@' + ip + ':22'] = passwd
        ssh_ip = 'root@' + ip
        list_user_ip.append(ssh_ip)

env.hosts = list_user_ip

env.user = 'root'
env.passwords = ip_dict

# 写日志实例化
log = Log(logname='log/fabric.log', logger='fabric',
          level=logging.INFO).getlog()


# 如果主机名里带有web字样的 不让他执行 cm函数,需要增加可以在list里添加函数名
web_re = re.compile(r"web")

if sys.argv[-1] in ['cm','cm_start']:
    for ip,host in host_dict.items():
        if web_re.findall(host):
           web_list.append('root@'+ip)
    env.exclude_hosts = web_list


# 获取到所有的web ip地址 以便来写入nginx配置文件
for ip in app_install.sections():
    for app,name in app_install.items(ip):
        if app == 'admin':
            web_ip.append(ip)



@task
def hostname():
    run("sed -i 's/\(HOSTNAME=\).*/\\1%s/g' /etc/sysconfig/network"
        % host_dict[env.host])
    for (ip, hostname) in host_dict.items():
        run("egrep '\\b{ip}\\b' /etc/hosts >/dev/null&&sed -i 's/\({ip}\\b\).*/\\1 {hostname}/g' /etc/hosts||echo '{ip} {hostname}' >>/etc/hosts".format(ip=ip,
            hostname=hostname))
    run('hostname {name}'.format(name=host_dict[env.host]))


@task
def jdk():
    result = run("if [ -d /opt/jdk ];then echo '/opt/jdk dir exists!';fi")
    if result:
        log.error('{ip} {message}'.format(ip=env.host, message=result))
        return 'error'
    put('app/jdk-7u67-linux-x64.tar.gz', '/tmp/')
    result = \
        run("tar -zxf /tmp/jdk-7u67-linux-x64.tar.gz -C /opt/||echo 'tar jdk fail!'"
            )
    if result:
        log.error('{ip} {message}'.format(ip=env.host, message=result))
        return 'error'
    run('mv /opt/jdk1.7.0_67 /opt/jdk')
    run('mkdir -p /usr/java')
    run('ln -s /opt/jdk/ /usr/java/default')


@task
def cm():
    result = run("if [ -d /opt/cm-5.4.3 ];then echo '/opt/cm-5.4.3 dir exists!';fi")
    if result:
        log.error('{ip} {message}'.format(ip=env.host, message=result))
        return 'error'

    run("echo 'running..... put cloudera-manager-el6-cm5.4.3_x86_64.tar.gz'")
    put("app/cloudera-manager-el6-cm5.4.3_x86_64.tar.gz","/opt/")
    with cd('/opt'):
        run("echo 'running..... tar cloudera-manager-el6-cm5.4.3_x86_64.tar.gz'")
        result = run("tar -zxf cloudera-manager-el6-cm5.4.3_x86_64.tar.gz||echo 'tar cm fail!'")

        if result:
            log.error('{ip} {message}'.format(ip=env.host, message=result))
            return 'error'
    run("sed -i 's/\(server_host=\).*/\\1{ip}/g' /opt/cm-5.4.3/etc/cloudera-scm-agent/config.ini".format(ip=this_machine_ip))
    
    if this_machine_ip == env.host:
        run("yum install mysql mysql-server -y")
        result = run("/etc/init.d/mysqld restart >/dev/null|| echo 'mysql start fail!'")
        if result:
            log.error('{ip} {message}'.format(ip=env.host, message=result))
        local("mysql -uroot < script/init_mysql.sql")
        local("mkdir -p /usr/share/java/")
        local("source /etc/profile")
        local("cp app/mysql-connector-java.jar /usr/share/java/")
        local("bash /opt/cm-5.4.3/share/cmf/schema/scm_prepare_database.sh mysql cm cmur 123456")


@task
def cm_start():
    with cd("/opt/cm-5.4.3/etc/init.d"):
        if this_machine_ip == env.host:
            run("./cloudera-scm-server restart")
            run("./cloudera-scm-agent restart")
        else:
            run("./cloudera-scm-agent restart")



@task
def supp():
    supp_all = []
    comm_all = []
    web_all = []
    run("mkdir -p {supp_path}".format(supp_path=supp_path))
    if env.host not in app_install.sections():
        return 'exit'
    for app,name in app_install.items(env.host):
        if name == 'supp':
            supp_all.append(app)
    if supp_all:
        put('script/config_c.sh','/tmp/')

    for supp_app in supp_all:
        put('app/{app_name}.tar.gz'.format(app_name=supp_app),'/tmp/')
        run("tar -zxf /tmp/{app_name}.tar.gz -C {supp_path}".format(app_name=supp_app,supp_path=supp_path))
        run("bash /tmp/config_c.sh {supp_app} {supp_path} {l_redis} {c_redis} {kafka} {zookeeper} {mysql} {flume}".format(supp_app=supp_app,
            supp_path=supp_path+"/"+supp_app, l_redis=app_ip.get('config','local_redis'),c_redis=app_ip.get('config','cluse_redis'),
            kafka=app_ip.get('config','kafka'),zookeeper=app_ip.get('config','zookeeper'),mysql=app_ip.get('config','mysql'),flume=app_ip.get('config','flume')))




@task
def web():
    web_all = []
    config_nginx = False
    # 查看本机器是否需要安装 web程序
    if env.host not in app_install.sections():
        return 'exit'

    for app,name in app_install.items(env.host):
        if name == 'web':
            web_all.append(app) 
        elif app == 'nginx':
            config_nginx = True
    if web_all:
        put('script/config_c.sh','/tmp/')
        run("mkdir -p {web_path}".format(web_path=web_path))
        run("mkdir -p /opt/mid_app")
        put('app/admin.tar.gz','/opt/web_app')
        put('app/duboo.tar.gz','/opt/web_app')
        put('app/api.tar.gz','/opt/web_app')
        put('app/redis-3.2.3.tar.gz','/opt/mid_app')
        with cd('/opt/web_app'):
            run('tar -zxf admin.tar.gz')
            run('tar -zxf api.tar.gz')
            run('tar -zxf duboo.tar.gz')
        # redis的安装
        with cd('/opt/mid_app'):
            run('tar -zxf redis-3.2.3.tar.gz')
        with cd('/opt/mid_app/redis-3.2.3'):
            run('/usr/bin/make MALLOC=libc')
        with cd('/opt/mid_app/redis-3.2.3/src'):
            run('/usr/bin/make PREFIX=/opt/mid_app/local_redis install')
        run('mkdir -p /etc/redis')
        put('conf/6380.conf','/etc/redis/')
        put('conf/redis','/etc/init.d/')
        run("sed -i 's#/usr/local#/opt/mid_app/local_redis#g' /etc/init.d/redis")
        run("chmod 777 /etc/init.d/redis")
        run("echo '/etc/init.d/redis start' >>/etc/rc.local")
        run("/etc/init.d/redis start")
# web配置文件修改
    for web_app in web_all:
        if web_app == 'openservice':
            run("bash /tmp/config_c.sh {web_app} {web_path} {l_redis} {c_redis} {kafka} {zookeeper} {mysql} {hbase}".format(web_app=web_app,
                web_path=web_path+"/api/"+web_app, l_redis=app_ip.get('config','local_redis'),c_redis=app_ip.get('config','cluse_redis'),
                kafka=app_ip.get('config','kafka'),zookeeper=app_ip.get('config','zookeeper'),mysql=app_ip.get('config','mysql'),hbase=app_ip.get('config','hbase')))
        else:
            run("bash /tmp/config_c.sh {web_app} {web_path} {l_redis} {c_redis} {kafka} {zookeeper} {mysql} {hbase}".format(web_app=web_app,
                web_path=web_path+"/"+web_app, l_redis=app_ip.get('config','local_redis'),c_redis=app_ip.get('config','cluse_redis'),
                kafka=app_ip.get('config','kafka'),zookeeper=app_ip.get('config','zookeeper'),mysql=app_ip.get('config','mysql'),hbase=app_ip.get('config','hbase')))

# nginx配置修改
    if config_nginx:
        put("app/tengine-2.1.2.tar.gz","/tmp/tengine-2.1.2.tar.gz")
        run("yum install gcc pcre-devel openssl openssl-devel  -y")
        with cd("/tmp/"):
            run("tar -zxf tengine-2.1.2.tar.gz")
        with cd("/tmp/tengine-2.1.2"):
            run("./configure --prefix=/opt/mid_app/nginx")
            run("make&&make install")
        put("conf/nginx.conf","/opt/mid_app/nginx/conf/")
        for ip in web_ip:
            run("sed -i ':a;N;$!ba;s/blgxy_web/%s/' /opt/mid_app/nginx/conf/nginx.conf"%ip)
        run("sed -i '/blgxy_web/d' /opt/mid_app/nginx/conf/nginx.conf") 

# 设置admin主从配置
    if len(web_ip) == 2 and env.host in web_ip:
        print(web_ip)
        if web_ip.index(env.host):
            put("conf/ehcache.xml_m","{web_path}/admin/webapps/ROOT/WEB-INF/classes/ehcache.xml".format(web_path=web_path))
            run("sed -i 's/smc_config/{ip}/g' {web_path}/admin/webapps/ROOT/WEB-INF/classes/ehcache.xml".format(web_path=web_path,ip=web_ip[0]))
        else:
            put("conf/ehcache.xml_s","{web_path}/admin/webapps/ROOT/WEB-INF/classes/ehcache.xml".format(web_path=web_path))
            run("sed -i 's/smc_config/{ip}/g' {web_path}/admin/webapps/ROOT/WEB-INF/classes/ehcache.xml".format(web_path=web_path,ip=web_ip[1]))


@task
def comm():
    comm_list = []
    ctfo_redis = False
    if env.host not in app_install.sections():
        return 'exit'
    for app,name in app_install.items(env.host):
        if name == 'comm':
            comm_list.append(app) 
        elif app == 'redis':
            ctfo_redis = True
    if len(comm_list) > 0:
        put('app/lbs.tar.gz',"/tmp")
        put('script/config_c.sh',"/tmp")
        run("mkdir -p /opt/comm_app")
        run("tar -zxvf /tmp/lbs.tar.gz -C /opt/comm_app/")
        run("echo '1 1 * * * /bin/bash /opt/comm_app/lbs/bin/ziplog >/dev/null 2>&1 &' >> /var/spool/cron/root")
    for app in comm_list:
        run("bash /tmp/config_c.sh {app} {path} {redis} {c_redis} {kafka}".format(path=comm_path,app=app,redis=app_ip.get('config','local_redis'),
                   c_redis=app_ip.get('config','cluse_redis'),kafka=app_ip.get('config','kafka')))
    if ctfo_redis:
        put('app/redis.tar.gz',"/tmp")
        run("mkdir -p /opt/mid_app")
        run("tar -zxvf /tmp/redis.tar.gz -C /opt/mid_app/")
        run("cp /opt/mid_app/redis/bin/redis-cli /usr/local/bin/")
        run("sed -i 's/\\(.*\\) [0-9.]*\\(:.*\\)/\\1 {ip}\\2/g' {path}/redis/c1.txt".format(path=mid_path,ip=env.host))
        with cd("{path}/redis".format(path=mid_path)):
            run("bash start.sh;sleep 5")
            run("cat c1.txt|./bin/redis-cli")
    



@task
@parallel(pool_size=3)
def host_init():
    put("script/init.sh","/tmp")
    run("bash /tmp/init.sh")


@task
def test():
    with settings(abort_on_prompts=True):
        try:
            result = run('ifconfig')
        except:
            result = ''
        if result:
            check_dict[env.host] = 1



@task
@runs_once
def callback():
    b = open('log/pp.pkl','wb')
    pickle.dump(check_dict,b)
    b.close()
    print(check_dict)


@task
def start_rc():
    if env.host not in app_install.sections():
        return 'exit'

    for app,name in app_install.items(env.host):
        if app in app_start:
            if app == 'admin':
                run('echo "service redis start" >>/etc/rc.local')
                run('echo "%s" >>/etc/rc.local'%app_start[app])
            else:
                run('echo "%s" >>/etc/rc.local'%app_start[app])


@task
def ifconfig_t():
    run("ifconfig")

@task
def r_password():
    run("echo 'bIbXdJHFv+9k'|passwd --stdin root ")



@task
def rpm_install():
    put("app/rpm_yl.tar.gz","/tmp")
    with cd("/tmp"):
        run("tar -zxvf rpm_yl.tar.gz")
    with cd("/tmp/rpm_yl"):
        run("rpm -ivh *.rpm --force --nodeps")

@task
def ifconfig():
    run("ifconfig")




@task
def pwd():
    run("pwd")



@task
def ls():
    run("ls")


@task
def hm():
    run("hostname")
