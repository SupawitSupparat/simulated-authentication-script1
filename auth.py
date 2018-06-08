#!/usr/bin/python
from __future__ import print_function
from __future__ import division
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import socket
import sys
import pyrad.packet
import mysql.connector
import time
start_time = time.time()
success = 0
denied = 0
session = 0
cnx = mysql.connector.connect(user='admin', 
                              password='admin',
                              host='192.168.56.201',
                              database='radius')

cursor = cnx.cursor()
query = ("SELECT Username,Password FROM test")
cursor.execute(query)
db = cursor.fetchall()

for row in db :
    if time.time() - start_time < 1 :
        session += 1
        srv = Client(server="192.168.56.201", secret=b"testing123", dict=Dictionary("dictionary"))
        req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=row[0])
        req["User-Password"] = req.PwCrypt(row[1])
    
        try:
            reply = srv.SendPacket(req)
        except pyrad.client.Timeout:
            sys.exit(1)
        except socket.error as error:
            sys.exit(1)
        if reply.code == pyrad.packet.AccessAccept:
            print("Access accepted")
            success += 1
        else:
            print("Access denied")
            denied +=1

cursor.close()
cnx.close()
print("Sessions transmitted: : ", session)
print("Responses received : ", success)
rate = success/session*100
print("Responses received rate: ", rate)
print("Timeout %.3s seconds " % (time.time() - start_time))