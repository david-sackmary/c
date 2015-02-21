import paramiko, argparse, csv, time, sys

def install_halo(host, id, password, keypair, terminal_buffer):

    terminal_buffer += "\n[" + ip + ']\n'

    i = 1
    while 1 < 30 :
      if args.debug: print ("Trying to connect to %s (%i/30)" % (host, i))

      try: 
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=id, password=password, key_filename=keypair)
        if args.debug: print "Connected to %s" % host
        break
      except paramiko.AuthenticationException:
        print "Authentication failed when connecting to %s" % host
        sys.exit(1)
      except:
        print "Could not SSH to %s, waiting for it to start" % host
        i += 1
        time.sleep(2)

    # If we could not connect within time limit
    if i == 30:
      print "Could not connect to %s. Giving up" % host
      sys.exit(1)

    # Get sudo or error out
    a, b, c = ssh.exec_command('sudo su')
    if args.debug: print b.readlines()

    # Identify which package manager is installed on the remote system
    a, b, c = ssh.exec_command('which apt-get')
    pkg_manager =  b.readlines()[0]
    if args.debug: print "Package manager is: ", pkg_manager

    # Install Halo or error trying
    if "apt-get" in pkg_manager:
      a, b, c = ssh.exec_command("echo 'deb http://packages.cloudpassage.com/debian debian main' | sudo tee /etc/apt/sources.list.d/cloudpassage.list > /dev/null \n")
      if args.debug: print b.readlines()
      a, b, c = ssh.exec_command("sudo apt-get -y install curl \n")
      if args.debug: print b.readlines()
      a, b, c = ssh.exec_command("curl http://packages.cloudpassage.com/cloudpassage.packages.key | sudo apt-key add -") 
      if args.debug: print b.readlines()
      a, b, c = ssh.exec_command("sudo apt-get update > /dev/null \n")
      if args.debug: print b.readlines()
      a, b, c = ssh.exec_command("sudo apt-get -y install cphalo \n")
      if args.debug: print b.readlines()
    elif "yum" in pkg_manager:
      a, b, c = ssh.exec_command("echo -e '[cloudpassage]\nname=CloudPassage\nbaseurl=http://packages.cloudpassage.com/redhat/$basearch\ngpgcheck=1' | tee /etc/yum.repos.d/cloudpassage.repo > /dev/null \n")
      if args.debug: print b.readlines()
      a, b, c = ssh.exec_command("rpm --import http://packages.cloudpassage.com/cloudpassage.packages.key")
      if args.debug: print b.readlines()
      a, b, c = ssh.exec_command("yum check-update > /dev/null")
      if args.debug: print b.readlines()
      a, b, c = ssh.exec_command("yum -y install cphalo")
      if args.debug: print b.readlines()

    cmd = "/etc/init.d/cphalod restart --daemon-key=" + args.daemon_key + " --tag=" + args.tag + " --server-label=" + args.server_label + "\n"
    a, b, c = ssh.exec_command(cmd)
    if args.debug: print b.readlines()

    return terminal_buffer


### Begin Execution ###

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

    terminal_buffer = install_halo(ip, id, password, keypair, terminal_buffer)

print ("\n############################################################################\n%s" % terminal_buffer)
