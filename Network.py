import  socket
import pickle
import events
import sys
import time
from Discovery import NetworkDicovery


class Network:
    def __init__(self,configured_IP = None,connectionMethod = "Default",timeout = 30):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        self.port = 5555
        self.configured_IP = configured_IP
        self.eventSize = 2048
        self.allDevicesIP = []
        self.isConnected = False
        self.connectionMedthod = connectionMethod
        self.timeout = timeout
        if self.configured_IP is None:
            self.getAllDevicesIP()
        else:
            self.allDevicesIP = [self.configured_IP]
        if self.connectionMedthod == "Default":
            self.players = self.connect()
        elif self.connectionMedthod == "brute":
            self.players = self.bruteConnect()

    def getHost(self):
        return self.host_ip


    def getPlayers(self):
        return self.players

    def getEvent(self):
        event = pickle.loads(self.client.recv(2048))
        return event


    def getUpdate(self):
        # try:
            # receive the size of the event object from the server
        bufferSize = self.bufferSize()
        print("size of event from the server = ",bufferSize)
        # accept the event object with the allocated buffer size then returns it to calling method
        return self.acceptData(bufferSize)
        # except pickle.UnpicklingError as p:
        #     print(p)
        #     pass

    def getAllDevicesIP(self):
        # returns a list of IPs of all connected devices on the Network to allDevices list
        self.allDevicesIP = NetworkDicovery().getAllHosts()

    def bruteConnect(self):
        print("client is attempting to bruteConnect to ", self.allDevicesIP)
        startTime = time.time()
        while time.time() - startTime < self.timeout:
            for ip in self.allDevicesIP:
                try:
                    self.addr = (ip, self.port)
                    self.client.connect(self.addr)
                    print("client has conneced to ",self.addr)
                    self.isConnected = True
                    break
                except:
                    pass
            if self.isConnected:
                break
            else:
                time.sleep(1)
        if self.isConnected:
            # receive the size of the player from the server
            bufferSize = self.bufferSize()
            print("initial dize of the data coming from the server = ", bufferSize)
            # accept the player object with the allocated buffer size
            return self.acceptData(bufferSize)
        else:
            print("restart server")
            return "Start Server"

    def connect(self):
        print("client is attempting to connect to ",self.allDevicesIP)
        for ip in self.allDevicesIP:
            try:
                self.addr = (ip, self.port)
                self.client.connect(self.addr)
                self.isConnected = True
                break
            except:
                pass
        if self.isConnected:
            # receive the size of the player from the server
            bufferSize = self.bufferSize()
            print("initial dize of the data coming from the server = ", bufferSize)
            # accept the player object with the allocated buffer size
            return self.acceptData(bufferSize)
        else:
            raise socket.error

    def bufferSize(self):
         return pickle.loads(self.client.recv(512)).bufferSize

    def acceptData(self,bufferSize):
        try:
            acceptedData = pickle.loads(self.client.recv(bufferSize))
            if acceptedData.event == "SERVER HAS REACHED MAX LOAD, LAUNCH NEW SERVER":
                pass
            elif acceptedData.event == "SERVER HAS REACHED MAX LOAD, CONNECT TO OTHER IP":
                # acceptedData.openServerIP
                pass
            else:
                print("data has been accepted")
                return acceptedData
        except Exception as e:
            print(e)


    def sendEvent(self,event):

        pickleEvent = pickle.dumps(event)
        self.client.send(pickleEvent)


    def send(self,data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(self.eventSize))
        except socket.error as e:
            print(e)

    def killClient(self):
        self.client.close()
        self.client.detach()
        self.client.shutdown(0)




