#!/usr/bin/python

import sys, os
import shlex, shutil
import subprocess
import re
import paramiko
import run_helper
import threading
import Queue
import getopt
import commands
import install_gluster_rpm



def usage():
    print './deploy_gluster [-g <git-branch> or --git <git-branch> | -t  or --tarball | -r or --rpm]'

    return None


def prepare_git_source(branch):
    git_repo = run_helper.get_git_repo()
    if git_repo[-1] == '/':
        git_repo = git_repo[:-1]

    target_dict = {'master' : '3git', 'release-3.2' : '3.2git'}
    target = target_dict[branch]
    print 'checking out glusterfs branch "' + branch + '"...'
    status, output = commands.getstatusoutput('cd ' + git_repo + ' && git checkout ' + branch)
    if status:
        print output
        sys.exit(1)

    print 'updating the repo to current head (git pull)...'
    status, output = commands.getstatusoutput('cd ' + git_repo + ' && git pull')
    if status:
        print output
        sys.exit(1)

    status, git_head = commands.getstatusoutput('cd ' + git_repo + ' && git show --pretty="%H" -s')
    print 'removing old tarballs if any...'
    os.system('rm -f ' + git_repo + '/glusterfs*.tar.gz')

    print 'autogen and configuring for make dist...'
    status, output = commands.getstatusoutput('cd ' + git_repo + ' && ./autogen.sh && ./configure --enable-fusermount')
    if status:
        print output
        sys.exit(1)

    print 'running make dist...'
    status, output = commands.getstatusoutput('cd ' + git_repo + ' && make dist')
    if status:
        print output
        sys.exit(1)

    print 'copying the genarated tar ball to cwd...'
    shutil.copy(git_repo + '/glusterfs-' + target + '.tar.gz', '.')

    print 'successfully created tarball from git repo...'

    return ('glusterfs-' + target + '.tar.gz', git_head)




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


def real_install_gluster(node, tarball, build_dir, prefix_path, ret_queue):
        match = re.search(r'([\w.-]+).tar.gz', tarball)
        target_dir = match.group(1)

        run_helper.run_command(node, 'rm -rf ' + build_dir + target_dir + '*', False)
        run_helper.run_command(node, 'mkdir -p ' + build_dir, False)
        run_helper.rcopy(node, tarball, build_dir, False)
        run_helper.run_command(node, 'cd ' + build_dir + ' && tar -xzf ' + tarball, False)
        run_helper.rcopy(node, 'buildit.sh', build_dir + target_dir, False)
        print 'build started on ' + node
        exit_status = run_helper.run_command(node, 'cd ' + build_dir + target_dir + ' && ./buildit.sh ' + prefix_path, False)

        check_exit_status(node, exit_status)
        ret_queue.put(exit_status)

        return 0



def install_gluster(tarball):
    nodes = run_helper.get_nodes_ip()

    clients = run_helper.get_client_ip()
    for client in clients:
        if client not in nodes:
            nodes.append(client)

    if not os.path.exists(tarball):
        print 'INFO: Source tarball ' + tarball + ' doesn\'t exist. Proceeding to download from bits.gluster.com'
        download_url = 'http://bits.gluster.com/pub/gluster/glusterfs/src/' + tarball
        cmd = 'wget ' +  download_url
        wget_status = os.system(cmd)
        if wget_status:
            print 'unable to download ' + tarball + ' from bits.gluster.com, \n Exiting...'
            sys.exit(1)

    prefix_path = run_helper.get_prefix_path()

    build_dir = run_helper.get_build_dir()
    if build_dir[-1] != '/':
        build_dir = build_dir + '/'

    ret_queue = Queue.Queue()
    threads = []
    for node in nodes:
        t = threading.Thread(target=real_install_gluster, args=(node, tarball, build_dir, prefix_path, ret_queue))
        t.start()
        threads.append(t)

    ret_codes = []
    for t in threads:
        t.join()
        ret_codes.append(ret_queue.get())

    return_value = 0
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



def get_options(args):
    opt = arg = []
    try:
        opt, arg = getopt.getopt(args, "g:rt", ["git=", "tar", "rpm"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)

    installation_way = None
    branch = None
    for k, v in opt:
        if k in ("-g", "--git"):
            installation_way = "git"
            branch = v
        elif k in ("-t", "--tar"):
            installation_way = "tarball"
        elif k in ("-r", "--rpm"):
            installation_way = "rpm"
        else:
            assert False, "unhandled option"
            usage()

    return (installation_way, branch)





if __name__ == '__main__':
    installation_way, branch = get_options(sys.argv[1:])
    if installation_way == "git":
        git_branches = ['master', 'release-3.2']
        if branch not in git_branches:
            print '"' + branch + '"  is not a proper git branch. Please specify a proper git branch'
            sys.exit(1)
        print 'installing from git source...'
        tarball, git_head = prepare_git_source(branch)
        install_status = install_gluster(tarball)
    elif installation_way == "tarball":
        print 'installing from tarball...'
        install_status = main_installer()
    elif installation_way == "rpm":
        print 'installing from rpms...'
        print 'WARNING: There are some known issues with this option. Please try',
        print 'downloading the rpms and using run_helper.py to install rpms, ',
        print 'should you encounter the error.'
        rpms = ['core', 'fuse', 'geo-replication']
        install_status = install_gluster_rpm.install_gluster_rpms(rpms)
    else:
        print 'unhandled option'
        usage()
        sys.exit(1)

    if install_status:
        print 'Installation FAILED. Please look into it'
        sys.exit(1)
