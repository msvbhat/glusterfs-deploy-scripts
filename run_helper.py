#!/usr/bin/python

import sys, os
import re
import paramiko
import getopt


def usage():
    print 'Usage: run_helper.py {[-c "file to be copied:path in destination machine"] [-r "command to be run"]}'
    return 0

#get the ip address of the nodes from the config file 
def get_nodes_ip():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()
    match = re.search(r'SERVER_IP_ADDRS="([\w.,-]+)"', configtext)
    if not match:
        print 'unable to find the ip addresses of the machines'
        sys.exit(1)

    nodes = match.group(1).split(',')

    return nodes


#get the client ip
def get_client_ip():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()
    match = re.search(r'CLIENT_IP_ADDRS="([\w.,-]+)"', configtext)
    if not match:
        print 'unable to find client IP address. Please set CLIENT_IP_ADDRS'
        sys.exit(1)

    clients = match.group(1).split(',')

    return clients


#get management node ip
def get_mgmt_node():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()

    match = re.search(r'MGMT_NODE="([\w.-]+)"', configtext)
    if not match:
        print 'Unable to find the management node. Please set the MGMT_NODE in configfile'
        sys.exit(1)

    return match.group(1)


#get the version of glusterfs
def get_gluster_version():
    fc = open('configfile', 'r')
    configtext = fc.read()
    fc.close()

    tarball_match = re.search(r'GLUSTER_VERSION="(glusterfs-[\w.]+)"', configtext)
    if not tarball_match:
        print 'Unable to find the gluster version. Please set the GLUSTER_VERSION in config file'
        sys.exit(1)

    tarball = tarball_match.group(1)

    return tarball


def get_git_repo():
    f = open('configfile', 'r')
    configtext =f.read()
    f.close()

    match = re.search(r'GIT_REPO="(\S+)"', configtext)
    if not match:
        print 'Unable to find the git repo. Please set the GIT_REPO in configfile'
        sys.exit(1)

    return match.group(1)



def get_build_dir():
    fc = open('configfile' , 'r')
    configtext = fc.read()
    fc.close()

    match = re.search(r'NODE_BUILD_DIR="(\S+)"', configtext)
    if not match:
        print 'Unable to find the build directory. Please set the proper NODE_BUILD_DIR in the config file'
        sys.exit(1)

    return match.group(1)



def get_server_export_dir():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()

    match = re.search(r'SERVER_EXPORT_DIR="(\S+)"', configtext)
    if not match:
        print 'Unable to find the server export directory. Please set SERVER_EXPORT_DIR in configfile'
        sys.exit(1)

    export_dir = match.group(1)
    invalid_export_dir = ['/', '//', '/root', '/root/', '/usr', '/usr/', '/etc', '/etc/', '/sbin', '/sbin/', '/boot', '/boot/', '/opt', '/opt/']
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



def get_mountpoint():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()
    match = re.search(r'MOUNTPOINT="(\S+)"', configtext)
    if not match:
        print 'unable to find the mount point'
        sys.exit(1)

    mountpoint = match.group(1)
    invalid_mountpoints = ['/', '//', '/root', '/root/', '/usr', '/usr/', '/etc', '/etc/', '/sbin', '/sbin/', '/boot', '/boot/', '/opt', '/opt/']
    if mountpoint in invalid_mountpoints:
        print mountpoint + ' is not a valid mountpoint. Please provide a valid mountpoint. Aborting...'
        sys.exit(1)

    return mountpoint



def get_mount_type():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()
    match = re.search(r'MOUNT_TYPE="(\w+)"', configtext)
    if not match:
        print 'unable to find the valid mount type. Please specify the mount type in configfile'
        sys.exit(1)

    return match.group(1)



def get_log_archive_dir():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()
    match = re.search(r'LOG_ARCHIVE="(\S+)"', configtext)
    if match:
        log_archive = match.group(1)
    else:
        print 'LOG_ARCHIVE is not set in configfile. Using "/tmp/sanity-run" as deafult log dir'
        log_archive = '/tmp/sanity-run'

    return log_archive




def get_send_mail_path():
    f = open('configfile', 'r')
    configtext = f.read()
    f.close()
    match = re.search(r'EMAIL="(\S+)"', configtext)
    if not match:
        print 'EMAIL is not set in configfile. Not sending the results, just archiving'
        email_path = None
    else:
        email_path = match.group(1)

    return email_path







#run commands in the remote machine
def run_command(node, cmd, verbose):

        ssh_handle = paramiko.SSHClient()
        ssh_handle.load_system_host_keys()
        ssh_handle.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_handle.connect(node, username='root', password='')
        chan = ssh_handle.get_transport().open_session()
        try:
            chan.exec_command(cmd)
        except:
            print 'unable to excecute the command ' + cmd + ' on the remote server ' + node

        fout = chan.makefile('rb')
        ferr = chan.makefile_stderr('rb')
        ret_code = chan.recv_exit_status()
        if verbose == True:
            print 'node: ' + node + '\ncommand: ' + cmd + '\n' + 'exit status: %d' % ret_code + '\n' + fout.read() + '\n' + ferr.read()
            print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
            print '\n\n'
        ssh_handle.close()

        return ret_code

#NOTE: I'm not sure how mush of above code is robust. Because if the remote machine sends back enough data to fill the buffer of 'channel file object' then,
#      host (this machine) may hang forever. Need a better way to handle this issue. Current code just assumes that the remote machine doesn't send lot of data.


#Do scp to node machine using scp command
def rcopy(node, srcfile, destpath, verbose):
        if verbose == True:
            print '>>>>>>>>>>>>>>>>>>> doing remote copy to host ' + node + ' <<<<<<<<<<<<<<<<<<<<<<'
        scpcmd = 'scp ' + srcfile + ' ' + node + ':' + destpath
        if verbose == True:
            print scpcmd
        try:
            if verbose == True:
                os.system(scpcmd)
            else:
                os.system(scpcmd + '> /dev/null 2>&1')
        except:
            print scpcmd + ' failed'

        if verbose == True:
            print '\n\n'

        return None



def main():
    opt = arg = []
    try:
        opt, arg = getopt.getopt(sys.argv[1:], "c:r:C:R:", ["copy=", "run=", "Run=", "Copy="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)

    scpsend = remoterun = in_all_machines = None
    for k, v in opt:
        if k in ("-c", "--copy"):
            scpsend = True
            filepath = v.split(':')
        elif k in ("-C", "--Copy"):
            scpsend = True
            filepath = v.split(':')
            in_all_machines = True
        elif k in ("-r", "--run"):
            remoterun = True
            cmd = v
        elif k in ("-R", "--Run"):
            remoterun = True
            cmd = v
            in_all_machines = True
        else:
            assert False, "unhandled option"

    if scpsend == True:
        sfile = filepath[0]
        destpath = filepath[1]

    all_nodes = get_nodes_ip()
    nodes = []
    for node in all_nodes:
        if node not in nodes:
            nodes.append(node)

    if in_all_machines == True:
        client_ips = get_client_ip()
        for client_ip in client_ips:
            if client_ip not in nodes:
                nodes.append(client_ip)

    if remoterun == True:
        for node in nodes:
            run_command(node, cmd, True)

    if scpsend == True:
        for node in nodes:
            rcopy(node, sfile, destpath, True)

    if not scpsend and not remoterun:
        print 'option unhandled. Please execute with proper option'
        usage()
        sys.exit(1)

    return 0


if __name__ == '__main__':
    main()
