#!/bin/bash


function install_Python3()
{
    py_new_ver="$1"
    test -f Python-${version}.tgz && rm -f Python-${version}.tgz
    wget -c https://www.python.org/ftp/python/${version}/Python-${version}.tgz && \
    tar zxvf Python-${version}.tgz && \
    cd Python-${version} && \
    ./configure --prefix=/usr/local/Python-${version} && \
    make && make install 
    if [[ $? -eq 0 ]] ; then
        echo "Python Ver : ${py_new_ver} install succeed."
        exit 0
    else
        echo "Python Ver : ${py_new_ver} install fail."
        exit 1
    fi
}

install_Python3 3.5.2
