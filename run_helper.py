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
            print 'node: ' + node + '\ncommand: ' + cmd + '\n' + 'exit status: ' + ret_code + '\n' + fout.read() + '\n' + ferr.read()
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
