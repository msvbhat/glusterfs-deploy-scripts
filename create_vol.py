#!/usr/bin/python

import os, sys
import re
import run_helper


def get_server_export_dir():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()
    
    match = re.search(r'SERVER_EXPORT_DIR="(\S+)"', configtext)
    if not match:
        print 'Unable to find the server export directory. Please set SERVER_EXPORT_DIR in configfile'
        sys.exit(1)

    export_dir = match.group(1)
    invalid_export_dir = ['/', '//', '/root', '/root/', '/usr', '/usr/', '/etc', '/etc/', '/sbin', '/sbin/', '/boot', '/boot/']
    if export_dir in invalid_export_dir:
        print export_dir + ' can NOT be the server export directory. Please give other valid directory'
        sys.exit(1)

    return export_dir



def get_volume_type():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()

    match = re.search(r'VOL_TYPE="([\w-]+)"', configtext)
    if not match:
        print 'Unable to find the gluster volume type. Please set the VOL_TYPE in configfile to proper gluster volume type'
        sys.exit(1)

    vol_type = match.group(1)
    supported_vol_types = ['dist', 'rep', 'stripe', 'dist-rep', 'stripe-rep', 'dist-stripe-rep', 'dist-stripe']
    if vol_type not in supported_vol_types:
        print vol_type + ' is not a supported gluster volume type. Please set the proper volume type'
        sys.exit(1)

    return vol_type



def get_vol_name():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()
    
    match = re.search(r'VOLNAME="(\S+)"', configtext)
    if not match:
        print 'Unable to find the volume name. Please set VOLNAME in configfile'
        sys.exit(1)

    return match.group(1)



def get_replica_count():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()

    match = re.search(r'REPLICA_COUNT="(\d+)"', configtext)
    if not match:
        print 'Unable to find the replica count. Please set the REPLICA_COUNT in configfile'
        sys.exit(1)

    replica_count = match.group(1)
    if replica_count < '2':
        print 'replica count can not be less than 2'
        sys.exit(1)

    return replica_count




def get_stripe_count():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()

    match = re.search(r'STRIPE_COUNT="(\d+)"', configtext)
    if not match:
        print 'Unable to find the stripe count. Please set the STRIPE_COUNT in configfile'
        sys.exit(1)

    stripe_count = match.group(1)
    if stripe_count < '2':
        print 'stripe count can not be less than 2'
        sys.exit(1)

    return stripe_count




def get_trans_type():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()
    
    match = re.search(r'TRANS_TYPE="([\w,]+)"', configtext)
    if not match:
        print 'Unable to find the transport type. Please set the TRANS_TYPE in configfile to proper supported transport type'
        sys.exit(1)

    trans_type = match.group(1)
    supported_trans_types = ['tcp', 'rdma', 'tcp,rdma']
    if trans_type not in supported_trans_types:
        print trans_type + ' is not a supported transport type. Please set the proper supported transport type'
        sys.exit(1)

    return trans_type



def pre_create_cleanup(nodes, export_dir):
    for node in nodes:
        cmd = 'pgrep gluster | xargs kill -9'
        run_helper.run_command(node, cmd, False) 

        cmd = 'rm -rf ' + export_dir
        run_helper.run_command(node, cmd, False) 

        cmd = 'rm -rf /etc/glusterd'
        run_helper.run_command(node, cmd, False) 

        cmd = 'rm -rf /usr/local/var/log/glusterfs/*'
        run_helper.run_command(node, cmd, False) 

    return 0


def create_gluster_volume():
    mgmt_node = run_helper.get_mgmt_node()
    nodes = run_helper.get_nodes_ip()
    if mgmt_node not in nodes:
        print 'management node MUST be part of the server nodes'
        sys.exit(1)

    export_dir = get_server_export_dir()
    vol_type = get_volume_type()
    trans_type = get_trans_type()
    volname = get_vol_name()

    pre_create_cleanup(nodes, export_dir)

    brick_list = ''
    for node in nodes:
        brick_list =  brick_list + node + ':' + export_dir + ' '

    replica_count = ''
    if vol_type == 'dist-rep' or vol_type == 'stripe-rep' or vol_type == 'rep' or vol_type == 'dist-stripe-rep':
        replica_count = 'replica ' + get_replica_count()

    stripe_count = ''
    if vol_type == 'stripe' or vol_type == 'stripe-rep' or vol_type == 'dist-stripe-rep' or vol_type == 'dist-stripe':
        stripe_count = 'stripe ' + get_stripe_count()

    vol_create_cmd = 'gluster volume create ' + volname + ' ' + replica_count + ' ' + stripe_count + ' ' + 'transport ' + trans_type + ' ' + brick_list

    flag = 0
    for node in nodes:
        status = run_helper.run_command(node, 'glusterd', False)
        if status:
            print 'glusterd can not be started in node: ' + node
            flag = 1

    if flag:
        print 'glusterd can not be started successfully in all nodes. Exiting...'
        sys.exit(1)

    flag = 0
    for node in nodes:
        if node != mgmt_node:
            status = run_helper.run_command(mgmt_node, 'gluster peer probe ' + node, False)
            if status:
                print 'peer probe went wrong in ' + node
                flag = 1

    if flag:
        print 'Peer probe went wrong in some machines. Exiting...'
        sys.exit(1)

    status = run_helper.run_command(mgmt_node, vol_create_cmd, True)
    if status:
        print 'volume creation failed.'

    return status




def start_gluster_volume():
    volname = get_vol_name()
    mgmt_node = run_helper.get_mgmt_node();
    vol_start_cmd = 'gluster volume start ' + volname
    status = run_helper.run_command(mgmt_node, vol_start_cmd, True)
    if status:
        print 'volume starting failed.'

    return status




def main():

    start = True
    args = sys.argv[1:]
    if not args:
        start = False
    else:
        if args[0] != '--start-vol':
            start = False

    status = create_gluster_volume()
    if status:
        print 'Exiting...'
        sys.exit(1)
    
    if start:
        status = start_gluster_volume()
        if status:
            print 'Exiting...'
            sys.exit(1)

    return status

if __name__ == '__main__':
    main()
