#!/bin/sh
# 自动拷由配置文件，还有修改项目配置



# 配置Redis
echo "####################### Redis开始配置 ###############################"
# 转到目录
cd redis-3.2.3
# 编译，要加MALLOC=libc，否则可能报错
/usr/bin/make MALLOC=libc 
# 转到src目录
cd src
# 安装
/usr/bin/make PREFIX=/opt/mid_app/redis install
# 创建配置目录
mkdir -p /etc/redis
#将配置文件拷到/etc/redis，注意，避免冲突，我们将redis的端口改为6380

#更改路径
sed -i 's#/usr/local#/opt/mid_app/redis#g' /etc/rc.d/init.d/redis
# 增加到系统服务
chkconfig --add redis
#设置为开机自启动
chkconfig redis on  
# 启动Redis
service redis start

echo "################################ Redis配置完成 ############################"




