This Git repository contains script for remotely accessing servers to get iptables, install Halo, and remove Halo.

get_iptables.py 
* Inputs server_list.txt which contains tuples of IP, username, password.  One tuple per line.
* Outputs the iptables on those servers, one txt file per server, each file named after the server
