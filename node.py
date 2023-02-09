
from audioop import add
import re
import socket
from threading import Thread
import time
import helperFunctions

#Known address of the primary control node
PRIME = helperFunctions.PRIME
class Node(Thread):
 def __init__(self, ip, port, role):
        Thread.__init__(self)
        self.role = role
        self.ip = ip
        self.port = port
        
        if self.ip + ":" + str(self.port) == PRIME:
            print("I AM THE KNOWN PRIME NODE")
            self.myConnections = []
            print(self.myConnections)

 def handleClient(self,conn,addr):
   #Handles each individual client on a seperate thread
     print("Handling connection ")
     print(addr[0])
     while True:
      try:
       data = conn.recv(1024)
       if data:
        self.processMessage(data.decode(),addr,conn)
       if not data:
        break
      except:
        print("Connection lost! " + str(addr[0]))
        self.handleDisconnect(conn,addr)
        break

 def handleDisconnect(self,conn,addr):
   print("handleDisconnect called")
   return

 def endSetup(self):
 
  return
      
  
 def spawnSever(self):
  #Configure server and start listeninig
  myServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  myServerSock.bind((self.ip,self.port))
  myServerSock.listen()
  print(self.role,"listeninig on",self.ip + ":" + str(self.port))

  
  #Register node with PRIME node
  if(self.ip + ":" + str(self.port) != PRIME):
     
   print("Registering newly created node")

   #Connect new node to CONTROL node for registration
   myClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   myClientSock.connect((PRIME.split(":")[0],int(PRIME.split(":")[1])))
         
   #Register node
   command = ("REGISTER " + self.role + " " + str(self.port))
   myClientSock.sendall(command.encode())

  self.endSetup()
  #Infinite accept loop
  while True:
   conn, addr = myServerSock.accept()
   print("Client FOUND!")
   Thread(target=self.handleClient, args=(conn,addr)).start() #New thread for each connected client
  

   
   


 def run(self):
   self.spawnSever()
   
   




