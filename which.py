import subprocess
a = subprocess.Popen("which apt-get", stdout=subprocess.PIPE, shell=True).stdout.read()
a = a.replace("\n","")
if a == '/usr/bin/apt-get':
    print "This linux is Debian"
else:
    print "This linux is NOT Debian"
