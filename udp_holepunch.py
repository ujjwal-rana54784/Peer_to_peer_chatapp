import socket
import threading
import sys
import random
import hashlib
import datetime
import time


class Gate(object):
    def __init__(self,name,port = random.randint(5000,10000)):
        self.ip = None
        self.port = port
        print(f"{name} ready on port {port}")
        self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
        self.bufferSize = 1024
        self.connection = None
        self.state = False
        self.start = False
        self.supernode = None
        self.name =  name
        self.peer  = None
        self.connection_name = None
        self.connectedpeerID = None
        self.pingcheck = True
    
    def opengate(self,address):  
            bytesToSend = str.encode( f"Connection_attempt {self.peer.name} {self.peer.peerid}" , "utf-8")
            for i in range(3):       
                
                self.s.sendto(bytesToSend,address )
                self.connection = address
            
    def ping(self):
        if(self.state):
            self.pingcheck = False
            for i in range(5):
                self.s.sendto("ping".encode(),self.connection)   
            
           
    def listner(self):
        print(f"\n \n >>>[ Listneing for messages on {self.ip}  {self.port} ... \n \n")
        while 1:
            
            
            bytesAddressPair = self.s.recvfrom(self.bufferSize)
            message = bytesAddressPair[0].decode('utf-8')
            address = bytesAddressPair[1]
            # print(message, "raw form")
            if(not message):
                continue
            # if( message.split()[0] in (self.peer.cache1 | self.peer.cache2) ):
            #     continue
            
            # in case of connection attempt recieved
            if(message =="ping"):
                if(self.connection):
                    self.pingcheck = True
                    self.s.sendto("pingback".encode(),self.connection)
                # print(self.name," online!")
                
                continue
            elif(message == "pingback"):
                # print(self.name," online!")
                self.pingcheck = True
                continue
            elif(message.split()[0] =="TRACKER")  :
                self.connection = None
                self.state = False
                self.connection_name = None
                self.connectedpeerID = None         
            elif(message.split()[0] == "Connection_attempt"):
                name = message.split()[1]
                if(self.connection and self.state):                   
                    # choice = input(f"Do you want to switch connection to {address} : {name}  . Say Y or N ?")
                    choice = "Y"
                    if(choice =="N"):
                        print(f"[Connection request from {address} : {name} declined!]")
                        continue
                self.connection = address
                self.connection_name = name
                self.connectedpeerID = message.split()[2]
                self.s.sendto(f"Connected! {self.peer.peerid}".encode(),address)
                print(f"{address} : connected!")
                self.state = True
                print("state updated to ",self.peer.g1.state,self.peer.g2.state,self.peer.g3.state, "conection to ",self.connection)
                
                if(self.peer.mode and not self.peer.g3.state):
                    self.peer.connect_to_network()
                
                self.state = True
            # conformation msg for connection
            elif(message.split()[0] == "Connected!" ):
                self.state = True
                self.connection = address
                self.connectedpeerID = message.split()[1]
                # print("state updated to " , self.state,"conntection 1 to ",self.connection)
                
                if(self.peer.mode and not self.peer.g3.state):
                    self.peer.connect_to_network()
                print(f"[{address}] succesfully connected  the {self.connection_name} on our {self.name}")
            
            #when registered with the supernode
            elif(message=="Regs"):
                print("Conntected to super node....")
                
            #in case of connection detail recived for the gate 
            elif(message.split()[0] == "Connection_details"):
                m  = message.split()
                self.connectedpeerID = m[3]
                print(f"peer ID info updated as {self.name} connected to {self.connectedpeerID}")
                print(f"Peer info : ip : {m[1]} \n port: {m[2]}")      
                #try a connection attempt
                print(f"[ Attemting to connect to {self.connection_name } {m[1]}:{m[2]} on {self.name} ... ]")
                newpeer = (m[1], int(m[2]))
                self.opengate(newpeer)
                
            else:
                try: 
                    
                    try:
                        
                        hashofmsg ,name,m,tstampt  =message.split("=")
                        if(self.peer.checkhash(hashofmsg)):
                            print(self.name,":",name,">>",m)
                        else:
                            continue
                    except:
                        print("RAW ", message)
                        continue
                    # print(m,"this is m")
                    

                    # self.peer.msgrelay.add()                
                    # self.peer.msgrelaymap[h] = m2
                    
                    self.peer.relay_unit(self,message)
                except(IndexError):
                    print("Index error, rounting issue!")
                    pass
            
    def newconnection(self,supernode_addr,custom_msg):
        if(supernode_addr):
            self.supernode = supernode_addr
            print(f"Attempting a New connection to supernode {supernode_addr} ")
            self.s.sendto(custom_msg.encode('Utf-8'),supernode_addr)
            if(not (self.start) ):
                self.s.bind((self.ip,self.port))
                t = threading.Thread(target=self.listner)
                t.start()
                self.start = True
                
        
    def send(self,msg):
        # format of the msg is [MSGHASH=NAME=MSG=TIMESTAMP]
        
        msg = self.peer.name +"="+ msg + "="+ str(datetime.datetime.now().second)
        msghash = hashlib.md5(msg.encode()).hexdigest()[:10]
        Finalmsg = msghash + "=" + msg
        self.peer.checkhash(msghash)
        if(self.state):
            self.s.sendto(Finalmsg.encode('utf-8') , self.connection)
        else:
            print(f"gate is not realy connected yet {self.name}")
            
    def relay(self,msg):
        if(self.connection):
            self.s.sendto(msg.encode('utf-8') , self.connection)
        else:
            print(f"not connected yet {self.name} ")
        # relay msg is orginialy hashed by someone else so no need to hash it again
            
    def ready(self):
        self.s.bind((self.ip,self.port))
        t = threading.Thread(target=self.listner)
        t.start()
        self.start = True
        
# So a gate can open gates of a ip
# listen for incoming messaages and based on that
#  >> get connected on any connection attempt
         
class peer(object):
    def __init__(self,g1,g2,g3,name,supernode_addr,mode):
        self.ip = socket.gethostbyname_ex(socket.gethostname())
        x = input(f"which ip interface you would like to make a gates on \n {self.ip[2]} give the index number : ")
        self.ip = self.ip[2][int(x)]
        self.mode = mode  # true means automatic
        self.g1 = g1
        self.g2 = g2
        self.g3=  g3
        self.g1.peer = self
        self.g2.peer = self
        self.g3.peer = self
        self.g1.ip = self.ip
        self.g2.ip = self.ip
        self.g3.ip = self.ip
        idinfo = f"{self.ip}{self.g1.port}{self.g2.port}{self.g3.port}".encode()
        self.peerid = hashlib.md5(idinfo).hexdigest()[:10]
        
        
        self.glist = [self.g1,self.g2,self.g3]
        self.name = name
        self.connected_peers = [ self.g1.connection, self.g2.connection, self.g3.connection] # name of the peers
        self.supernode_addr = supernode_addr
        
        # self.msgrelay = set()
        # self.msgrelaymap = dict()
        self.cache1 = set()
        self.cache2 = set()
        
        self.cache1clear = True
        self.cache2clear  =True
        t3event = threading.Event()
        t3 = threading.Thread(target= self.verifyconnections,args=(t3event,))
        t3.setDaemon(1)
        t3.start()
    def connect_to_network(self) :
        if( not self.g1.state):
            self.g1.connectedpeerID = None
            self.g1.newconnection(self.supernode_addr,self.connect_packet(self.g1))
        elif( (not self.g2.state) ):
            self.g1.connectedpeerID = None
            self.g2.newconnection(self.supernode_addr,self.connect_packet(self.g2))
            
        elif(not self.g3.state ):
            self.g1.connectedpeerID = None
            self.g3.newconnection(self.supernode_addr,self.connect_packet(self.g3))
        else:
            print("ALL gates are connected ! ")
            
        
    def connect_packet(self,gate) :
        # sample connect packet is  [ privateIP-gate-connectedpeerids-peerId]
        # ip is there to diffentiate host behind NAT,gate is there to diffrentiate the gate, connected peer is theere to check we dont connection to same guy again
        #server must Take the connectect packet and send us back Regs first to show that we are registered with him
        #then he must send us Connection_details back to us
        #  "Connection_details ip:port "
        
        x = ""
        # noofpeer = 0
       
        # print(self.g1.connectedpeerID)
        # print(self.g2.connectedpeerID)
        # print(self.g3.connectedpeerID,end="\n\n\n")
        
        connected_peersids = [ str(self.g1.connectedpeerID), str(self.g2.connectedpeerID),str(self.g3.connectedpeerID)] 
        # print(connected_peersids,".............................\n\n")
        for i in connected_peersids:
            
            if(i):
                x = x + "-" + str(i)
                # noofpeer  +=1 
        # so x = -192.168.43.91:5506-184.55.5.6:5520 example
        
        peer_discovery_msg = f"+{self.ip}-{gate.name}{x}-{self.peerid}"
        
        return peer_discovery_msg
    
    
    
    def start(self):
        
        self.g1.ready()
        self.g2.ready()
        self.g3.ready()
        
    
    
    def checkhash(self,h):
        
        if(h in self.cache1 | self.cache2):
            return False  # its in the cache, dont relay or print the msg
        else:
            
            if(datetime.datetime.now().minute %2 ==0):
                self.cache2clear = True
                if(self.cache1clear):
                    self.cache1.clear()
                    # print("Cashe 1 Cleared!")
                    self.cache1clear = False
                self.cache1.add(h)
                # print("Cashe update:", self.cache1,  self.cache2  )
            else:
                self.cache1clear = True
                if(self.cache2clear):
                    self.cache2.clear()
                    # print("Cache2 cleared!")
                    self.cache2clear = False
                self.cache2.add(h)
                # print("Cashe update:", self.cache1 , self.cache2  )
            return True
                
        
        
    def relay_unit(self,gate,m):       
        for i in self.glist :
            if(i != gate and i.state):
                i.relay(m)
    def verifyconnections(self,event):

        while(1):
            # self.connect_to_network()
            self.g1.ping()
            self.g2.ping()
            self.g3.ping()
            
            event.wait(30)
            
            if(not self.g1.pingcheck and self.g1.state ):
                self.g1.state = False
                self.g1.connection = None
                self.g1.connectedpeerID = None
                self.g1.connection_name = None
                # self.connect_to_network()
                print(f"{self.g1.connection_name} disconnected from the network] ...\n " )
        
            if(not self.g2.pingcheck and self.g2.state):
                self.g2.state = False
                self.g2.connection = None
                self.g2.connectedpeerID = None
                self.g2.connection_name = None
                # self.connect_to_network()
                print(f"{self.g2.connection_name} disconnected from the network] ...\n " )
            if(not self.g3.pingcheck and self.g3.state):
                self.g3.state = False
                # self.connect_to_network()
                self.g3.connection = None
                self.g2.connectedpeerID = None
                self.g2.connection_name = None
                print(f"{self.g3.connection_name} disconnected from the network] ...\n " )
                
        
    
# server should have reposnse of connectable peer when recived msg with = and should respond with Connection_details name ip port
# server must maintain a peer record
t = input("Chose the mode of opeartion. \n Mannual or Automatic (with public server available)  M/A")
if(t=="M" or t=="m"):
    t = False
elif(t=="a" or t=="A"):
    t = True
else:
    print("input not correct , please enter valid input. Restart the file")
    sys.exit(0)

r1 = random.randint(5000,10000)
r2 = random.randint(5000,10000)
r3 = random.randint(5000,10000)
g1  = Gate("g1",r1)
g2 = Gate("g2",r2)
g3 = Gate("g3",r3)


Ujjwal = peer(g1,g2,g3,"UNKNOWN",None,t)

Ujjwal.start()
name  = input("YOUR NAME : ")
Ujjwal.name = name

supernode = input("Enter super node details. you can change them later By connect. PRESS S to SKIP! \n")
if(supernode != "S" and supernode != "s"):
    Ujjwal.supernode_addr = (supernode.split()[0] , int(supernode.split()[1]))


info = """
Hello, welcome to help  menu for this peer to peer chatbox.
A few point to note :
=> Gate ip adresses are chosen randomly
=> you cannot connect to same peer on multiple gates. A peer id is made by Name and port number of 3 gates. which is unique.

MAnual mode: 
this mode is for testing purpose
you can also connect to the multiple terminals instances of users and server on same computer using this.

Enter "switch"
then the gate number on which you want to switch connection.
Then enter the <ip><space><port> of the new details. eg. " 10.1.0.4 5567 "
you would be connected to that gate of that instance.


Automatic mode :
here you need to specify supernode details first.
you can skip them initialy but later you have to specify them
We assume super node have the python file running for supernode and it is acccesible to all peers.
Then you just have to type "connect" and you would be connected with supernode and it would automaticly 
check who is in lobby and connect with random stranger.


enter "show" to see what are your status of connection on 3 gates

local message cache is cleared after every 2 minutes
every 30 sec connection is checked if it is still alive or not. So if you feel you are disconnected
Just type "connect" again.

"""
while(1):
    # print(Ujjwal.g1.state, "here")
    
    msg = input(">> ")
    if(msg == "exit"):
        Ujjwal.g1.s.close()
        Ujjwal.g2.s.close()
        Ujjwal.g3.s.close()
        sys.exit()
    elif(msg == ""):
        print(".......Empty msg are not allowed!....")
        continue
    elif(msg == "switch"):
        x = int(input("which gate? tell the number: "))- 1
        
        y = input("Enter the new connection details : ")
        Ujjwal.glist[x].opengate((y.split()[0],int( y.split()[1])))
    elif (msg.split()[0] == "NAME"):
        Ujjwal.name = msg.split()[1]
        continue
    elif(msg.split()[0] == "clear"):
        x = int(msg.split()[1])
        Ujjwal.glist[x].connection_name = None
        Ujjwal.glist[x].state = False
        Ujjwal.glist[x].connection = None
        Ujjwal.glist[x].peerid = None
        Ujjwal.connect_to_network()
        continue
        
        
    elif(msg.split()[0] == "connect"):
        if( len(msg.split())>1 and msg.split()[1] =="new" or not Ujjwal.supernode_addr):
            y = input("supernode ip port : ")
            ip,port = y.split()
            port = int(port)
            Ujjwal.supernode_addr = (ip,port)
            Ujjwal.connect_to_network()
            
        elif(Ujjwal.supernode_addr):
            Ujjwal.connect_to_network()
            
        
    elif(msg == "show"):
        print(".............",Ujjwal.name,".......",Ujjwal.ip )
        print("peer id is :",Ujjwal.peerid)
        print("connnection detials are  ")
        print(Ujjwal.g1.connection , Ujjwal.g2.connection,Ujjwal.g3.connection,end="\n")
        print(Ujjwal.g1.connection_name , Ujjwal.g2.connection_name,Ujjwal.g3.connection_name,end="\n")
        print("Following are the peer ID's \n")
        print(Ujjwal.g1.connectedpeerID,end="  ")
        print(Ujjwal.g2.connectedpeerID,end="  ")
        print(Ujjwal.g3.connectedpeerID,end="\n\n\n")
        continue
    elif(msg =="info"):
        print(info)
        continue
    
    for i in Ujjwal.glist :
        if(i.state):
            i.send(msg)
        
   
   
    
    