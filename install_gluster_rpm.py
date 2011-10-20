#!/usr/bin/python

import sys, os
import run_helper
import re
import getopt


def usage():
    print 'Usage: install_gluster_rpm.py {[-d "install debuginfo"] [-g "install geo-replication"]',
    print '[-r "install rdma"] [-a "install all"}'
    return 0

def install_rpm(nodes, ,version, rpms):
    for node in nodes:
        for rpm in rpms:
            cmd = 'rpm -Uvh http://bits.gluster.com/pub/gluster/glusterfs/' + version + '/x86_64/glusterfs-' + rpm + '-' + version + '-1.x86_64.rpm'
            run_helper.run_command(node, cmd, True)

    return 0



def main():
    opt = arg = []
    try:
        opt, arg = getopt.getopt(sys.argv[1:], "dgra", ["debuginfo", "georep", "rdma", "all"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)

    rpms = ['core', 'fuse']

    for k in opt:
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

    all_nodes = run_helper.get_nodes_ip()
    nodes = []
    for node in all_nodes:
        if node not in nodes:
            nodes.append(node)

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

    install_rpm(nodes, version, rpms)

    return 0



if __name__ == '__main__':
  install_rpm()
