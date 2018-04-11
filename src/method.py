#!/usr/bin/python
# coding=utf8

import os
import sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE)
import settings
from fabric.api import run



def dir(app_dir,path=None,mkdir=False):
    app_install_dir = settings.APP_DIR[app_dir]
    if mkdir:
        if not run("if [ -d {dir} ];then echo '/opt/jdk dir exists!';fi".format(dir=app_install_dir)):
            run('mkdir -p {dir}'.format(dir=app_install_dir))

    if path != None:
        return os.path.join(app_install_dir,path)
    return app_install_dir


