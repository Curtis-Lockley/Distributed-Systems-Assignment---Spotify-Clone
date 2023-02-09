import controlNODE
import helperFunctions
import os
import  time
import socket
musicPath = "music"

PRIME = helperFunctions.PRIME
ROLE = "CONTROL"
primeNode = controlNODE.controlNode(PRIME.split(":")[0], int(PRIME.split(":")[1]), ROLE)
primeNode.start()

def songSync():
 while 1:
  time.sleep(7)
  try:
 #if node does not have song in primes music folder, send song over
 # dir_list = os.listdir(musicPath)
 # print(dir_list)
   songList = os.listdir("music")
   for node in primeNode.myConnections:
    if node[0] == "CONTROL":
     print(("getting songs!"))
     print("requesting songList from " + node[1] + ":" + str(node[2]))
     MSG = "SONGLIST"
     songCheck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     songCheck.connect((node[1], int(node[2])))
     songCheck.sendall(MSG.encode())
     songResults = songCheck.recv(1024).decode().split("SONGS=")[1].split(":")
   
     print((str(songResults)))
     songCheck.close()
     for song in songList:
      print("searching for " + song + " in results folder")
      #Check if results has the same files as the prime node
      found = 0
      syncSock = songCheck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      syncSock.connect((node[1], int(node[2])))
      for result in songResults:
       if result == song:
        found
        found = 1
        continue
      if found == 0:
       print("song not found, sending file over")
       MSG="INCOMINGSONG " + song
       print(MSG)
       songCheck.sendall(MSG.encode())
       file = open("music/"+song,'rb')
       MSG= file.read(1024)
       songCheck.send(MSG)
       while (MSG):
        MSG= file.read(1024)
        songCheck.send(MSG)

       print("Transfer complete")
       file.close()
       syncSock.close()
      #Check if prime needs to download from control node
      for result in songResults:
        found = 0
        syncSock = songCheck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        syncSock.connect((node[1], int(node[2])))
        for song in songList:
         if song == result:
          found = 1
          continue
        if found == 0:
          print("need to download song from node")
          MSG="SENDME " + result
          print(MSG)
          songCheck.sendall(MSG.encode())

          file = open("music/" + result,'wb')
          f = syncSock.recv(1024)
          while f:
              file.write(f)
              f = syncSock.recv(1024)
           
     
          file.close()
          print("file transfered")
 
  except Exception as e:
      print("An exception occurred " + str(e))

songSync()
print("returned")
