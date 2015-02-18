#!/usr/bin/env python

# __author__ = 'nick'

# you need paramiko module for this to run
# pip install paramiko

import paramiko, argparse, csv, time
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', action='store', default='./server_list.txt',
                    help='file path & name for server list')
parser.add_argument('--keypair', '-k', action='store', default='/home/f/.ssh/id_rsa',
                    help='Keypair for SSH. WARNING! This will overwrite any keypair name from the input file')
parser.add_argument('--daemon_key', action='store', default='',
                    help='HALO daemon key for registration')
parser.add_argument('--tag', '-t', action='store', default='',
                    help='HALO server group tag for registration')
parser.add_argument('--server_label', '-s', action='store', default='',
                    help='Server label for registration')
parser.add_argument('--debug', '-d', action='store_true', default=True,
                    help='[CoOlNiCk] It will enable debug mode while executing the script')
args = parser.parse_args()

server_list = list(csv.reader(open(args.input, 'rb'), delimiter=' ', skipinitialspace=True))

def install_halo_debian(ip, id, password, keypair, terminal_buffer):
    terminal_buffer += "\n[" + ip + ']\n'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=id, password=password, key_filename=keypair)

    chan = ssh.invoke_shell()
    temp_buffer = ''

    time.sleep(3)
    chan.send('sudo su - \n')
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer
    
    print temp_buffer  #get the last line.  that will be the prompt.

    time.sleep(1)
    chan.send("echo 'deb http://packages.cloudpassage.com/debian debian main' | sudo tee /etc/apt/sources.list.d/cloudpassage.list > /dev/null \n")
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer
    #check_lastLine(buffer) is last line of buffer the prompt?

    time.sleep(3)
    chan.send("sudo apt-get -y install curl \n")
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(4)
    chan.send("\n curl http://packages.cloudpassage.com/cloudpassage.packages.key | sudo apt-key add -")
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(4)
    chan.send("\n sudo apt-get update > /dev/null \n")
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(4)
    chan.send("\n sudo apt-get -y install cphalo \n") 
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(50)
    cmd = "\n sudo /etc/init.d/cphalod restart --daemon-key=" + args.daemon_key + " --tag=" + args.tag + " --server-label=" + args.server_label + " \n\n\n"
    chan.send(cmd)
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(50)
    chan.send("\n\n")
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    terminal_buffer += temp_buffer
    terminal_buffer += "\n================================================================"
    ssh.close()

    return terminal_buffer

def install_halo_centos(ip, id, password, keypair, terminal_buffer):
    terminal_buffer += "\n[" + ip + ']\n'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=id, password=password, key_filename=keypair)

    chan = ssh.invoke_shell()
    temp_buffer = ''

    time.sleep(3)
    chan.send('sudo su - \n')
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(1)
    chan.send("echo -e '[cloudpassage]\nname=CloudPassage\nbaseurl=http://packages.cloudpassage.com/redhat/$basearch\ngpgcheck=1' | tee /etc/yum.repos.d/cloudpassage.repo > /dev/null \n")
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(3)
    chan.send('rpm --import http://packages.cloudpassage.com/cloudpassage.packages.key \n')
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(1)
    chan.send("\n yum check-update > /dev/null \n")
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(1)
    chan.send("\n yum -y install cphalo \n")
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(1)
    cmd = "\n /etc/init.d/cphalod restart --daemon-key=" + args.daemon_key + " --tag=" + args.tag + " --server-label=" + args.server_label + " \n\n\n"
    chan.send(cmd)
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    time.sleep(5)
    chan.send("\n\n")
    buffer = chan.recv(9999)
    if args.debug: print ("%s\n" % buffer)
    temp_buffer += buffer

    terminal_buffer += temp_buffer
    terminal_buffer += "\n================================================================"
    ssh.close()

    return terminal_buffer

terminal_buffer =''

for server in server_list:
    ip = server[0]
    id = server[1]
    password = server[2]
    if args.keypair == None and len(server) > 3:
        keypair = server[3]
    else:
        keypair = args.keypair
    if args.debug:
        print ('Server IP: %s\nLogin ID: %s\nLogin Password: %s\nKeypair: %s\n' % (ip, id, password, keypair))

    isDebian = subprocess.Popen("which apt-get", stdout=subprocess.PIPE, shell=True).stdout.read()
    isDebian = isDebian.replace("\n","")
    if isDebian == '/usr/bin/apt-get':
        print "package manager is apt-get"
        terminal_buffer = install_halo_debian(ip, id, password, keypair, terminal_buffer)
    else:
        isCentOS = subprocess.Popen("which yum", stdout=subprocess.PIPE, shell=True).stdout.read()
        isCentOS = isDebian.replace("\n","")
        print isCentos         #remove later, then fill in line below
        if isCentOS == 'yum':  #expand this...
            print "package manager is yum"
            terminal_buffer = install_halo_centos(ip, id, password, keypair, terminal_buffer)
        else:
            print "package manager not identified..."

print ("\n#################################################################################\n%s" % terminal_buffer)
