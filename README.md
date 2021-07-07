# Peer_to_peer_chatapp
This is a peer to peer terminal based chat application that can work for 2 computer over the internet.

Have you ever wondered how we can make a chat application directly from one computer to another, without involving any kind of server
or any intermediries, just a network of simple day to day laptops and computer.

In this project , i have tried to acomplish the same. This application can chat with a  group of computers by directly connecting to each other.
We also assume that you are connected to internet using some mobile hotpsot or some kind of wifi which implements NAT so that you are behind the NAT.
if you have computer with public IP. even better!

## requirements: 
- A windows or linux computer .
- Python version 3.2 and above
- Superuser permision for network acess.
-  A public computer on cloud or with public ip accesible to all peers

Public computer is needed just for once setting up connection and bypassing the NAT firewall of mobile hotspots.
We use technique called _UDP hole punching_.


### *I would walk you through very easy and detailed steps so you dont get struck anywhere*.


## Steps:

1. clone the directory or download and extract the python files.
2. Run the file _Udp_holepunchtracker.py_ on public computer.
The defualt port would be 6666 . Note down the public ip of the computer.

![](/images/tracker1.jpg)

It may look like this.

3. Now Run the file _Udp_holepunch.py_  on computer you want to make a peer. IF you are on windows , it may show you a firewall warning as this is a networking application.


![](/images/network.png)

make sure you check the *public networks* checkbox and then allow access. In case of linux, you may need to run file with `sudo`.

4. Now your terminal would ask few quetions

![](/images/peer1.jpg)

Mannual mode is when you are testing the application on same computer, or without the tracker file. We choose Authomatic or "a" for now
There would be 3 Gates  or sockets open on interface you specify.

now you may have diffrent interfaces awailable, like loopback, wifi, eathernet. Choose the one which is connected to internet.
for eg in my case, 192.168.43.228 is my wifi interface so i enter index number 2.

NOTE  :*If you are unsure which interface has which ip, open your cmd [if in windows] and enter `ipconfig` to get details of intefaces. in linux this would be `ifconfig`*.   


5. Now , three gates would be up and running. Enter your name and then Super node details.    

![](/images/peer2.jpg)  

Super node is terminal instance running  _udp_holepunchtracker.py_ file you might want to run all instancs _peers and supernode_ on same computer first just for testing purpose.  
Enter the details like this : `192.162.158.6 6666`  
NOTE :_you can skip this part but later you might want to give details anyway_.

6. Now, you just need to type `connect`. And if you and supernode are on same network( _Either internet or on on same local network_)
then you would be succefuly connected to supernode.

![](/images/peer3.jpg)  

7. Now wait for another peer to repeat the same task and connect to supernode, once another pc is connected, you would get info of other peer and would be connected to that. you can then verify by messaging anything.  

Meanwhile you may see some logs on supernode terminal.Ignore them!  
Also , do not worry if you see some weird logs on your terminal also. There is need to work on those.

8. Once some other peer is also connected you may see something like this. If you feel you are not connected, just type `connect` again to refresh.

![](/images/peer4.jpg)  
these are 2 instaces on same pc.  
g1 means you recived a message on gate number 1.

9. If someother peer also want to join, he would repeat the same process. But he cant direcly connect to you since you are already connected and are not waiting in lobby for him. but you can as you have 2 other gates empty.   
so just say `connect` again , and then you would be connected to new guy on other gate.


NOTE : _you may get really weird logs and if these logs do not stop, just close terminal and restart another instance_

10. Some useful commands  

* `show` : used for checking current connection detials.
* `connect` : used for connecting/reconnecting
* `switch` : used in manual mode, to connect to a particular peer.
* `exit` : to exit the terminal
* `info`  : to get the help dialouge box.


#### if you want to work further on this Or understand the code base, i would be happy to help. Reach out to me directly at Ujjwal54784@gmail.com or raise an issue in the repo. 😄




