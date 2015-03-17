### Get_iptables.py 
### INPUT: 'server_list.txt' from the same directory,
###         unless a different file is supplied as an arg.  
###         Each line in server_list.txt should contain 3 values:  
###         ip_address user pwd
### OUTPUT: A set of files in the same directory.
###         Each is named by the ip_address of its' corresponding line.
###       
### Note: More error checking should be done for bad/down servers.

import paramiko, argparse, csv, time, sys

def paramiko_with_ssh(host, id, password, keypair):
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

    a, b, c = ssh.exec_command('sudo iptables -L -v -n')
    ip_tables =  b.readlines()[0]
    if args.debug: print "ip_tables is: ", ip_tables

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

    success = paramiko_with_ssh(host, id, password, keypair)
    if success:  
        success_buffer += "\n[" + host + ']\n'
    else:   
        error_buffer += "\n[" + host + ']\n'

if args.debug: 
    if success_buffer:
        print ("### Processed Iptables from these servers: %s" % success_buffer)###")
    if error_buffer:
        print ("\n\n### ERROR getting Iptables from these servers: %s" % error_buffer)###")        
    print ("### END get_iptables.py  ###")

############## NOTE TO FUTURE DEVELOPER/TEST/QA:
############## THIS CODE NEEDS ERROR CHECKING ON BAD/DOWN SERVERS
