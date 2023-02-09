import builtins
import threading
from tkinter import *
from tkinter import ttk
import socket
import pyaudio
from threading import Thread
import time
import helperFunctions


#HOST = '10.30.8.196'  # The server's hostname or IP address
#PORT = 50010        # The port used by the server
IP = helperFunctions.get_myIP()
P2PPORT = 25566
HOST = helperFunctions.PRIME.split(":")[0]  # The server's hostname or IP address
#HOST = '192.168.1.110'  # The server's hostname or IP address
PORT = int(helperFunctions.PRIME.split(":")[1])    # The port used by the server
musicthread = threading
authThread = threading
p2pJoinThread = threading
root = Tk()
root.geometry("500x300")
root.title("Login Form")

stopThread = 0
playing = 0
loggedIn = 0
P2PConnections = []

frm = ttk.Frame(root, padding=10)
frm.grid()

e = Entry(root)
e.get




def login():
    #Get values
    username = loginEntry.get()
    password = passwordEntry.get()
    
    #Send details to database server
#    #Configure client socket and connect
    myClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    myClientSock.connect((HOST,PORT))
    #MESSAGE = "LOGIN username=" + username +" password=" +password # Data to be sent over the network

    #Check for login server
    MESSAGE = "LOGIN"
    print(MESSAGE)
    myClientSock.sendall(MESSAGE.encode())
    data = myClientSock.recv(1024) #blocking code
    
    resp = data.decode()
    print(resp.split(None)[0])
    if resp.split(None)[0] == "DATABASE@":
     #Connect to login server and send login request
     myClientSock.close()
     loginServer = resp.split(None)[1]
     loginPort = int(resp.split(None)[2])
    
     MESSAGE = "LOGIN username=" + username +" password=" +password # Data to be sent over the network
     print(MESSAGE)
     myAuthSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     myAuthSock.connect((loginServer,loginPort))
     myAuthSock.sendall(MESSAGE.encode())

     data = myAuthSock.recv(1024) #blocking code
     resp = data.decode()

     if(resp == "1"):
        print("logged in as " + username +"!")
        global loggedIn
        loggedIn = 1
        def heartbeat():
            while(loggedIn == 1):
             try:
              myAuthSock.recv(1024)
              RESP = "PONG"
              print(RESP)
              time.sleep(5)
              myAuthSock.sendall(RESP.encode())
             except:
              myAuthSock.close()
            
            #myAuthSock.close()
        authThread.Thread(target=heartbeat).start()

        def closed():
         root.deiconify()
         top.destroy()
         global loggedIn
         loggedIn = 0
        # pygame.mixer.music.stop()
        root.withdraw()
        top = Toplevel(bg="#b3e0ff")
        top.geometry("500x500")



        def selectedSong(self):

            global stopThread
            stopThread = 1
            while(playing != 0):
             pass
            stopThread = 0
            


            print("song selected: " + songList.get(ACTIVE))

            #Connect to file server
            MESSAGE = "MUSIC"
            myClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            myClientSock.connect((HOST,PORT))
            myClientSock.sendall(MESSAGE.encode())
            data = myClientSock.recv(1024) #blocking code
            resp = data.decode()

            if resp.split(None)[0] == "FILE@":
             #Request file
             print("FILE server found!")
             myClientSock.close()
             MESSAGE = "PLAY " + songList.get(ACTIVE) + " " + username
             print(MESSAGE)
             fileServer = resp.split(None)[1]
             filePort = int(resp.split(None)[2])
             myClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
             myClientSock.connect((fileServer,filePort))
             myClientSock.sendall(MESSAGE.encode())
             
             
             #await pyaudio configuration
             print("awaiting config")
             data = myClientSock.recv(1024)
             print("config obtained")
             resp = data.decode()
             if resp.split(None)[0] == "CONFIG":
               FORMAT = int(resp.split(":")[0].split("=")[1])
               RATE = int(resp.split(":")[1].split("=")[1])
               CHANNELS = int(resp.split(":")[2].split("=")[1])
               CHUNK = int(resp.split(":")[3].split("=")[1])
               MSGLEN = int(resp.split(":")[4].split("=")[1])

               print(FORMAT)
               print(RATE)
               print(CHANNELS)
               #Configure pyaudio
               p = pyaudio.PyAudio()

               
            #    # define callback (2)
            #    def callback(in_data, frame_count, time_info, status):
                
            #     return (data, pyaudio.paContinue)

               stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)
               #Let file server know that the client is configured and ready
               MESSAGE = "READY"
               myClientSock.sendall(MESSAGE.encode())
               
               #Await music stream
               def playmusic():
                global playing
                playing = 1    
                print("Playing!")  
                global stopThread
                
                #Open P2P server
                p2pServerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                p2pServerSock.bind((IP,P2PPORT))
                p2pServerSock.listen()
                # p2pServerSock.setblocking(0)
                print("P2P Server started on " + p2pServerSock.getsockname()[0] + ":" + str(p2pServerSock.getsockname()[1]))
 
                bytes_recd = 0
                def p2pThread():
                    while playing == 1:
                     for conns in P2PConnections:
                        print(conns[1])
                        pass
                     #print("P2P Thread Starting!")
                     try:
                      conn, addr = p2pServerSock.accept()
                      print("P2P Client Found! Adding to connection list")
                      P2PConnections.append([conn,addr,0,0])
                     except:
                         pass
                    print("Music stopped. disconnecting P2P Clients")
                    for conns in P2PConnections:
                        P2PConnections.remove(conns)
                        pass
                
                Thread(target=p2pThread).start()
                # data = myClientSock.recv(min(MSGLEN - int(bytes_recd),CHUNK))
                # bytes_recd = bytes_recd + len(data)
                while bytes_recd < MSGLEN:
                 print(stopThread)
                 print("bytes reced: " + str(bytes_recd) + " bytes left: " + str(MSGLEN - bytes_recd))
                 if stopThread == 1:
                   print("thread closed")
                   stream.stop_stream()
                   stream.close()
                   p.terminate()
                   myClientSock.close()
                   playing = 0
                   p2pServerSock.close()
                   return
                 try:
                   print("getting data!")
                   data = myClientSock.recv(CHUNK)
                   print("writing to stream")
                   stream.write(data)
                   #if any P2P Clients, send data to them also
                   for conns in P2PConnections:
                    #if no byts sent to this connection, provide pyaudio configuration
                    if conns[3] == 0:
                     print("sending pyaudio configuration")
                     MESSAGE = "CONFIG FORMAT={FORMAT}:RATE={RATE}:CHANNELS={CHANNELS}:CHUNK={CHUNK}:MSGLEN={MSGLEN}".format(FORMAT=FORMAT,RATE=RATE,CHANNELS=CHANNELS,CHUNK=CHUNK,MSGLEN=MSGLEN - bytes_recd)
                     conns[3] = 1
                     conns[0].sendall(MESSAGE.encode())
                    else:
                     conns[0].send(data)
                   bytes_recd = bytes_recd + CHUNK
                 except Exception as e:
                     print("breaking")
              
                     if e.args[0] == 10054:
                      conns[0].close()
                      print("removing " + str(conns))
                      print(conns)
                      P2PConnections.remove(conns)
                     else:
                      break
                print("done playing")
                global loggedIn
                #loggedIn = 0
                stream.stop_stream()
                stream.close()
                p.terminate()
                myClientSock.close()
                playing = 0
                p2pServerSock.close()

                
               musicthread.Thread(target=playmusic).start()
               

              





             #
            # data = myClientSock.recv(1024) #blocking code
            #Play Song
            # file = 'some.wav'
            # pygame.mixer.music.load(file)
            # pygame.mixer.music.play()

        def songPlay():
            print("song resuming")
           # pygame.mixer.music.unpause()
            
        def songPause():
            print("song Paused!")
            global stopThread
            stopThread =  1
            print(stopThread)

        def songStop():
            print("song stopped")
            #pygame.mixer.music.stop()
        
        #Song list and get song button
        songList = Listbox(top)
     
        songList.bind('<Double-1>', selectedSong)
        songList.grid(row=0,column=0,sticky=W)

        def getSongs():
            songList.delete(0,END)
         
            print("Getting songs from server")

            #Connecting to server
            MESSAGE = "MUSIC"
            myClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            myClientSock.connect((HOST,PORT))
            myClientSock.sendall(MESSAGE.encode())
            data = myClientSock.recv(1024) #blocking code
            resp = data.decode()

            if resp.split(None)[0] == "FILE@":
                print("FILE server found!")
              #Send message requesting songs
                myClientSock.close()
                MESSAGE = "MUSICLIST"                
                fileServer = resp.split(None)[1]
                filePort = int(resp.split(None)[2])
                myClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                myClientSock.connect((fileServer,filePort))
                myClientSock.sendall(MESSAGE.encode())
                data = myClientSock.recv(1024) #blocking code
                resp = data.decode()
                myClientSock.close()

                #Process returned list
                songs = resp.split(None)[1].split(":")
                
                idx = 0
                for song in songs:
                    idx = idx + 1
                    songList.insert(idx,song)
  
                
            # #Display songs
            # # i = 0
            # # for currentSong in songs:
            # #     songList.insert(i,currentSong)
            # #     i = i + 1
            
        getSongs()
        

        p2pAddress = StringVar()

        def p2pJoin():
         def p2pPlayThread():
          global stopThread
          stopThread = 0
          global playing 
          p2pIP = p2pAddress.get().split(":")[0]
          p2pPORT = int(p2pAddress.get().split(":")[1])
          p2pClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          p2pClientSock.connect((p2pIP, p2pPORT))
          print("connected to " + p2pIP + ":" + str(p2pPORT))
          data = p2pClientSock.recv(1024)
          resp = data.decode()
          print("Config:  " + resp)
          FORMAT = int(resp.split(":")[0].split("=")[1])
          RATE = int(resp.split(":")[1].split("=")[1])
          CHANNELS = int(resp.split(":")[2].split("=")[1])
          CHUNK = int(resp.split(":")[3].split("=")[1])
          MSGLEN = int(resp.split(":")[4].split("=")[1])
         
          p = pyaudio.PyAudio()
          stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

          bytes_recd = 0
          while bytes_recd < MSGLEN:
                 print(stopThread)
                 print("bytes reced: " + str(bytes_recd) + " bytes left: " + str(MSGLEN - bytes_recd))
                 if stopThread == 1:
                   print("thread closed")
                   stream.stop_stream()
                   stream.close()
                   p.terminate()
                   p2pClientSock.close()
                   playing = 0
                   return
                 try:
                   print("getting data!")
                   data = p2pClientSock.recv(CHUNK)
                   print("writing to stream")
                   stream.write(data)
                   bytes_recd = bytes_recd + CHUNK
                 except Exception as e:
                     print("breaking")
                     print(e)
                     break
          print("done playing")
          stream.stop_stream()
          stream.close()
          p.terminate()
          p2pClientSock.close()
          playing = 0
         p2pJoinThread.Thread(target=p2pPlayThread).start()

        btnGetSong = Button(top, text="Get Song List!",padx=10,pady=10, command=getSongs).grid(row=1,column=0)

        #Music Player
        btnPlay = Button(top,bg="green",width=5,text="PLAY",command=songPlay).grid(row=0,column=1)
        btnPause = Button(top,bg="yellow",width=5,text="PAUSE",command=songPause).grid(row=0,column=2)
        btnStop = Button(top,bg="red",width=5,text="STOP",command=songStop).grid(row=0,column=3)

        #P2P IP enter
        p2pLabel = Label(top, text="P2P ip address \n e.g (127.0.0.1:25566)").grid(row=2,column=0)
        p2pEntry = Entry(top,textvariable=p2pAddress).grid(row= 2,column= 1)
        p2psubmitBtn = Button(top, text="connect to P2P user",command=p2pJoin).grid(row=2, column=3)


        

        # #Friend list
        # friendList = Listbox(top)
        # friendList.insert(1, "User1")
        # friendList.insert(2, "User2")
        # friendList.insert(3, "User3")
        # friendList.grid(row=0,column=4,sticky=W)

        top.protocol("WM_DELETE_WINDOW", closed)
        

     else:
        print("login details incorrect, try again.")
    myClientSock.close()
    


    
    

#Username
loginLabel = Label(root, text="Username").grid(row=0, column=0)
loginEntry = Entry(root)
loginEntry.grid(row=0, column=1)
#Password
passwordLabel = Label(root,text="Password").grid(row=1, column=0)
passwordEntry = Entry(root)
passwordEntry.grid(row=1, column=1)
#Confirm button
submitBtn = Button(root, text="Login!",command=login).grid(row=2,column=0)
root.mainloop()