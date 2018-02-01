#!/bin/bash

mkdir -p /tools/
PythonUrl="https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz"

function install_Python2()
{
    python_version=$(python -V | awk '{print $2}' | awk -F'.' '{print $1}')
    test ${python_version} -eq 2 && { echo "$(python -V) , no need install." ; exit 1 ; }

    Python2Url="$1"
    if ! ls /tools/Python-2.*.tgz > /dev/null 2>&1 ; then
        wget -P /tools/ ${Python2Url}
    fi
    if ls /tools/Python-2.*.tgz > /dev/null 2>&1 ; then
        PyFile=$(ls /tools/Python-2.*.tgz | awk -F'/' '{print $NF}')
        cd /tools/
        tar zxvf ${PyFile}
        PyDir=$(ls -l | awk '/^d/ && $NF~/Python-2/{print $NF}')
        PyPath="/usr/local/${PyDir}"
        PyBin="${PyPath}/bin/python"
        ./configure --prefix=${PyPath}
        make && make install
        test ! -f ${PyBin} && { echo "install python2 fail." ; exit 1 ; }
        echo "${PyPath}/lib" > /etc/ld.so.conf.d/python2.conf
        ldconfig
        tabPath=$(find ${PyPath}/lib/ -name "site-packages" -type d)
        cat > ${tabPath}/tab.py <<EOF
#!/usr/bin/env python
# python startup file
import sys
import readline
import rlcompleter
import atexit
import os
# tab completion
readline.parse_and_bind('tab: complete')
# history file
histfile = os.path.join(os.environ['HOME'], '.pythonhistory')
EOF
    else
        echo "Python-2.*.tgz : No such file or directory."
        exit 1
    fi
}


function install_pip_setuptool()
{
    ## install pip setuptools
    if [ ! -f /tools/get-pip.py ] ; then
        wget -P /tools/ https://bootstrap.pypa.io/get-pip.py
    fi
    if [ ! -f /tools/ez_setup.py ] ; then
        wget -P /tools/ https://bootstrap.pypa.io/ez_setup.py
    fi

    if ls /usr/local/ | grep '[Pp]ython' > /dev/null ; then
        PythonDir=$(ls -l /usr/local/ | awk '/^d/ && $NF~/[Pp]ython/{print $NF}')
        PythonBin="/usr/local/${PythonDir}/bin/python"
    else
        PythonBin="/usr/bin/python"
    fi

    if [ -f /tools/get-pip.py ] ; then
        ${PythonBin} /tools/get-pip.py
    fi
    if [ -f /tools/ez_setup.py ] ; then
        ${PythonBin} /tools/ez_setup.py --insecure
    fi
}


install_Python2
install_pip_setuptool

