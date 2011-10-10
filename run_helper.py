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
    match = re.search(r'NODES_IP_ADDRS="([\w.,-]+)"', configtext)
    if not match:
        print 'unable to find the ip addresses of the machines'
        sys.exit(1)

    nodes = match.group(1).split(',')

    return nodes

#run commands in the remote machine
def run_command(node, cmd, verbose):

        if verbose == True:
            print '>>>>>>>>>>>>>>> executing command "' + cmd + '" on remote machine "' + node + '" <<<<<<<<<<<<<<<<<<<<<<<'
        ssh_handle = paramiko.SSHClient()
        ssh_handle.load_system_host_keys()
        ssh_handle.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_handle.connect(node, username='root', password='')
        try:
            (fin, fout, ferr) = ssh_handle.exec_command(cmd)
        except:
            print 'unable to excecute the command ' + cmd + ' on the remote server ' + node

        if verbose == True:
            print 'output:'
            print fout.read()
            print 'error:'
            print ferr.read()
            print '\n\n'
        ssh_handle.close()

        return None

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
        opt, arg = getopt.getopt(sys.argv[1:], "c:r:", ["copy=", "run="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)

    scpsend = remoterun = None
    for k, v in opt:
        if k in ("-c", "--copy"):
            scpsend = True
            filepath = v.split(':')
            sfile = filepath[0]
            destpath = filepath[1]
        elif k in ("-r", "--run"):
            remoterun = True
            cmd = v
        else:
            assert False, "unhandled option"


    if remoterun == True:
        nodes = get_nodes_ip()
        for node in nodes:
            run_command(node, cmd, True)

    if scpsend == True:
        nodes = get_nodes_ip()
        for node in nodes:
            rcopy(node, sfile, destpath, True)

    if not scpsend and not remoterun:
        print 'option unhandled. Please execute with proper option'
        usage()
        sys.exit(1)

    return 0


if __name__ == '__main__':
    main()
