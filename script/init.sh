#！/bin/bash

echo 'nameserver 114.114.114.114'>/etc/resolv.conf
echo "dns ok!"

#set language

sed -i 's#\(LANG=\).*#\1"en_US.UTF-8"#g' /etc/sysconfig/i18n
source /etc/sysconfig/i18n

#set ntp
yum -y install ntp >/dev/null
echo "*/3 * * * * /usr/sbin/ntpdate cn.pool.ntp.org > /dev/null 2>&1" >> /var/spool/cron/root
service crond restart

#set ulimit
echo "ulimit -SHn 102400" >> /etc/rc.local
cat >> /etc/security/limits.conf << EOF
*           soft   nofile       65535
*           hard   nofile       65535
EOF

ulimit -SHn 102400

#add user
useradd cloudera-scm
useradd hadoop

#set sysctl
mv /etc/sysctl.conf /etc/sysctl.conf.bak

cat >> /etc/sysctl.conf << EOF
#表示系统同时保持TIME_WAIT的最大数 如果超过这个数立即清楚并打印告警信息
net.ipv4.tcp_max_tw_buckets = 6000
#关闭tcp_sack 这个选项应该启用，但是这会增加对 CPU 的占用。
net.ipv4.tcp_sack = 1
#开启tcp_window_scaling 要支持超过 64KB 的窗口，必须启用该值
net.ipv4.tcp_window_scaling = 1
#自动调优所使用的接受缓存区的值 最小 默认 最大
net.ipv4.tcp_rmem = 4096 87380 4194304
#自动调优定义每个socket使用的内存 最小 默认 最大
net.ipv4.tcp_wmem = 4096 16384 4194304
#为TCP socket预留用于发送缓冲的内存默认值
net.core.wmem_default = 8388608
#为TCP socket预留用于接收缓冲的内存默认值（单位：字节）
net.core.rmem_default = 8388608
#为TCP socket预留用于接收缓冲的内存最大值
net.core.rmem_max = 16777216
#TCP socket预留用于发送缓冲的内存最大值（单位：字节）
net.core.wmem_max = 16777216
#每个网络接口接收数据包的速率比内核处理这些包的速率快时，允许送到队列的数据包的最大数目
net.core.netdev_max_backlog = 262144
#listen(函数)的默认参数,挂起请求的最大数量限制
net.core.somaxconn = 262144
#系统所能处理不属于任何进程的TCP sockets最大数量
net.ipv4.tcp_max_orphans = 3276800
#表示SYN队列的长度，默认为1024，加大队列长度为262144，可以容纳更多等待连接的网络连接数。
net.ipv4.tcp_max_syn_backlog = 262144
#关闭TCP时间戳
net.ipv4.tcp_timestamps = 0
#减少系统SYN连接重试次数，为了打开对端的连接，内核需要发送一个SYN并附带一个回应前面一个SYN的ACK。
net.ipv4.tcp_synack_retries = 1
#在内核放弃建立连接之前发送SYN包的数量。
net.ipv4.tcp_syn_retries = 1
#确定 TCP 栈应该如何反映内存使用；每个值的单位都是内存页（通常是 4KB）内存实用化的下线 使用应用压力上限 内存上限
net.ipv4.tcp_mem = 94500000 915000000 927000000
#表示如果套接字由本端要求关闭，这个参数决定了它保持在FIN-WAIT-2状态的时间
net.ipv4.tcp_fin_timeout = 30
#表示当keepalive起用的时候，TCP发送keepalive消息的频度。缺省是2小时，改为5分钟
net.ipv4.tcp_keepalive_time = 300
#表示开启重用。允许将TIME-WAIT sockets重新用于新的 TCP 连接，默认为 0 表示关闭。 
net.ipv4.tcp_tw_reuse = 1
#表示开启TCP连接中TIME-WAIT sockets的快速收回功能，默认为 0 ，表示关闭。
net.ipv4.tcp_tw_recycle = 1
#表示用于向外连接的端口范围。
net.ipv4.ip_local_port_range = 5000 65000
#增加打开文件数的限制
fs.file-max = 6553560
kernel.shmall = 3294967296
kernel.shmmax = 1294967296
EOF
/sbin/sysctl -p

#cdh的系统调优
echo 0 > /proc/sys/vm/swappiness
sysctl -w vm.swappiness=0
echo never > /sys/kernel/mm/redhat_transparent_hugepage/defrag
echo never>/sys/kernel/mm/redhat_transparent_hugepage/enabled




#disable selinux
sed -i '/SELINUX/s/enforcing/disabled/' /etc/selinux/config
echo "selinux is disabled,you must reboot!"
setenforce 0


#disable iptables
/etc/init.d/iptables stop
chkconfig iptables off

#disable managernetwork
chkconfig NetworkManager off
/etc/init.d/NetworkManager stop

#epel 源
cd /etc/yum.repos.d/
rpm -ivh http://mirrors.ustc.edu.cn/fedora/epel/6/x86_64/epel-release-6-8.noarch.rpm


#install package
yum -y install telnet lzop >/dev/null
yum -y install  vim net-snmp patch openssl openssl-devel unzip make gcc gcc-devel lrzsz  pcre-devel autoconf bison bzip2 bzip2-devel cmake crontabs curl curl-devel gcc gcc-c++ glib2 glib2-devel glibc glibc-devel iptraf krb5-devel libevent-devel libidn libidn-devel libjpeg libjpeg-devel libpng libpng-devel libtool libtool-ltdl libxml2 libxml2-devel libxslt-devel lrzsz lsof make ncurses ncurses-devel nss_ldap ntp openssh openssh-clients openssl openssl-devel pam-devel setuptool strace Tcl/Tk unzip vim-enhanced wget zip zlib zlib-devel rsync dstat dos2unix unix2dos bc apr-util  automake bzip2-libs nc mtr mysql net-snmp-libs nmap pcre bind-utils  libselinux-python >/dev/null
#set jdk

cat >> /etc/profile << EOF
export JAVA_HOME=/opt/jdk
export CLASSPATH=\$CLASSPATH:\$JAVA_HOME/lib/*.jar
export PATH=\$JAVA_HOME/bin:\$PATH
export HISTTIMEFORMAT="%Y-%m-%d %H:%M:%S "
EOF

#set ssh
cat >> /etc/ssh/sshd_config <<EOF
PermitEmptyPasswords no
UseDNS no
EOF

sed -i 's#^\(GSSAPIAuthentication\).*#\1 no#' /etc/ssh/sshd_config 



/etc/init.d/sshd restart 
echo 'service is init is ok..............'
