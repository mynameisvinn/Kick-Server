# setting up infrastructure

## launching ec2 instance
you can find preconfigured amis by searching "deep learning ami" for ubuntu machines.

once youve launched ec2, youll need to update [kick.ini](https://github.com/mynameisvinn/Kick/blob/master/Kick/kick.ini) for the client library (which needs host ip and port).

## configuring ec2 ports
for now, enable all inbound traffic to all ports.

## configuring da server
upload [server.py](https://github.com/mynameisvinn/Kick-Server/blob/master/server.py) to your ec2 machine. 

shell into the ec2 machine and do `python server.py 1111`. (1111 refers to the server port; it can be anything since we've enabled inbound traffic to all ports.) you should see `>> server up`.

### why do we send a file (instead of bytes) over a socket?
tbd