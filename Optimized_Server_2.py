from importer import *
from multiprocessing import Process

class Server():
    def __init__(self,player = Player(0,0,5,50,(255,0,0)),spawnclient = True, clientnetwork= None):
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        self.port = 5555
        self.clientCount = 0
        self.spawnClient = spawnclient
        self.clientNetwork = clientnetwork
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.players = player
        self.clientList = []
        self.hashList = []
        self.pauseOperations = False
        self.startTime = 0.0
        self.serverCount = 0
        self.serverList = []
        self.parentServer = None
        self.acceptUpdateFromParent = False
        self.currentServerCount = 0
        self.init()


    def init(self):
        from client_runner import clientRunner

        if self.spawnClient:
            if self.clientNetwork is not None:
                self.parentServer = self.clientNetwork
                start_new_thread(self.acceptInitialDataFromParent,(self.parentServer,))
            print("starting server through client")
            self.connect()
            self.socket.listen(20)
            start_new_thread(self.run,())
            self.clientProcess = clientRunner()
            self.clientProcess.start()

        else:
            self.connect()
            self.socket.listen(20)
            self.run()


        while True:
            pass



    def connect(self):
        while True:
            try:
                self.socket.bind((self.host_ip,self.port))
                break
            except socket.error as e:
                print(e)
                quit(0)
                exit()
        print("host has connected")

    def parentServerEventHandler(self,event):
        if event.action == "PAUSE RENDER" and not self.acceptUpdateFromParent:
            self.acceptUpdateFromParent = True
        elif self.acceptUpdateFromParent and event.event == "PASS":
            self.players = event.players
        elif self.acceptUpdateFromParent and event.event == "RESUME RENDER":
            self.acceptUpdateFromParent = False
        else:
            self.players.eventHandler(event)

    def bufferSize(self,conn):
         return pickle.loads(conn.recv(512)).bufferSize

    def acceptData(self,bufferSize):
        try:
            acceptedData = pickle.loads(self.client.recv(bufferSize))
            return acceptedData
        except Exception as e:
            print(e)


    def acceptInitialDataFromParent(self,conn):
        bufferSize = self.bufferSize(conn)
        print("initial dize of the data coming from the server = ", bufferSize)
        dataFromServer =  self.acceptData(bufferSize)
        self.players = dataFromServer.players
        self.currentServerCount = dataFromServer.currentPlayer


    def parentServerHandler(self,conn):
        self.acceptInitialDataFromParent(conn)
        while True:
            try:
                event = pickle.loads(conn.recv(1024))
                self.parentServerEventHandler(event)
                if not event:
                    print("diconnected")
                    break
                else:
                    # event to be sent to client has to be pickled
                    clientEvent = pickle.dumps(event)
                    for conns in range(len(self.clientList)):
                        self.hashList[conns] = event.currentHash
                        self.clientList[conns].sendall(clientEvent)
            except:
                break



        print("Lost connection")
   

    def sendToClient(self,conn,event):

        bufferSize = pickle.dumps(recvSize(sys.getsizeof(event)))
        # send size of the object to the client
        conn.send(bufferSize)
        # server sleep for 5ms to give the client enough time to process accept data in sequence
        time.sleep(0.005)
        #send event object to client
        conn.send(event)

    def verifyDuplicateConsistency(self):
        # checks whether list values for every client maintain a two third majority consensus

        checkedHashes = []
        hashConsistency = 0
        for hashs in self.hashList:
            if hashs not in checkedHashes:
                checkedHashes.append(hashs)
                hashCount = self.hashList.count(hashs)
                if hashCount > hashConsistency:
                    hashConsistency = hashCount
        consistencyPercentile = 1
        if len(self.hashList) != 0:
            consistencyPercentile = hashConsistency/len(self.hashList)

        if consistencyPercentile >= 0.66:
            return True
        else:
            return False

    def checkTimer(self):
        # every ten seconds the function checks value for consensus
        # if majority is preserved everything carries on
        # else all clients are updated with the values from the server

        while True:
            if (time.time()-self.startTime) > 10:
                self.startTime = time.time()
                if not self.verifyDuplicateConsistency():
                    self.pauseOperations = True
                    self.updateAllClients()
                else:
                    pass

            else:
                # since while loops can be expensive this function sleeps for the next ten seconds ensuring
                # that the least amount of steps are taken to check consensus
                time.sleep(10)



    def updateAllClients(self):
        # send message to all clients to pause operations
        for conns in range(len(self.clientList)):
            self.clientList[conns].sendall(pickle.dumps(Event("PAUSE RENDER", None, None, None, None, None,None)))
        time.sleep(0.1)
        # send server player object to all clients
        for conns in range(len(self.clientList)):
            self.sendToClient(self.clientList[conns],pickle.dumps(Players(self.players,conns,"PASS")))
        time.sleep(0.1)
        # send message to all clients to resume operations
        for conns in range(len(self.clientList)):
            self.sendToClient(self.clientList[conns], pickle.dumps(Players(None, None, "RESUME RENDER")))
        time.sleep(0.01)
        self.pauseOperations = False


    def threaded_Client(self,conn,playerCount):
        self.initializeClient(conn,playerCount)
        self.hashList.append(self.players.getCurrentHash())
        while True:
            try:
                if not self.pauseOperations:
                    # find a way to call updateALlClients outside this loop, without repetition
                    event = pickle.loads(conn.recv(1024))
                    # print(self.players.getCurrentHash(),self.hashList)
                    self.players.eventHandler(event)

                    # print(event.action,event.data)
                    if not event:
                        print("diconnected")
                        break
                    else:
                        # event to be sent to client has to be pickled
                        clientEvent = pickle.dumps(event)
                        if self.parentServer is not None:
                            self.parentServer.sendall(clientEvent)
                        for conns in range(len(self.clientList)):
                            self.hashList[conns] = event.currentHash
                            self.clientList[conns].sendall(clientEvent)
                else:
                    pass
            except:
                break
        print("Lost connection")
        index = self.clientList.index(conn)
        self.hashList.remove(self.hashList[index])
        self.clientList.remove(conn)
        self.clientCount -= 1
        conn.close()

    def initializeClient(self, conn, playerCount):

        # sends the player object that is kept on the server to the new client
        allPlayers = pickle.dumps(Players(self.players, playerCount))
        bufferSize = pickle.dumps(recvSize(sys.getsizeof(allPlayers)))
        # send size of the object to the client
        conn.send(bufferSize)
        print("sending the initial size of the Player",bufferSize)
        time.sleep(0.1)
        # send Player object
        conn.send(allPlayers)

    def run(self):
        print("running has started")
        self.startTime = time.time()
        while True:
            conn, addr = self.socket.accept()
            if self.clientCount <5:
                self.clientList.append(conn)
                print("Connected to:", addr)
                start_new_thread(self.threaded_Client, (conn, self.clientCount))
                self.clientCount += 1
                if self.clientCount >=2:
                    # the need to ensure majority consensus is only required if two or more clients are connected
                    start_new_thread(self.checkTimer, ())
            elif self.serverCount < 5 and self.clientCount >= 5:
                self.serverList.append(conn)
                self.clientList.append(conn)
                start_new_thread(self.threaded_Client, (conn,self.serverCount))
                self.serverCount += 1

    # def initializeServerProtocolsAsGod(self, conn, serverCount):
    #     if serverCount == 5:
    #         protocol = pickle.dumps(
    #             Players(self.players, serverCount, event="SERVER HAS REACHED MAX LOAD, LAUNCH NEW SERVER"))
    #         bufferSize = pickle.dumps(recvSize(sys.getsizeof(protocol)))
    #     elif serverCount > 5:
    #         pass
    #     # send size of the object to the client
    #     conn.send(bufferSize)
    #     time.sleep(0.1)
    #     # send Player object
    #     conn.send(protocol)
    #
    # def threaded_ProxyClient(self, conn, serverCount):
    #     self.initializeServerProtocolsAsGod(conn, serverCount)



                
        
        



def serverStarter(arguments):
    process = Process(target=Server,args=arguments,daemon=False)
    return process


        
if __name__ == "__main__":
    pass

