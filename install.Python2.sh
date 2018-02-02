#!/bin/bash

function install_Python2()
{
    py_new_ver="$1"
    py_old_ver="$(python -V | awk '{print $2}')"
    if [[ "${py_new_ver}" == "${py_old_ver}" ]] ; then
        echo "python has been installed."
        exit 0
    fi

    test -d rm -rf /usr/local/Python && rm -rf rm -rf /usr/local/Python
    test -d /usr/local/Python-${py_new_ver} && rm -rf /usr/local/Python-${py_new_ver}
    wget -c https://www.python.org/ftp/python/${py_new_ver}/Python-${py_new_ver}.tgz && \
    tar zxvf Python-${py_new_ver}.tgz && \
    cd Python-${py_new_ver}/ && \
    ./configure --prefix=/usr/local/Python-${py_new_ver} && \
    make && make install
    if [[ $? -eq 0 ]] && [[ -f /usr/local/Python-${py_new_ver}/bin/python ]] ; then
        echo "/usr/local/Python-${py_new_ver}/lib" > /etc/ld.so.conf.d/python2.conf
        ldconfig
        mv /usr/bin/python /usr/bin/python_old
        ln -s /usr/local/Python-${py_new_ver}/bin/python /usr/bin/python
        
        install_pip ${py_new_ver}
        
        install_tab ${py_new_ver}

    else
        echo "python ver: ${py_new_ver} install fail."
        exit 1
    fi
}

function install_pip()
{
    test -f /usr/bin/pip && rm -f /usr/bin/pip
    wget https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    ln -s /usr/local/Python-$1/bin/pip /usr/bin/pip
}

function install_tab()
{
    pip install readline
    tabPath=$(find /usr/local/Python-$1/ -name "site-packages" -type d)
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
}


install_Python2 2.7.13
