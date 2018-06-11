#!/usr/bin/python
from __future__ import print_function
from __future__ import division
from pyrad.client import Client
from pyrad.dictionary import Dictionary
from concurrent.futures import ThreadPoolExecutor
from Queue import Queue
from multiprocessing import Pool
import threading
import random
import socket
import sys
import time
import pyrad.packet
import mysql.connector
import time
import fire
import concurrent.futures

start_time = time.time()

class Script(object):
    success = 0
    denied = 0
    session = 0

    def __init__(self, username, password,request,server,secret,timeout,auth_port = 1812,acct_port = 1813):
      self.username = username
      self.password = password
      self.acct_port = auth_port
      self.auth_port = auth_port
      self.request = request
      self.server = server
      self.secret = secret
      self.timeout = timeout

    def task(self):
          srv = Client(server=self.server, secret=self.secret, dict=Dictionary("dictionary"))
          req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=self.username)
          req["User-Password"] = req.PwCrypt(self.password)
          self.authandacct(srv,req)
    
    def login(self):
        self.task()
       


    def auth(self,srv,req):
       
        self.session += 1    
        try:
            reply = srv.SendPacket(req)
        except pyrad.client.Timeout:
            sys.exit(1)
        except socket.error :
            sys.exit(1)
        if reply.code == pyrad.packet.AccessAccept:
            print("Access accepted")
            self.success += 1
        else:
            print("Access denied")
            self.denied +=1

        print ("Start ",time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"))
        print("Sessions transmitted: : ", self.session)
        print("Responses received : ", self.success)
        rate = self.success/self.session*100
        print("Responses received rate: ", rate)
        print("Timeout %s seconds " % (time.time() - start_time))
      
    def acct(self,srv, req):
     print("Sending accounting start packet")
     req["Acct-Status-Type"] = "Start"
     print("Sending accounting stop packet")
     req["Acct-Status-Type"] = "Stop"
     req["Acct-Input-Octets"] = random.randrange(2**10, 2**30)
     req["Acct-Output-Octets"] = random.randrange(2**10, 2**30)
     req["Acct-Session-Time"] = random.randrange(120, 3600)
     req["Acct-Terminate-Cause"] = random.choice(["User-Request", "Idle-Timeout"])

    
    def authandacct(self,srv,req):
        if self.request == 'auth':
            self.auth(srv,req) 
        else:
            self.acct(srv,req)

if __name__ == '__main__':
   fire.Fire(Script)