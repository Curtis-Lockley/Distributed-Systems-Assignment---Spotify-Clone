
import imp
from signal import signal
import socket
from threading import Thread
import time
import helperFunctions
from node import Node
import os
import pyaudio
import wave
import signal

from subprocess import Popen, CREATE_NEW_CONSOLE

IP = helperFunctions.get_myIP()
PRIME = helperFunctions.PRIME
ROLE = "FILE"

class fileNode(Node):
 connectedUsers = 0
 def processMessage(self, msg, addr, conn):
     print(msg)
     print("messaging being processed by FILE node!")
     self.connectedUsers = self.connectedUsers + 1
     if msg.split()[0] == "MUSICLIST":
      songList = ""
      path = "music"
      dir_list = os.listdir(path)
      idx = 0
      for song in dir_list:
       songList = songList + song
       if idx != len(dir_list) - 1:
        songList = songList + ":"
        idx = idx + 1
      MESSAGE = "FILESFOUND " + songList
      print(MESSAGE)
      conn.sendall(MESSAGE.encode())
      conn.close()
      self.connectedUsers = self.connectedUsers - 1
      if self.connectedUsers == 0:
               print("no more users connected. Shutting down")
               pid = os.getpid()
               os.kill(pid, signal.SIGTERM) 

     if msg.split()[0] == "PLAY":
         self.connectedUsers = self.connectedUsers + 1
         #Verify user is logged in
         myAuthSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         myAuthSock.connect((PRIME.split(":")[0],int(PRIME.split(":")[1])))
         MESSAGE = "ISLOGGEDIN " + addr[0] + " " + msg.split()[2]
         print(MESSAGE)
         myAuthSock.sendall(MESSAGE.encode())
         resp = myAuthSock.recv(1024)
         nodes = resp.decode().split(None,1)[1]
         print("nodes:" + str(nodes))
         #Check each node for user
         myAuthSock.close()
         nodes = nodes.split(":")
         print("nodes:" + str(nodes))
         for node in nodes:
          print("Current node: " + node.split()[0] + ":" + node.split()[1])
          myAuthSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          host = node.split()[0]
          port = int(node.split()[1])
          myAuthSock.connect((host,port))
          myAuthSock.sendall(MESSAGE.encode())
          resp = myAuthSock.recv(1024)
          verified = resp.decode()
          print("verified: " + verified)
          if verified == "1":
            myAuthSock.close()
            break

      
         if verified != "0":
          print("PLAYING " + msg.split()[1])

        
          CHUNK = 4096
        
          file = wave.open("music/" + msg.split()[1],'rb')
          p = pyaudio.PyAudio()
         
          #Get pyaudio configuration to send back to client
          FORMAT = p.get_format_from_width(file.getsampwidth())
          RATE = file.getframerate()
          CHANNELS = file.getnchannels()
          MSGLEN = os.stat("music/" + msg.split()[1]).st_size

          print("format: " + str(FORMAT))
          print("framerate: " + str(RATE))
          print("channels: " + str(CHANNELS))
          print("MSGLEN: " + str(MSGLEN))

          #Send configuration back to client
          MESSAGE = "CONFIG FORMAT={FORMAT}:RATE={RATE}:CHANNELS={CHANNELS}:CHUNK={CHUNK}:MSGLEN={MSGLEN}".format(FORMAT=FORMAT,RATE=RATE,CHANNELS=CHANNELS,CHUNK=CHUNK,MSGLEN=MSGLEN)
          conn.sendall(MESSAGE.encode())

          #Await confirmation from the client to begin sending file
          data = conn.recv(1024)
          resp = data.decode()

          if resp == "READY":
             #Configure pyaudio
             # stream = p.open(format = FORMAT,
             #    channels = 1,
             #    rate = RATE,
             #    input=True,
             #    frames_per_buffer=CHUNK)

             #Start sending audio
             bytesSent = 0

             while bytesSent <= MSGLEN:
                try:
                 data = file.readframes(CHUNK)
                 conn.send(data)
                 bytesSent = bytesSent + CHUNK
                 print("bytes sent: "+ str(bytesSent))
            #  data = file.readframes(CHUNK)
            #  while len(data) > 0:
            #      conn.send(data)
            #      data = file.readframes(CHUNK)
                except:
                    print("Client either disconnected or is done recieving")
                    break
             print("done sending!")
             # stream.stop_stream()
             # stream.close()
             p.terminate()
             conn.close()
             self.connectedUsers = self.connectedUsers - 1
             if self.connectedUsers == 0:
               print("no more users connected. Shutting down")
               pid = os.getpid()
               os.kill(pid, signal.SIGTERM) 
         else:
             MESSAGE = "UNVERIFIED"
             myAuthSock.close()
             conn.sendall(MESSAGE.encode())
             conn.close()


     return
 
#Get random port
port = helperFunctions.get_random_port()
#port = 50009
myFileNode = fileNode(IP,port,ROLE)
myFileNode.start()

