#!/usr/bin/python

import sys, os
import run_helper
import re
import getopt
import threading
import Queue


def usage():
    print 'Usage: install_gluster_rpm.py {[-d "install debuginfo"] [-g "install geo-replication"]',
    print '[-r "install rdma"] [-a "install all"}'
    return 0

def install_rpm(node, version, rpms, ret_queue):
    flag = 0
    failed_rpms = []
    for rpm in rpms:
        cmd = 'rpm -Uvh http://bits.gluster.com/pub/gluster/glusterfs/' + version + '/x86_64/glusterfs-' + rpm + '-' + version + '-1.x86_64.rpm'
        status = run_helper.run_command(node, cmd, False)
        if status:
            flag = 1
            failed_rpms.append(rpm)

    if flag == 0:
        print '%s: Installation complete. Following rpms are successfully installed:' % node + ' '  + ','.join(rpms)
    else:
        print '%s: Installation FAILED. Following rpms failed to install:' % node + ' ' + ','.join.(failed_rpms)

    ret_queue.put(flag)

    return None



def install_gluster_rpms(rpms):

    nodes = run_helper.get_nodes_ip()

    clients = run_helper.get_client_ip()
    for client in clients:
        if client not in nodes:
            nodes.append(client)

    g_version = run_helper.get_gluster_version()
    if g_version[-7:] == '.tar.gz':
        gluster_version = g_version[:-7]
    else:
        gluster_version = g_version

    match = re.search(r'glusterfs-([\w.]+)', gluster_version)
    if not match:
        print 'unable to get gluster version to determine the rpm URL. Please check the configfile'
        sys.exit(1)
    version = match.group(1)

    ret_queue = Queue.Queue()
    threads = []
    for node in nodes:
        t = threading.Thread(target=install_rpm, args=(node, version, rpms, ret_queue))
        t.start()
        threads.append(t)

    ret_codes = []
    for t in threads:
        t.join()
        ret_codes.append(ret_queue.get())

    ret_value = 0
    for ret in ret_codes:
        if ret != 0:
            ret_value = 1
            break

    return ret_value



def main():
    opt = arg = []
    try:
        opt, arg = getopt.getopt(sys.argv[1:], "dgra", ["debuginfo", "georep", "rdma", "all"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)

    rpms = ['core', 'fuse']

    for k , v in opt:
        if k in ("-d", "--debuginfo"):
            rpms.append('debuginfo')
        elif k in ("-g", "--georep"):
            rpms.append('geo-replication')
        elif k in ("-r", "--rdma"):
            rpms.append('rdma')
        elif k in ("-a", "--all"):
            rpms = ['core', 'fuse', 'debuginfo', 'geo-replication', 'rdma']
        else:
            rpms = rpms

    print 'WARNING: There are some known issuew while installing from rpms using ,'
    print 'this script. Please try ',
    print 'downloading the rpms and using run_helper.py to install rpms, ',
    print 'should you encounter the error.'
    status = install_gluster_rpms(rpms)
    if status:
        print 'rpm installation went bananas in some machine. Please look into it.'

    return status


if __name__ == '__main__':
    main()
