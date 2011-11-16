#!/usr/bin/python

import sys, os
import shlex
import subprocess
import re
import paramiko
import run_helper
import threading
import Queue



def get_biuld_dir():
    fc = open('configfile' , 'r')
    configtext = fc.read()
    fc.close()

    match = re.search(r'NODE_BUILD_DIR="(\S+)"', configtext)
    if not match:
        print 'Unable to find the build directory. Please set the proper NODE_BUILD_DIR in the config file'
        sys.exit(1)

    return match.group(1)



def check_exit_status(node, exit_status):
    if exit_status == 0:
        print node + ':     glusterfs Installation Complete!'
    elif exit_status == 1:
        print node + ':     autogen failed! Please check "autogen" logs'
    elif exit_status == 2:
        print node + ':     configure failed! Please check "configure" logs'
    elif exit_status == 3:
        print node + ':     make failed! Please check "make" logs'
    elif exit_status == 4:
        print node + ':     make install failed! Please check "make install" logs'
    else:
        print node + ':     improper exit code. Something went Bananas!!!'

    return 0


def real_install_gluster(node, tarball, build_dir, ret_queue):
        match = re.search(r'([\w.-]+).tar.gz', tarball)
        target_dir = match.group(1)

        run_helper.run_command(node, 'rm -rf ' + build_dir + '*', False)
        run_helper.run_command(node, 'mkdir -p ' + build_dir, False)
        run_helper.rcopy(node, tarball, build_dir, False)
        run_helper.run_command(node, 'cd ' + build_dir + ' && tar -xzf ' + tarball, False)
        run_helper.rcopy(node, 'buildit.py', build_dir + '/' + target_dir, False)
        exit_status = run_helper.run_command(node, 'cd ' + build_dir + '/' + target_dir + ' && ./buildit.py', False)
        print 'build started on ' + node

        check_exit_status(node, exit_status)
        ret_queue.put(exit_status)

        return 0



def install_gluster(tarball):
    all_nodes = run_helper.get_nodes_ip()
    nodes = []
    for node in all_nodes:
        if node not in nodes:
            nodes.append(node)

    clients = run_helper.get_client_ip()
    for client in clients:
        if client not in nodes:
            nodes.append(client)

    if not os.path.exists(tarball):
        print 'INFO: Source tarball ' + tarball + ' doesn\'t exist. Proceeding to download from bits.gluster.com'
        download_url = 'http://bits.gluster.com/pub/gluster/glusterfs/src/' + tarball
        cmd = 'wget ' +  download_url
        try:
            os.system(cmd)
        except:
            print 'unable to download ' + tarball + ' from bits.gluster.com'

    build_dir = get_biuld_dir()
    if build_dir[-1] != '/':
        build_dir = build_dir + '/'

    invalid_build_dir = ['/', '//', '/root', '/root/', '/usr', '/usr/', '/etc', '/etc/', '/sbin', '/sbin/', '/boot', '/boot/']
    if build_dir in invalid_build_dir:
        print build_dir + ' can not be build directory. Please provide other build directory'
        sys.exit(1)

    ret_queue = Queue.Queue()
    threads = []
    for node in nodes:
        t = threading.Thread(target=real_install_gluster, args=(node, tarball, build_dir, ret_queue))
        t.start()
        threads.append(t)

    return_value = 0
    ret_codes = []
    for t in threads:
        t.join()
        ret_codes.append(ret_queue.get())

    for ret in ret_codes:
        if ret != 0:
            return_value = 1
            break

    return return_value



def main_installer():
    gluster_version = run_helper.get_gluster_version()
    if gluster_version[-7:] != '.tar.gz':
        tarball = gluster_version + '.tar.gz'
    else:
        tarball = gluster_version

    status = install_gluster(tarball)
    if status:
        print 'Installation went Bananas. Please look into it.'

    return status

if __name__ == '__main__':
    main_installer()
