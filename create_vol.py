#!/usr/bin/python

import os, sys
import re
import run_helper




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

        cmd = 'rm -f /usr/local/var/log/glusterfs/.c*'
        run_helper.run_command(node, cmd, False)


        cmd = 'rm -rf /var/log/glusterfs/*'
        run_helper.run_command(node, cmd, False)

        cmd = 'rm -f /var/log/glusterfs/.c*'
        run_helper.run_command(node, cmd, False)

    return 0


def create_gluster_volume():
    mgmt_node = run_helper.get_mgmt_node()
    nodes = run_helper.get_nodes_ip()
    if mgmt_node not in nodes:
        print 'management node MUST be part of the server nodes'
        sys.exit(1)

    export_dir = run_helper.get_server_export_dir()
    vol_type = run_helper.get_volume_type()
    trans_type = run_helper.get_trans_type()
    volname = run_helper.get_vol_name()

    pre_create_cleanup(nodes, export_dir)

    brick_list = ''
    for node in nodes:
        brick_list =  brick_list + node + ':' + export_dir + ' '

    replica_count = ''
    if vol_type == 'dist-rep' or vol_type == 'stripe-rep' or vol_type == 'rep' or vol_type == 'dist-stripe-rep':
        replica_count = 'replica ' + run_helper.get_replica_count()

    stripe_count = ''
    if vol_type == 'stripe' or vol_type == 'stripe-rep' or vol_type == 'dist-stripe-rep' or vol_type == 'dist-stripe':
        stripe_count = 'stripe ' + run_helper.get_stripe_count()

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
    volname = run_helper.get_vol_name()
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
