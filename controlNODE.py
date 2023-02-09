
from audioop import add
import socket
from threading import Thread
import time
import os
import helperFunctions
from node import Node

from subprocess import Popen, CREATE_NEW_CONSOLE

#Known address of the primary control node
PRIME = helperFunctions.PRIME
ROLE = "CONTROL"
class controlNode(Node):
 maxLoad = 6
 load = 0
 def spawnNode(self,role):
   #Check current load
   if self.load != self.maxLoad:
    if role == "DATABASE":
       theproc = Popen(["py", "dbNode.py"], creationflags=CREATE_NEW_CONSOLE)
       #theproc = Popen(["venv38/Scripts/python.exe", "dbNODE.py"], creationflags=CREATE_NEW_CONSOLE)
    elif role == "FILE":
       theproc = Popen(["py", "fileNODE.py"], creationflags=CREATE_NEW_CONSOLE)
       #theproc = Popen(["venv38/Scripts/python.exe", "fileNODE.py"],creationflags=CREATE_NEW_CONSOLE)
   else:
    for node in self.myConnections:
      if node[0] == "CONTROL":
        print(str(node)) # ('CONTROL', '127.0.0.1', '50002', 63075)
        loadCheck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        loadCheck.connect((node[1],int(node[2])))
        MSG = "LOAD"
        loadCheck.sendall(MSG.encode())
        load = int(loadCheck.recv(1024).decode())
        print("Load for current node is: " + str(load))
        if load < self.maxLoad:
          #Control node has room for more nodes
          MSG = "SPAWN " + role
          loadCheck.sendall(MSG.encode())
          loadCheck.recv(1024)
          loadCheck.close()
        else:
         print("maxload: " + str(self.maxLoad) + " load: " + str(load))
          



   return

 def handleDisconnect(self,conn,addr):
   #See if client is in list of connections
   if self.ip + ":" + str(self.port) == PRIME:
    for node in self.myConnections:
      if node[1] == addr[0] and node[3] == addr[1]:
       try:
        print("removing node from known connections")
        role = node[0]
        self.myConnections.remove(node)
       except:
        print("failed to remmove, node may already have been removed")
       if role != "CONTROL" and node[1] == self.ip:
        self.load = self.load - 1
       elif role == "CONTROL":
        #Delete all nodes from ip of the disconnected control node
        print("control node has disconnected!")
        for node in self.myConnections:
          if node[1] == addr[0]:
           self.myConnections.remove(node)
       else:
        #Tell control node to decrease load by 1
        for node in self.myConnections:
          if node[1] == addr[0]:
            try:
              decLoadSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              decLoadSock.connect((node[1],int(node[2])))
              MSG = "DECLOAD"
              decLoadSock.sendall(MSG.encode())
              decLoadSock.close()
            except:
              print("could not access control node")
           

    print(self.myConnections)
    print("current nodes: " + str(self.load))
   return
 

 def findNode(self,role,conn):
    found = 0
    for node in self.myConnections:
        if node[0] == role:
          #ECHO node found
          HOST = node[1]
          PORT = node[2]
          MESSAGE = role +"@ " + HOST + " " + PORT
          #Send server details back to client
          print(MESSAGE)
          conn.sendall(MESSAGE.encode())
          found = 1
          return MESSAGE
    if found == 0:
      print("NODE NOT FOUND, MAKING NEW ONE")
      self.spawnNode(role)
      time.sleep(0.75)
      return self.findNode(role,conn)

 def findAllNode(self,role,conn):
   found = 0
   first = 1
   print("FINDING ALL " + role + " NODES")
   MESSAGE = ""
   for node in self.myConnections:
     if node[0] == role:
       #Node found
       print("Node found!")
       found = 1
       HOST = node[1]
       PORT = node[2]
       print(HOST + str(PORT))
       if(first == 1):
         MESSAGE = MESSAGE + role +"@ " + HOST + " " + PORT
         first = 0
       else:
         MESSAGE = MESSAGE + ":" + HOST + " " + PORT
   if found == 0:
      print("NODE NOT FOUND, MAKING NEW ONE")
      self.spawnNode(role)
      time.sleep(0.5)
      return self.findAllNode(role,conn)   
      
   print(MESSAGE)  
   return MESSAGE
 def endSetup(self):
  # if self.ip + ":" + str(self.port) == PRIME:
  # #Startup required nodes
  #  print("spinning up required nodes")
  # #Startup load balancer
  # #  theproc = Popen(["py", "loadNODE.py"],creationflags=CREATE_NEW_CONSOLE)
  # #Startup File (Service) node
  #  #theproc = Popen(["venv38/Scripts/python.exe", "fileNODE.py"],creationflags=CREATE_NEW_CONSOLE)
  #  #theproc = Popen(["py", "fileNODE.py"],creationflags=CREATE_NEW_CONSOLE)
  # # #Startup database (Authentication) node
  #  #theproc = Popen(["py", "dbNODE.py"],creationflags=CREATE_NEW_CONSOLE)
  # #  theproc = Popen(["py", "dbNODE.py"],creationflags=CREATE_NEW_CONSOLE)
  # #  theproc = Popen(["py", "dbNODE.py"],creationflags=CREATE_NEW_CONSOLE)
  return


 def processMessage(self, msg, addr, conn):
    print(msg)
    if msg == "SPAWN ECHO":
     print("SPAWN ECHO COMMAND")

    if msg.split(None)[0] == "REGISTER":
     # Register node

       if addr not in self.myConnections:
        print("new connection!")
        connectionDetails = (msg.split(None)[1], addr[0],msg.split(None)[2],addr[1])
        self.myConnections.append(connectionDetails)
        if(msg.split(None)[1] != "CONTROL" and addr[0] == self.ip):
          self.load = self.load + 1

        print(self.myConnections)
        print("current nodes: " + str(self.load))
    
    if msg == "ECHOTEST":
      self.findNode("ECHO",conn)

    
    if msg == "LOGIN":
      #find database nodes in connections list
      print("finding DB node")
      found = 0
      while found == 0:
       MESSAGE = self.findAllNode("DATABASE",conn).split(None,1)[1]
       print("balancing load for: " + str(MESSAGE))
       nodes = MESSAGE.split(":")
       #for each node
       for node in nodes:
        loadCheck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("connected to " + node.split(None)[0])
        loadCheck.connect((node.split(None)[0],int(node.split(None)[1])))
        CHECKMSG = "LOAD"
        loadCheck.sendall(CHECKMSG.encode())
        load = loadCheck.recv(1024).decode()
        print("Load for current node is: " + load)
        if int(load) < 2:
         found = 1
         MESSAGE = "DATABASE@ " + node.split(None)[0] + " " + node.split(None)[1]
         break
       if found != 0:
        print(MESSAGE)
        conn.sendall(MESSAGE.encode())
        return
       theproc = Popen(["py", "dbNode.py"], creationflags=CREATE_NEW_CONSOLE)
       #theproc = Popen(["venv38/Scripts/python.exe", "dbNode.py"], creationflags=CREATE_NEW_CONSOLE)
       time.sleep(1)
    
    if msg == "MUSIC":
      MESSAGE = self.findNode("FILE",conn)
      conn.sendall(MESSAGE.encode())

    if msg.split()[0] == "ISLOGGEDIN":

       MESSAGE = self.findAllNode("DATABASE",conn)
       conn.sendall(MESSAGE.encode())
    
    if msg.split()[0] == "LOAD":
              
       MESSAGE = str(self.load)
       print("sending load")
       conn.sendall(MESSAGE.encode())
       print("load sent")

    if msg.split(None)[0] == "SPAWN":
      self.spawnNode(msg.split(None)[1])
      MESSAGE = "DONE"
      self.load = self.load + 1
      conn.sendall(MESSAGE.encode())

    if msg.split(None)[0] == "DECLOAD":
      self.load = self.load - 1
    

    if msg.split(None)[0] == "SONGLIST":
        songList = os.listdir("music")
        MSG = "SONGS="
        for song in songList:
            if MSG != "SONGS=":
                MSG = MSG + ":"
            MSG = MSG + str(song)
        conn.sendall(MSG.encode())

    if msg.split(None)[0] == "INCOMINGSONG":
        file = open("music/" + msg.split(None)[1],'wb')
        f = conn.recv(1024)
        while f:
            file.write(f)
            f = conn.recv(1024)
     
        file.close()
        print("file transfered")
    
    if msg.split(None)[0] == "SENDME":

     file = open("music/"+ msg.split(None)[1],'rb')
     MSG= file.read(1024)
     conn.send(MSG)
     while (MSG):
      MSG= file.read(1024)
      conn.send(MSG)

     print("Transfer complete")
     file.close()
     conn.close()
         

    return

    # if msg == "ECHOTEST":
    #   #Find first echo node in connections list
    #    for node in self.myConnections:
    #     if node[0] == "ECHO":
    #       #ECHO node found
    #       HOST = node[1]
    #       PORT = node[2]
    #       MESSAGE = "ECHO@ " + HOST + " " + PORT
    #       #Send server details back to client
    #       print(MESSAGE)
    #       conn.sendall(MESSAGE.encode())
    #       break


# primeNode = controlNode(PRIME.split(":")[0],int(PRIME.split(":")[1]),ROLE)
# primeNode.start()
# time.sleep(1)
# myControlNode = controlNode(helperFunctions.get_myIP(),helperFunctions.get_random_port(),ROLE)
# myControlNode.start()
