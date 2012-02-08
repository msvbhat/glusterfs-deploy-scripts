#!/usr/bin/python

import sys, os
import re
import paramiko
import getopt



def read_config_file():
    global rh_config_dict

    rh_config_dict = {}
    f = open('configfile', 'r')
    for line in f.readlines():
        match = re.search(r'([\w]+)="([^"]+)"', line)
        if  match:
            key = match.group(1)
            value = match.group(2)
            rh_config_dict[key] = value
    f.close()
    return None



def usage():
    print 'Usage: run_helper.py {[-c "file to be copied:path in destination machine"] [-r "command to be run"]}'
    return 0

#get the ip address of the nodes from the config file 
def get_nodes_ip():
    try:
        servers = rh_config_dict['SERVER_IP_ADDRS']
    except:
        print 'unable to retrive the server ip address from configfile. Please set SERVERS_IP_ADDRS in configfile'
        sys.exit(1)

    server_set = set([])
    for server in servers.split(','):
        server_set.add(server)

    return list(server_set)


#get the client ip
def get_client_ip():
    try:
        clients = rh_config_dict['CLIENT_IP_ADDRS']
    except:
        print 'unable to find client IP address. Please set CLIENT_IP_ADDRS in configfile'
        sys.exit(1)

    clients_set = set([])
    for client in clients.split(','):
        clients_set.add(client)

    return list(clients_set)


#get the prefix path to install gluster
def get_prefix_path():
    try:
        prefix_path = rh_config_dict['PREFIX_PATH']
    except:
        prefix_path = ''

    return prefix_path



#get management node ip
def get_mgmt_node():
    try:
        mgmt_node = rh_config_dict['MGMT_NODE']
    except:
        mgmt_node = None

    return mgmt_node


#get the version of glusterfs
def get_gluster_version():
    try:
        tarball = rh_config_dict['GLUSTER_VERSION']
    except:
        print 'Unable to find the gluster version. Please set the GLUSTER_VERSION in config file'
        sys.exit(1)

    return tarball


def get_git_repo():
    try:
        git_repo = rh_config_dict['GIT_REPO']
    except:
        print 'Unable to find the git repo. Please set the GIT_REPO in configfile'
        sys.exit(1)

    return git_repo



def get_build_dir():
    invalid_build_dir = ['/', '//', '/root', '/root/', '/usr', '/usr/', '/etc', '/etc/', '/sbin', '/sbin/', '/boot', '/boot/', '/opt', '/opt/', '/var', '/var/', '/bin', '/bin/']

    try:
        build_dir = rh_config_dict['NODE_BUILD_DIR']
        if build_dir in invalid_build_dir:
            print build_dir + ' can not be build directory. Using /tmp/build-dir as build directory'
            build_dir = '/tmp/build-dir'
    except:
        print 'Unable to find the build directory. Using /tmp/build-dir as build directory'
        build_dir = '/tmp/build-dir'

    return build_dir



def get_server_export_dir():
    try:
        export_dir = rh_config_dict['SERVER_EXPORT_DIR']
    except:
        print 'Unable to find the server export directory. Please set SERVER_EXPORT_DIR in configfile'
        sys.exit(1)

    if export_dir[-1] == '/':
        export_dir = export_dir[:-1]
    invalid_export_dir = ['/', '//', '/root', '/root/', '/usr', '/usr/', '/etc', '/etc/', '/sbin', '/sbin/', '/boot', '/boot/', '/opt', '/opt/', '/var', '/var/', '/bin', '/bin/']
    if export_dir in invalid_export_dir:
        print export_dir + ' can NOT be the server export directory. Please give other valid directory'
        sys.exit(1)

    return export_dir



def get_volume_type():
    try:
        vol_type = rh_config_dict['VOL_TYPE']
    except:
        print 'Unable to find the gluster volume type. Please set the VOL_TYPE in configfile to proper gluster volume type'
        sys.exit(1)

    supported_vol_types = ['dist', 'rep', 'stripe', 'dist-rep', 'stripe-rep', 'dist-stripe-rep', 'dist-stripe']
    if vol_type not in supported_vol_types:
        print vol_type + ' is not a supported gluster volume type. Please set the proper volume type'
        sys.exit(1)

    return vol_type


def get_vol_name():
    try:
        volname = rh_config_dict['VOLNAME']
    except:
        print 'Unable to find the volume name. Please set VOLNAME in configfile'
        sys.exit(1)

    return volname





def get_number_of_bricks():
    try:
        no_of_bricks = rh_config_dict['NO_OF_BRICKS']
    except:
        print 'Unable to get the number of bricks for volume. Please set NO_OF_BRICKS in configfile to proper value and retry'
        sys.exit(1)

    return no_of_bricks




def get_replica_count():
    try:
        replica_count = rh_config_dict['REPLICA_COUNT']
    except:
        print 'Unable to find the replica count. Please set the REPLICA_COUNT in configfile'
        sys.exit(1)

    return replica_count



def get_stripe_count():
    try:
        stripe_count = rh_config_dict['STRIPE_COUNT']
    except:
        print 'Unable to find the stripe count. Please set the STRIPE_COUNT in configfile'
        sys.exit(1)

    return stripe_count



def get_trans_type():
    try:
        trans_type = rh_config_dict['TRANS_TYPE']
    except:
        print 'Unable to find the transport type. Please set the TRANS_TYPE in configfile to proper supported transport type'
        sys.exit(1)

    supported_trans_types = ['tcp', 'rdma', 'tcp,rdma']
    if trans_type not in supported_trans_types:
        print trans_type + ' is not a supported transport type. Please set the proper supported transport type'
        sys.exit(1)

    return trans_type



def get_mountpoint():
    try:
        mountpoint = rh_config_dict['MOUNTPOINT']
    except:
        print 'unable to find the mount point. Please set the MOUNTPOINT in configfile'
        sys.exit(1)

    invalid_mountpoints = ['/', '//', '/root', '/root/', '/usr', '/usr/', '/etc', '/etc/', '/sbin', '/sbin/', '/boot', '/boot/', '/opt', '/opt/', '/var', '/var/', '/bin', '/bin/']
    if mountpoint in invalid_mountpoints:
        print mountpoint + ' is not a valid mountpoint. Please provide a valid mountpoint. Aborting...'
        sys.exit(1)

    if mountpoint[-1] == '/':
        mountpoint = mountpoint[:-1]

    return mountpoint



def get_mount_type():
    try:
        mount_type = rh_config_dict['MOUNT_TYPE']
    except:
        print 'unable to find the valid mount type. Please set MOUNT_TYPE in configfile'
        sys.exit(1)

    return mount_type



def get_log_archive_dir():
    try:
        log_archive = rh_config_dict['LOG_ARCHIVE']
    except:
        print 'LOG_ARCHIVE is not set in configfile. Using "/tmp/sanity-run" as deafult log dir'
        log_archive = '/tmp/sanity-run'

    return log_archive




def get_send_mail_path():
    try:
        email_path = rh_config_dict['EMAIL']
    except:
        print 'EMAIL is not set in configfile. Not sending the results, just archiving'
        email_path = None

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

    nodes = get_nodes_ip()

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


read_config_file()
if __name__ == '__main__':
    main()
