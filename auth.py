#!/usr/bin/python
from __future__ import print_function
from __future__ import division
from pyrad.client import Client
from pyrad.dictionary import Dictionary
from Queue import Queue
from threading import Thread
import random
import socket
import sys
import time
import pyrad.packet
import mysql.connector
import time
import fire
import argparse
import ast



start_time = time.time()

class Script(object):
    success = 0
    denied = 0
    session = 0
    timeout = 60.0
    threads = []

    def __init__(self, username, password,request,server,secret,concurrent,timeout,auth_port = 1812,acct_port = 1813):
      self.username = username
      self.password = password
      self.acct_port = auth_port
      self.auth_port = auth_port
      self.request = request
      self.server = server
      self.secret = secret
      self.timeout = timeout/1000
      self.concurrent = concurrent
   
    def SendPacket(self,srv, req):
        try:
            srv.SendPacket(req)
        except pyrad.client.Timeout:
            print("RADIUS server does not reply")
            sys.exit(1)
        except socket.error as error:
            print("Network error: " + error[1])
            sys.exit(1)

    def login(self):
         srv = Client(server=self.server, secret=self.secret, dict=Dictionary("dictionary"))
         req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=self.username)
         req["User-Password"] = req.PwCrypt(self.password)
         t = Thread(target=self.authandacct(srv,req))
         t.daemon = True
         t.start()
         if(self.request == 'auth'):
            print("Start :",time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"))
            print("Request type : ",self.request)
            print("Sessions transmitted : ", self.session)
            print("Responses received : ", self.success)
            print("Responses received rate: %s %% " % (self.success/self.session*100))
            print("Timeout %.4s seconds " % (time.time() - start_time))
       
    def auth(self,srv,req):
        for i in range(self.concurrent):
         if time.time() - start_time < self.timeout :
              self.session += 1    
              reply = srv.SendPacket(req)
              if reply.code == pyrad.packet.AccessAccept:
                  self.success += 1
              else:
                  self.denied +=1
         else: i = self.concurrent

    def acct(self,srv, req):
        print("Sending accounting start packet")
        req["Acct-Status-Type"] = "Start"
        self.SendPacket(srv, req)
        print("Sending accounting stop packet")
        req["Acct-Status-Type"] = "Stop"
        req["Acct-Input-Octets"] = random.randrange(2**10, 2**30)
        req["Acct-Output-Octets"] = random.randrange(2**10, 2**30)
        req["Acct-Session-Time"] = random.randrange(120, 3600)
        req["Acct-Terminate-Cause"] = random.choice(["User-Request", "Idle-Timeout"])
        self.SendPacket(srv, req)

    def authandacct(self,srv,req):
     if (self.request == 'auth'):
         self.auth(srv,req)
     elif(self.request == "acct"):
         self.acct(srv,req)



if __name__ == '__main__':
   fire.Fire(Script)
  
