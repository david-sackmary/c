### Get_iptables.py 
### INPUT: 'server_list.txt' from the same directory,
###         unless a different file is supplied as an arg.  
###         Each line in server_list.txt should contain 3 values:  
###         ip_address user pwd
### OUTPUT: A set of files in the same directory.
###         Each is named by the ip_address of its' corresponding line.
###       
### Note: More error checking should be done for bad/down servers.

import paramiko, argparse, csv

def get_Iptables(host, id, password):
    trans = paramiko.Transport((host, 22))
    trans.connect(username=id, password=password)
    session = trans.open_channel("session")
    session.exec_command('sudo iptables -L -v -n')
    session.recv_exit_status()
    while session.recv_ready():
        return session.recv(20000)

### Begin Execution ###
parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', action='store', default='./server_list.txt',
                    help='File path & name for server list')
args = parser.parse_args()
args.debug = False
server_list = list(csv.reader(open(args.input, 'rb'), delimiter=' ', skipinitialspace=True))
for server in server_list:
    host = server[0]
    id = server[1]
    password = server[2]

    iptables = get_Iptables(host, id, password)
    outfile = host + ".iptables"
    file = open(outfile,"w")
    file.write(iptables)
    file.close()
