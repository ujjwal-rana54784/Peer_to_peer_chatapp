import socket
import threading
import sys
import random
import hashlib
import datetime
import time

connections = set()
furthercheck = True
def listner(t):
    global furthercheck
    print("Started listening on ",ip," ", port)
    while 1 :
        bytesAddressPair = t.recvfrom(1024)
        # print("here")
        
        message = bytesAddressPair[0].decode('utf-8')
        address = bytesAddressPair[1]
        print("RAW ",address,message,'\n')
        if(message[0]=="+"):
            entry =    address[0] +":"+ str(address[1])+'-'+message[1:]
            connections.add(entry)
            t.sendto("Regs".encode(),address)
            print("added ...")
            furthercheck = True
            
        # except(KeyboardInterrupt):
        #     print("Exiting now")
        #     t.close()
        #     sys.exit()



def resolver():
    global furthercheck
    temp = set()
    while 1 :
        # print(len(connections)>=2 ,furthercheck )
        while(len(connections)>=2 and  furthercheck):   
            
            x = connections.pop().split('-')
            id1 =  x[-1]
            
            print("Resolving...",id1)
            addr1 = (x[0].split(':')[0] , int(x[0].split(':')[1]) )
            z=len(connections)
            for i in range(z) :
                b = connections.pop().split('-')
                id2 = b[-1]
                print("attempting....","id1:",id1 ,"id2 :", id2)
                if((id1 in b) or (id2 in x) ):
                    temp.add( "-".join(b))
                    print("Found in connctions.... skipping........................")
                    if(i==z-1):
                        connections.add("-".join(x))
                        furthercheck = False
                        connections.update(temp)
                        break
                    continue
                addr2 = (b[0].split(':')[0] , int(b[0].split(':')[1]) )
                addr2tobesent = b[0].split(':')[0] +" " + b[0].split(':')[1] + " "+str(id2)
                addr1tobesent = x[0].split(':')[0] + " "+ x[0].split(':')[1] + " "+str(id1)
                
                t.sendto( ("Connection_details " + str(addr2tobesent)).encode(),addr1)
                t.sendto( ("Connection_details " + str(addr1tobesent) ).encode(),addr2)
                
                connections.update(temp)
                break
        #     break
    
    
def Connetion_check(t,event):
    while 1:
        if(len(connections)>0):
            for i in connections:
                ip,port = i.split('-')[0].split(':')
                port = int (port)
                t.sendto("TRACKER REFRESH!, please reconnect if you want!".encode(),(ip,port))
        connections.clear()
        event.wait(60)
    


t  = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
port = 6666
ip =  socket.gethostbyname(socket.gethostname())

t.bind((ip,port))

t1 = threading.Thread(target=listner,args=(t,))
t1.setDaemon(1)
t1.start()

t2 = threading.Thread(target=resolver)
t2.setDaemon(1)
t2.start()

t3event= threading.Event()
t3 =threading.Thread(target = Connetion_check,args=(t,t3event))
t3.setDaemon(1)
t3.start()
while(1):
    
    x = input(">>")
    if(x=="show"):
        for i in connections:
            print(i.split('-')[-1])
            print(furthercheck)




        

        
    
    
    
    