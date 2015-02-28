#install_halo_via_ssh.py
* Inputs server_list.txt which contains tuples of IP, username, password.  One tuple per line.

#remove_halo_via_ssy.py
* Inputs server_list.txt which contains tuples of IP, username, password.  One tuple per line.

#Get_Iptables.py
* Inputs server_list.txt which contains tuples of IP, username, password.  One tuple per line.
* Outputs the iptables on those servers, one txt file per server, each file named after the server

Authors:

Remotely accesses an arbitrary number of remote servers and returns their iptables.

##Dependencies:

    argparse
    csv
    paramiko
    

##Installation

Clone, download, or fork the git repo, then configure as below.

##Configuration

Edit server_list.txt.  For each line, add an IP address, username and password.

##Usage:

./install_halo_via_ssh.py server_list.txt
Installs Halo on each server listed in server_list.txt

./get_iptables.py server_list.txt

##Output

For each line in server_list.txt, ip_tables.py will generate a text file which contains the iptables for that server.
These text files will appear in the same directory where get_iptables.py is executed.
