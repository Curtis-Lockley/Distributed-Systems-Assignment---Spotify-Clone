import socket
import helperFunctions

#PRIME = "10.30.8.196:50001"
#PRIME = "192.168.1.110:25565"
#PRIME = "192.168.1.110:25565"

#Config
PRIME = "127.0.0.1:50001"
IP = "127.0.0.1"
#PRIME = "10.30.8.172:50001"
#IP = "10.30.8.172"
PORTSTART = 50002
PORTEND = 50010

def get_myIP():
 global IP
 #ip =socket.gethostbyname(socket.gethostname())
 #ip = "192.168.1.110" # for testing
 #ip = "10.30.8.196" # for testing
 #ip = "192.168.1.110" # for testing
 return IP

def get_random_port():
    # current = 50001
    # port = 0
    # #Get random port
    # tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tempSock.bind(('',0))
    # port = tempSock.getsockname()[1]
    # tempSock.close()
    # print(port)
 tempSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 for port in (range(PORTSTART,PORTEND)):
  try:
     print("trying to host port on port " + str(port))
     tempSock.bind((IP,port))
     print("port found!")
     tempSock.close()
     return port
  except:
   print("port taken")
   pass




