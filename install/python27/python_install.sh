#!/bin/bash

pwd=`pwd`


yum install gcc zlib-devel openssl-devel readline-devel sqlite-devel sqlite2-devel build-essential libssl-devel libffi-devel -y

cd Python-2.7.12

./configure --prefix=/usr/local/python2.7
make
make install

if [[ $? != 0 ]]
then
    echo "install fail!!!!!"
    exit
fi


mv /usr/bin/python /usr/bin/python.old

ln -s /usr/local/python2.7/bin/python2.7 /usr/bin/python

sed -i 's#bin/python$#/bin/python2.6#g' /usr/bin/yum

cd $pwd


python ez_setup.py

cd pip-9.0.1

python setup.py install

cd /usr/local/python2.7/bin

./pip install fabric

rm -rf /usr/bin/fab

ln -s /usr/local/python2.7/bin/fab /usr/bin/fab

./pip install tornado
./pip install futures
