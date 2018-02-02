#!/bin/bash


function install_Python3()
{
    version="$1"
    mkdir -p /tools/
    test -f /tools/Python-${version}.tgz && rm -f /tools/Python-${version}.tgz
    wget -P /tools/ https://www.python.org/ftp/python/${version}/Python-${version}.tgz
    if [[ $? -eq 0 ]] && [[ -f /tools/Python-${version}.tgz ]] ; then
        cd /tools/
        tar zxvf Python-${version}.tgz
        cd Python-${version}
        ./configure --prefix=/usr/local/Python-${version}
        make && make install
    fi
}

install_Python3 3.5.2
