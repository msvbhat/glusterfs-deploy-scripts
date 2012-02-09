#!/bin/bash

prefix=''
if [ $# -ge 1 ]; then
    prefix="--prefix=$1"
fi

./autogen.sh 2>err.autogen.sh 1>out.autogen.sh

./configure $prefix 2>err.configure 1>out.configure
if [ $? -ne 0 ]; then
    exit 2
fi

make 2>err.make 1>out.make
if [ $? -ne 0 ]; then
    exit 3
fi

make install 2>err.make_install 1>out.make_install
if [ $? -ne 0 ]; then
    exit 4
fi

exit 0
