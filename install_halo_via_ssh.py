### Install_halo_via_ssh.py expects to input 'server_list.txt' from the same directory,
### unless a different file is supplied as an arg.  Each line in server_list.txt should
### contain 3 values:  ip_address user pwd
###
### Note: More error checking should be done for bad/down servers.

import paramiko, argparse, csv, time, sys

def install_halo(host, id, password, keypair):
    i = 1
    while 1 < 30 :
      if args.debug: print ("Trying to connect to %s (%i/30)" % (host, i))

      try: 
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=id, password=password, key_filename=keypair)
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

    # Sudo on the remote server
    a, b, c = ssh.exec_command('sudo su')

    # Identify which package manager is installed on the remote system
    a, b, c = ssh.exec_command('which apt-get')
    pkg_manager =  b.readlines()[0]
    if args.debug: print "Package manager is: ", pkg_manager

    # Install Halo
    if "apt-get" in pkg_manager:
      a, b, c = ssh.exec_command("echo 'deb http://packages.cloudpassage.com/debian debian main' | sudo tee /etc/apt/sources.list.d/cloudpassage.list > /dev/null \n")
      if args.debug: print "DEBUG echo (expecting empty set) : \n" + str(b.readlines()) + "\n"
      a, b, c = ssh.exec_command("sudo apt-get -y install curl \n")
      if args.debug: print "DEBUG installing curl : \n" + str(b.readlines()) + "\n"
      a, b, c = ssh.exec_command("curl http://packages.cloudpassage.com/cloudpassage.packages.key | sudo apt-key add -") 
      if args.debug: print "DEBUG curl (expecting OK): \n" + str(b.readlines()) + "\n"
      a, b, c = ssh.exec_command("sudo apt-get update > /dev/null \n")
      if args.debug: print "DEBUG update (expecting empty set) : \n" + str(b.readlines()) + "\n"
      a, b, c = ssh.exec_command("sudo apt-get -y install cphalo \n")
      if args.debug: print "DEBUG sudo apt-get -y install Halo \n" + str(b.readlines()) + "\n"
    elif "yum" in pkg_manager:
      a, b, c = ssh.exec_command("echo -e '[cloudpassage]\nname=CloudPassage\nbaseurl=http://packages.cloudpassage.com/redhat/$basearch\ngpgcheck=1' | tee /etc/yum.repos.d/cloudpassage.repo > /dev/null \n")
      if args.debug: print "DEBUG echo: \n" + str(b.readlines()) + "\n"
      a, b, c = ssh.exec_command("rpm --import http://packages.cloudpassage.com/cloudpassage.packages.key")
      if args.debug: print "DEBUG rpm: \n" + str(b.readlines()) + "\n"
      a, b, c = ssh.exec_command("yum check-update > /dev/null")
      if args.debug: print "DEBUG yum check-update: \n" + str(b.readlines()) + "\n"
      a, b, c = ssh.exec_command("yum -y install cphalo")
      if args.debug: print "DEBUG yum install Halo: \n" + str(b.readlines()) + "\n"

    cmd = "sudo /etc/init.d/cphalod start --daemon-key=" + args.daemon_key + " --tag=" + args.tag + " --server-label=" + args.server_label + "\n"
    a, b, c = ssh.exec_command(cmd)
    if args.debug: print "DEBUG sudo /etc/init.d/cphalod start --daemon-key=" + args.daemon_key + "\n(expecting empty set) : \n" + str(b.readlines()) + "\n"
    return True #Add error handling later

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
parser.add_argument('--debug', '-d', action='store_true', default=False,
                    help='[CoOlNiCk] It will enable debug mode while executing the script')
args = parser.parse_args()

server_list = list(csv.reader(open(args.input, 'rb'), delimiter=' ', skipinitialspace=True))

success_buffer =''
error_buffer =''
for server in server_list:
    host = server[0]
    id = server[1]
    password = server[2]
    if args.keypair == None and len(server) > 3:
        keypair = server[3]
    else:
        keypair = args.keypair
    if args.debug:
        print ('Server IP: %s\nLogin ID: %s\nLogin Password: %s\nKeypair: %s\n' % (host, id, password, keypair))

    success = install_halo(host, id, password, keypair)
    if success:  
        success_buffer += "\n[" + host + ']\n'
    else:   
        error_buffer += "\n[" + host + ']\n'

if args.debug: 
    if success_buffer:
        print ("### Halo is installed on these servers: %s" % success_buffer)###")
    if error_buffer:
        print ("\n\n### ERROR installing Halo on these servers: %s" % success_buffer)###")        
    print ("### END install_halo_via_ssh  ###")

############## NOTE TO FUTURE DEVELOPER/TEST/QA:
############## THIS CODE NEEDS ERROR CHECKING ON BAD/DOWN SERVERS
