import paramiko, argparse, csv, time, sys

def remove_halo(host, id, password, keypair):
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

    # Remove Halo
    if "apt-get" in pkg_manager:
      a, b, c = ssh.exec_command("sudo apt-get purge cphalo\n")
    elif "yum" in pkg_manager:
      a, b, c = ssh.exec_command("sudo yum remove cphalo")

    return # Add Error Checking later


### Begin Execution ###

parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', action='store', default='./server_list.txt',
                    help='file path & name for server list')
parser.add_argument('--keypair', '-k', action='store', default='/home/f/.ssh/id_rsa',
                    help='Keypair for SSH. WARNING! This will overwrite any keypair name from the input file')
parser.add_argument('--debug', '-d', action='store_true', default=False,
                    help='Enable debug mode while executing the script')
args = parser.parse_args()

server_list = list(csv.reader(open(args.input, 'rb'), delimiter=' ', skipinitialspace=True))

terminal_buffer =''
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

    remove_halo(host, id, password, keypair)
    terminal_buffer += "[" + host + ']\n'

if args.debug: 
    print ("### Halo is no longer on these servers:\n%s" % terminal_buffer)
    print ("### END remove_halo_via_ssh ###")
