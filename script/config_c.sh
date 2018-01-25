#!/bin/bash
#to write sunyang
#This script is a modified configuration file.
#bash config_c.sh [app] [path] [redis-m-192.168.0.1] [redis-s-192.168.0.2] [nginx-n-192.168.0.109] [oracle-a,oracle-b,oracle-c]

mccproxy_port=9000
monitor_port=9003
mreport_port=9004
information_port=9001
bminformation_port=9002
bfinformation_port=9006
statistics_port=9002
trackfileser_port=9040
MobileServer_port=9005
RestSer_port=9004
webServer_port=9005
rtcar_port=9008
clapp_port=88

mysql_passwd="smc@z9w5"




#alarmservice (){
#    local path=$1
#    local redis_ip=$2
#    local c_redis_ip=$3
#    local kafka_ip=`echo $4|sed -r 's/([0-9.]+)/\1:9092/g'`
#    local zookeeper=`echo $5|sed -r 's/([0-9.]+)/\1:2181/g'`
#    local mysql_ip=$6
#    local flume=`echo $7:1463`
#    sed -i 's/\(^database.mysql_jdbc_url=[^0-9]*\)[0-9.]*\(.*\)/\1'${mysql_ip}'\2/g' ${path}/system.properties
#    sed -i 's/\(^redis.host=\).*/\1'${c_redis_ip}'/g' ${path}/system.properties
#    sed -i 's/\(^database.mysql_password=\).*/\1'${mysql_passwd}'/g' ${path}/system.properties
#    sed -i 's/\(^rm.redis.host=\).*/\1'${c_redis_ip}'/g' ${path}/system.properties
#    sed -i 's/\(^kafka.hosts=\).*/\1'${kafka_ip}'/g' ${path}/system.properties
#    sed -i 's/\(^kafka.metadata.broker.list=\).*/\1'${kafka_ip}'/g' ${path}/system.properties
#    sed -i 's/\(^zookeeper.list=\).*/\1'${zookeeper}'/g' ${path}/system.properties
#
#}

alarmservice (){
    local path=$1
    local redis_ip=$2
    local c_redis_ip=$3
    local kafka_ip=`echo $4|sed -r 's/([0-9.]+)/\1:9092/g'`
    local zookeeper=`echo $5|sed -r 's/([0-9.]+)/\1:2181/g'`
    local mysql_ip=$6
    local flume=`echo $7:1463`
    sed -i 's/kafka_ip/'${kafka_ip}'/g' ${path}/application.yml
    sed -i 's/c_redis/'${c_redis_ip}'/g' ${path}/application.yml
    sed -i 's/mysql_ip/'${mysql_ip}'/g' ${path}/application.yml
    sed -i 's/zookeeper_ip/'${zookeeper}'/g' ${path}/application.yml

}



saveservice (){
    local path=$1
    local redis_ip=$2
    local c_redis_ip=$3
    local kafka_ip=`echo $4|sed -r 's/([0-9.]+)/\1:9092/g'`
    local zookeeper=$5
    local mysql_ip=$6
    local flume=`echo $7:1463`
    sed -i 's/\(^redisHost=\).*/\1'${c_redis_ip}'/g' ${path}/system.properties
    sed -i 's/\(^cacheHost=\).*/\1'${c_redis_ip}'/g' ${path}/system.properties
    sed -i 's/\(^kafkaHosts=\).*/\1'${kafka_ip}'/g' ${path}/system.properties
    sed -i 's/\(^zookeeperList=\).*/\1'${zookeeper}'/g' ${path}/system.properties
    sed -i 's/\(^flumeHost=\).*/\1'${flume}'/g' ${path}/system.properties

}


synservice (){
    local path=$1
    local redis_ip=$2
    local c_redis_ip=$3
    local kafka_ip=`echo $4|sed -r 's/([0-9.]+)/\1:9092/g'`
    local zookeeper=$5
    local mysql_ip=$6
    local flume=`echo $7:1463`
    sed -i 's/\(^redisHost=\).*/\1'${c_redis_ip}'/g' ${path}/system.properties
    sed -i 's/\(^kafkaHosts=\).*/\1'${kafka_ip}'/g' ${path}/system.properties
    sed -i 's/\(^zookeeperList=\).*/\1'${zookeeper}'/g' ${path}/system.properties
    sed -i 's/\(^oracleUser=\).*/\1root/g' ${path}/system.properties
    sed -i 's/\(^oraclePass=\).*/\1'${mysql_passwd}'/g' ${path}/system.properties
    sed -i 's#\(^oracleUrl=\).*#\1jdbc:mysql://'${mysql_ip}':3306/evsmc#g' ${path}/system.properties

}

openservice (){
    local path=$1
    local redis_ip=$2
    local c_redis_ip=$3
    local kafka_ip=`echo $4|sed -r 's/([0-9.]+)/\1:9092/g'`
    local zookeeper=`echo $5|sed -r 's/([0-9.]+)/\1:2181/g'`
    local mysql_ip=$6
    local hbase=$7
    sed -i 's/\(^KAFKA_BROKER_ADDRESS=\).*/\1'${kafka_ip}'/g' ${path}/start.sh
    sed -i 's/\(^KAFKA_ZOOKEEPER_ADDRESS=\).*/\1'${zookeeper}'/g' ${path}/start.sh
    sed -i 's/\(^SPRING_REDIS_HOST=\).*/\1'${c_redis_ip}'/g' ${path}/start.sh
    sed -i 's/\(^oracleUser=\).*/\1root/g' ${path}/start.sh
    sed -i 's/\(^SPRING_HBASE_QUORUM=\).*/\1'${hbase}'/g' ${path}/start.sh

}

admin (){
    local path=$1
    local redis_ip=$2
    local openservice=$2
    local c_redis_ip=$3
    local kafka_ip=`echo $4|sed -r 's/([0-9.]+)/\1:9092/g'`
    local zookeeper=`echo $5|sed -r 's/([0-9.]+)/\1:2181/g'`
    local mysql_ip=$6
    local hbase=$7
    sed -i 's#\(^jdbc.url.*//\).*\(:3306.*\)#\1'${mysql_ip}'\2#g' ${path}/webapps/ROOT/WEB-INF/classes/config.properties
    sed -i 's/^\(jdbc.password=\).*/\1'${mysql_passwd}'/g' ${path}/webapps/ROOT/WEB-INF/classes/config.properties
    sed -i 's/\(^kafka.metadata.broker.list = \).*/\1'${kafka_ip}'/g' ${path}/webapps/ROOT/WEB-INF/classes/sysDefine.properties
    sed -i 's/\(^kafka.zookeeper.list = \).*/\1'${zookeeper}'/g' ${path}/webapps/ROOT/WEB-INF/classes/sysDefine.properties
    sed -i 's#\(^bitnei.openservice.url.*http://\).*\(:.*\)#\1'${openservice}'\2#g' ${path}/webapps/ROOT/WEB-INF/classes/sysDefine.properties
    sed -i 's/\(^redis.host=\).*/\1'${redis_ip}'/g' ${path}/webapps/ROOT/WEB-INF/classes/redis.properties
    sed -i 's/\(^redis.port=\).*/\16380/g' ${path}/webapps/ROOT/WEB-INF/classes/redis.properties
    sed -i 's/\(^redis.pass=\).*/\1123456/g' ${path}/webapps/ROOT/WEB-INF/classes/redis.properties
    sed -i 's/\(^redis.cto.host=\).*/\1'${c_redis_ip}'/g' ${path}/webapps/ROOT/WEB-INF/classes/redis.properties
    local zookeeper_m=`echo $zookeeper|awk -F"," '{print $1}'`
    local zookeeper_a=`echo $zookeeper|sed 's/^[0-9.]*:[0-9]*,//g'`
    sed -i 's#\(<dubbo:registry address="zookeeper://\)[0-9.]*:2181\(.*\)#\1'${zookeeper_m}'\2#g' ${path}/webapps/ROOT/WEB-INF/classes/dubbo-consumer.xml
    sed -i 's#\(.*backup=\)[0-9.,:]*\(.*\)#\1'${zookeeper_a}'\2#g' ${path}/webapps/ROOT/WEB-INF/classes/dubbo-consumer.xml
    dos2unix ${path}/webapps/ROOT/WEB-INF/classes/config.properties
    dos2unix ${path}/webapps/ROOT/WEB-INF/classes/sysDefine.properties
    dos2unix ${path}/webapps/ROOT/WEB-INF/classes/redis.properties
    dos2unix ${path}/webapps/ROOT/WEB-INF/classes/dubbo-consumer.xml

}

duboo (){
    local path=$1
    local redis_ip=$2
    local c_redis_ip=$3
    local kafka_ip=`echo $4|sed -r 's/([0-9.]+)/\1:9092/g'`
    local zookeeper_ip=$5
    local zookeeper=`echo $5|sed -r 's/([0-9.]+)/\1:2181/g'`
    local mysql_ip=$6
    local hbase=$7
    sed -i 's/\(^redis.host.from=\).*/\1'${redis_ip}'/g' ${path}/webapps/EnergyDataCenter/WEB-INF/classes/system.properties
    sed -i 's/\(^redis.port.from=\).*/\16380/g' ${path}/webapps/EnergyDataCenter/WEB-INF/classes/system.properties
    sed -i 's/\(^redis.password.from=\).*/\1123456/g' ${path}/webapps/EnergyDataCenter/WEB-INF/classes/system.properties
    sed -i 's/\(^cacheHost=\).*/\1'${c_redis_ip}'/g' ${path}/webapps/EnergyDataCenter/WEB-INF/classes/system.properties

    sed -i 's#\(<value>\)[0-9]*\.[0-9.,]*\(</value>\)#\1'${zookeeper_ip}'\2#g' ${path}/webapps/EnergyDataCenter/WEB-INF/classes/hbase-site.xml
    local zookeeper_m=`echo $zookeeper|awk -F"," '{print $1}'`
    local zookeeper_a=`echo $zookeeper|sed 's/^[0-9.]*:[0-9]*,//g'`
    sed -i 's#\(<dubbo:registry address="zookeeper://\)[0-9.]*:2181\(.*\)#\1'${zookeeper_m}'\2#g' ${path}/webapps/EnergyDataCenter/WEB-INF/classes/dubbo-provider.xml
    sed -i 's#\(.*backup=\)[0-9.,:]*\(.*\)#\1'${zookeeper_a}'\2#g' ${path}/webapps/EnergyDataCenter/WEB-INF/classes/dubbo-provider.xml

}

term_gb_svr (){
    local path=$1
    local redis_ip=$2
    local c_redis_ip=$3
    local kafka_ip=`echo $4|sed -r 's/([0-9.]+)/\1:9092/g'`
    sed -i 's/\(^rediscluster=\).*/\1'${c_redis_ip}':6379/g' ${path}/lbs/conf/ws/term_gb_svr.conf
    sed -i 's/\(^brokers=\).*/\1'${kafka_ip}'/g' ${path}/lbs/conf/ws/term_gb_svr.conf

}

plat_gb_cli (){
    local path=$1
    local redis_ip=$2
    local c_redis_ip=$3
    local kafka_ip=`echo $4|sed -r 's/([0-9.]+)/\1:9092/g'`
    sed -i 's/\(^rediscluster=\).*/\1'${c_redis_ip}':6379/g' ${path}/lbs/conf/ws/plat_gb_cli.conf
    sed -i 's/\(^kafka_brokers=\).*/\1'${kafka_ip}'/g' ${path}/lbs/conf/ws/plat_gb_cli.conf

}


plat_gb_svr (){
    local path=$1
    local redis_ip=$2
    local c_redis_ip=$3
    local kafka_ip=`echo $4|sed -r 's/([0-9.]+)/\1:9092/g'`
    sed -i 's/\(^rediscluster=\).*/\1'${c_redis_ip}':6379/g' ${path}/lbs/conf/ws/plat_gb_svr.conf
    sed -i 's/\(^brokers=\).*/\1'${kafka_ip}'/g' ${path}/lbs/conf/ws/plat_gb_svr.conf

}



case "$1" in
alarmservice)
    alarmservice $2 $3 $4 $5 $6 $7 $8
    ;;
saveservice)
    saveservice $2 $3 $4 $5 $6 $7 $8
    ;;
synservice)
    synservice $2 $3 $4 $5 $6 $7 $8
    ;;
openservice)
    openservice $2 $3 $4 $5 $6 $7 $8
    ;;
admin)
    admin $2 $3 $4 $5 $6 $7 $8
    ;;
duboo)
    duboo $2 $3 $4 $5 $6 $7 $8
    ;;
term_gb_svr)
    term_gb_svr $2 $3 $4 $5
    ;;
plat_gb_svr)
    plat_gb_svr $2 $3 $4 $5
    ;;
plat_gb_cli)
    plat_gb_cli $2 $3 $4 $5
    ;;
*)
    echo "no service"
    ;;
esac
