import socket
from sqlite3.dbapi2 import Cursor
from threading import Thread
import time
from node import Node
import helperFunctions
import sqlite3
import os
import signal



PRIME = helperFunctions.PRIME
ROLE = "DATABASE"

IP = helperFunctions.get_myIP()
class authNode(Node):
 loggedIn = []

 def processMessage(self, msg, addr, conn):
     print(msg)
     print("messaging being processed by DATABASE node!")
     MESSAGE = "0"
     if msg == "LOAD":
         MESSAGE = str(len(self.loggedIn))
         conn.sendall(MESSAGE.encode())
         conn.close()

     
     if msg.split()[0] == "LOGIN":
         #Get input
 
         username = msg.split()[1].split("=",1)[1]
         password = msg.split()[2].split("=",1)[1]
        
         
         #Confirm details
         logged = False
         db = sqlite3.connect('test.db')
         dbCursor = db.cursor()
         dbCursor.execute('''SELECT username FROM users WHERE username =? AND password =?''',(username,password))
         for row in dbCursor:
          print (row[0])
          for user in self.loggedIn:
              if user[0] == row[0]:
                  print("user already logged in")
                  logged = True
        

          if logged == False:
           MESSAGE = "1"
           self.loggedIn.append((username,addr[0]))
           print("logged in users: " + str(self.loggedIn))
           print(MESSAGE)

           conn.sendall(MESSAGE.encode())
           #Liveliness check
           print("MESSAGE = " + MESSAGE)
           if(MESSAGE != "0"):
            print("HEARTBEAT FROM" + addr[0])
            while True:
             try:
              MESSAGE = "PING"
              print("Number of user connections: " + str(len(self.loggedIn)))
              conn.sendall(MESSAGE.encode())
              print("AWAITING PONG")
              conn.recv(1024)
             except:
              print("CLIENT NO LONGER LOGGED IN!")
              self.loggedIn.remove((username,addr[0]))
              print("logged in users: " + str(self.loggedIn))
              if len(self.loggedIn) == 0:
               print("no more users connected. Shutting down")
               pid = os.getpid()
               os.kill(pid, signal.SIGTERM) 
              break
        #   else:
        #      print("THE MESSAGE IS: " + MESSAGE)
        #      conn.sendall(MESSAGE.encode())
        #      conn.close()
         
         print("THE MESSAGE IS: " + MESSAGE)
         conn.sendall(MESSAGE.encode())
         conn.close()
         
     if msg.split()[0] == "ISLOGGEDIN":
         #Tell requesting node if user is logged in
         print("CHECKING USERS")
         username = msg.split()[2]
         ip = msg.split()[1]
         found = 0
         MESSAGE = "0"
         for user in self.loggedIn:
             if user[0] == username and user[1] == ip:
                 found = 1
                 print("verified " + username)
                 MESSAGE = "1"
                 conn.sendall(MESSAGE.encode())
                 return
         if found == 0:
             print("not found")
         conn.sendall(MESSAGE.encode())
        
           

     return

 def openDB(self):
  db = sqlite3.connect('test.db')
  dbCursor = db.cursor()
  dbCursor.execute('''SELECT username FROM users''')
  for row in dbCursor:
      print (row[0])

  print ("Opened database successfully")
  return
 

#Get random port
port = helperFunctions.get_random_port()

myDbNode = authNode(IP,port,ROLE)
print(myDbNode.role)
myDbNode.openDB()
myDbNode.start()


