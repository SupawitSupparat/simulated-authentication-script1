#!/usr/bin/python
from __future__ import print_function
from __future__ import division
from pyrad.client import Client
from pyrad.dictionary import Dictionary
from concurrent.futures import ThreadPoolExecutor
from Queue import Queue
from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool 
from twisted.internet import task
from twisted.internet import reactor
from multiprocessing import Process, Queue
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
import multiprocessing

start_time = time.time()

class Script(object):
    success = 0
    denied = 0
    session = 0
    concurrent = 300
    timeout = 60.0
    threads = []
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
        for i in range(60):
          srv = Client(server=self.server, secret=self.secret, dict=Dictionary("dictionary"))
          req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=self.username)
          req["User-Password"] = req.PwCrypt(self.password)
          self.authandacct(srv,req)
        
    def login(self):
            for i in range (5):
             t = threading.Thread(target = self.task())
             self.threads.append(t)
             t.start()
            
            print ("Start ",time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"))
            print("Sessions transmitted: : ", self.session)
            print("Responses received : ", self.success)
            print("Responses received rate: ", self.success/self.session*100)
            print("Timeout %s seconds " % (time.time() - start_time))


    def auth(self,srv,req):
        self.session += 1    
        reply = srv.SendPacket(req)
        if reply.code == pyrad.packet.AccessAccept:
            self.success += 1
        else:
            self.denied +=1
      
    # def acct(self,srv, req):
    #  print("Sending accounting start packet")
    #  req["Acct-Status-Type"] = "Start"
    #  print("Sending accounting stop packet")
    #  req["Acct-Status-Type"] = "Stop"
    #  req["Acct-Input-Octets"] = random.randrange(2**10, 2**30)
    #  req["Acct-Output-Octets"] = random.randrange(2**10, 2**30)
    #  req["Acct-Session-Time"] = random.randrange(120, 3600)
    #  req["Acct-Terminate-Cause"] = random.choice(["User-Request", "Idle-Timeout"])

    
    def authandacct(self,srv,req):
        if self.request == 'auth':
            self.auth(srv,req) 
        # else:
        #     self.acct(srv,req)


if __name__ == '__main__':
   fire.Fire(Script)