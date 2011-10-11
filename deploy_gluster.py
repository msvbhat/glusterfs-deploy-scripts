#!/usr/bin/python

import sys, os
import shlex
import subprocess
import re
import paramiko
import run_helper
import threading



def get_tarball():
    fc = open('configfile', 'r')
    configtext = fc.read()
    fc.close()

    tarball_match = re.search(r'GLUSTER_TARBALL="([\w.-]+.tar.gz)"', configtext)
    if not tarball_match:
        print 'ERROR: Empty tarball. Please set the GLUSTER_TARBALL in config file'
        sys.exit(1)

    tarball = tarball_match.group(1)

    return tarball



def get_biuld_dir():
    fc = open('configfile' , 'r')
    configtext = fc.read()
    fc.close()

    match = re.search(r'NODE_BUILD_DIR="([\w/]+)"', configtext)
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


def real_install_gluster(node, tarball, build_dir):
        match = re.search(r'([\w.-]+).tar.gz', tarball)
        target_dir = match.group(1)

        run_helper.run_command(node, 'mkdir -p ' + build_dir, False)
        run_helper.rcopy(node, tarball, build_dir, False)
        run_helper.run_command(node, 'cd ' + build_dir + ' && tar -xzf ' + tarball, False)
        run_helper.rcopy(node, 'buildit.py', build_dir + '/' + target_dir, False)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(node, username='root', password='')
        chan = ssh.get_transport().open_session()
        chan.exec_command('cd ' + build_dir + '/' + target_dir + ' && ./buildit.py')
        print 'build started on ' + node

        exit_status = chan.recv_exit_status()
        check_exit_status(node, exit_status)

        return 0



def install_gluster():
    nodes = run_helper.get_nodes_ip()

    tarball = get_tarball()
    if not os.path.exists(tarball):
        print 'INFO: Source tarball ' + tarball + ' doesn\'t exist. Proceeding to download from bits.gluster.com'
        download_url = 'http://bits.gluster.com/pub/gluster/glusterfs/src/' + tarball
        cmd = 'wget ' +  download_url
        try:
            os.system(cmd)
        except:
            print 'unable to download ' + tarball + ' from bits.gluster.com'


    build_dir = get_biuld_dir()

    threads = []
    for node in nodes:
        t = threading.Thread(target=real_install_gluster, args=(node, tarball, build_dir))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return 0


if __name__ == '__main__':
    install_gluster()
