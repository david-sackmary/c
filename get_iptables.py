import paramiko, argparse, csv

def get_Iptables(ip, id, password):
    trans = paramiko.Transport((ip, 22))
    trans.connect(username=id, password=password)
    session = trans.open_channel("session")
    session.exec_command('sudo iptables -L')
    session.recv_exit_status()
    while session.recv_ready():
        return session.recv(1024)

### Begin Execution ###
parser = argparse.ArgumentParser()
parser.add_argument('--input', '-i', action='store', default='./server_list.txt',
                    help='File path & name for server list')
args = parser.parse_args()
args.debug = False
server_list = list(csv.reader(open(args.input, 'rb'), delimiter=' ', skipinitialspace=True))
for server in server_list:
    ip = server[0]
    id = server[1]
    password = server[2]
    if args.debug:
        print ('Server IP: %s\nLogin ID: %s\nLogin Password: %s\n' % (ip, id, password))

    iptables = get_Iptables(ip, id, password)
    outfile = ip + "_iptables"
    file = open(outfile,"w")
    file.write(iptables)
    file.close()
