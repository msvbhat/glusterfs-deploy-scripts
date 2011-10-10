#!/usr/bin/python

import sys, os
import commands
import subprocess
import shlex


def main():

# Run autogen
    faout = open('autogen.out.remote', 'w')
    faerr = open('autogen.err.remote', 'w')
    ap = subprocess.Popen(['./autogen.sh'], stdout=faout, stderr=faerr).wait()
    faout.close()
    faerr.close()
    if ap:
        sys.exit(1)

#Run configure
    fcout = open('configure.out.remote', 'w')
    fcerr = open('configure.err.remote', 'w')
    cp = subprocess.Popen(['./configure CFLAGS="-g -DDEBUG -O0"'], shell=True, stdout=fcout, stderr=fcerr).wait()
    fcout.close()
    fcerr.close()
    if cp:
        sys.exit(2)

#Run make
    fmout = open('make.out.remote', 'w')
    fmerr = open('make.err.remote', 'w')
    mp = subprocess.Popen(['make'], stdout=fmout, stderr=fmerr).wait()
    fmout.close()
    fmerr.close()
    if mp:
        sys.exit(3)

#Run make install
    fiout = open('makeinstall.out.remote', 'w')
    fierr = open('makeinstall.err.remote', 'w')
    ip = subprocess.Popen(['make', 'install'], stdout=fiout, stderr=fierr).wait()
    fiout.close()
    fierr.close()
    if ip:
        sys.exit(4)

#Retrun 0 if al are successful
    sys.exit(0)

if __name__ == '__main__':
    main()
