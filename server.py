"""launch server application for remote code execution.
"""

import socket
import numpy as np
import sys
import subprocess
import jsonpickle
import argparse
import subprocess
import cloudpickle
import dill
import os
import torch


def execute(fname):
    """execute python source code and return res to client.

    evaluate python source and place its runtime environment into namespace, a dict. then, extract res
    from environment and return it to client.
    """
    
    # https://github.com/mynameisvinn/piegrad/blob/master/PieGrad.py
    # https://stackoverflow.com/questions/16877323/getting-return-information-from-another-python-script
    # https://stackoverflow.com/questions/6357361/alternative-to-execfile-in-python-3
    namespace = {}  # this is the server's runtime env
    with open(fname, "rb") as source_file:
        code = compile(source_file.read(), fname, "exec")
    exec(code, namespace)  # put results in namespace env 
    
    # send numpy results as bytes https://markhneedham.com/blog/2018/04/07/python-serialize-deserialize-numpy-2d-arrays/
    res = namespace['res']
    return res


def receive_file(c, out_fname):
    """receive bytes from client and save as out_fname.
    
    https://stackoverflow.com/questions/9382045/send-a-file-through-sockets-in-python
    """
    # data = c.recv(1024).decode('utf-8')

    l = c.recv(65536 * 5)
    print("reading", l)
    with open(out_fname, 'wb') as f:
        f.write(l)
    return True
    

def _install_packages(c):
    """pip install packages necessary for client script.
    """
    # receive requirements from client
    r = receive_file(c, "requirements.txt")
    
    # pip install
    if r:
        ret = subprocess.run(["pip", "install", "-r", "requirements.txt"])
        if ret.returncode != 0:  # https://www.google.com/search?q=return+code+0&oq=return+code+0&aqs=chrome..69i57.3240j0j1&sourceid=chrome&ie=UTF-8
            raise ValueError


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, help='server port')
    args = parser.parse_args()

    print(">> server up with port", args.port)

    # set up an endpoint for communication with client
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    endpoint = ('', args.port)  # https://stackoverflow.com/questions/8033552/python-socket-bind-to-any-ip
    s.bind(endpoint)
    s.listen(5)
    
    while True:

        # step 1: connect with client
        c, addr = s.accept()      
        print('successfully connected to', addr )

        # step 2: receive requirements from client and install necessary packages
        print(">> installing requirements.txt")
        _install_packages(c)

        # step 2: receive source file from client and save it as "barfoo"
        temp_fname = "barfoo.py"
        receive_file(c, temp_fname)

        # step 3: evaluates source and return result
        res = execute(temp_fname)

        # step 4: convert res to bytes as a file
        with open('results.pkl', 'wb') as f:
            cloudpickle.dump(res, f)

        # then send that file over a socket
        with open('results.pkl', "rb") as f:
            b = f.read()
        c.sendall(b)  # https://stackoverflow.com/questions/56194446/send-big-file-over-socket
        
        c.close() 
        print(">> closed connection with client", addr)