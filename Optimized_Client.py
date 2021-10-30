from importer import *
from Network import Network
from multiProcessing import Process


class Client:
    def __init__(self):
        self.width = 500
        self.height = 500
        self.pauseNetwork = False
        self.pauseRender = False
        self.playerEvents = ["UP", "DOWN", "DOWN", "RIGHT", "UPDATE List", "APPEND List", "INCREASE COUNTER"]
        self.networkEvents = ["PAUSE RENDER", "RESUME RENDER"]
        self.connect()

    def connect(self, defaultNetwork=None):
        from server_runner import serverRunner
        try:
            if defaultNetwork is None:
                self.network = Network()
            else:
                self.network = defaultNetwork
            self.Player = self.network.getPlayers().players
            self.currentPlayer = self.network.getPlayers().currentPlayer
            print("current player = ",self.currentPlayer)
            self.killReceivingThread = False
            if self.currentPlayer >= 5:
                print("launching new server")
                serverProcess = serverRunner((self.Player,True,self.network.client))
                serverProcess.start()
                serverProcess.join()
                print("server has been killed")
                exit()
            else:
                if defaultNetwork is None:
                    self.win = pygame.display.set_mode((self.width, self.height))
                    pygame.display.set_caption("client")
                    self.main()
                else:
                    start_new_thread(self.receiveEvents, ())
                    self.pauseRender = False
                    print("time taken to restart server is ",time.time()-self.startTime)

        except socket.error:
            print("there are no running servers")
            serverProcess = serverRunner((Player(0, 0, 5, 50, (255, 0, 0)), True, None))
            serverProcess.start()
            serverProcess.join()

            print("server has been killed")
            exit()

    def redrawwindow(self):
        if not self.pauseRender:
            self.win.fill((255, 255, 255))
            self.Player.draw(self.win)
            pygame.display.update()
        else:
            # make a render paused image if you can
            pass

    def reconnect(self):
        # the following code insures that in the event that the client has lost connection
        # the client will first attempt to reconnect with the server or
        # proceed to starting the server itself with it already contains

        from server_runner import serverRunner
        self.pauseRender = True
        self.startTime = time.time()
        network = Network(connectionMethod="brute",timeout=((self.currentPlayer-1)*30)+5)
        if network.getPlayers() == "Start Server":
            serverProcess = serverRunner((self.Player, False, None))
            serverProcess.start()
            network = Network(connectionMethod="brute")
            self.connect(network)
        else:
            self.connect(network)

    def main(self):
        print("client has started")
        self.save = False
        self.run = True
        clock = pygame.time.Clock()
        clock.tick(600)
        start_new_thread(self.receiveEvents, ())

        while self.run:
            if self.killReceivingThread:
                self.reconnect()
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.sendEvent(Event("INCREASE COUNTER", self.currentPlayer, pygame.mouse.get_pos(),
                                         self.Player.getLineCounter(), (255, 0, 0), 1, self.Player.getCurrentHash()))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    lineWidth = self.Player.getLineWidth()
                    if event.button == 5:
                        if lineWidth == 1:
                            pass
                        else:
                            lineWidth -= 1
                            self.Player.setLineWidth(lineWidth)
                    elif event.button == 4:
                        if lineWidth == 30:
                            pass
                        else:
                            lineWidth += 1
                            self.Player.setLineWidth(lineWidth)
                    self.sendEvent(
                        Event("APPEND List", self.currentPlayer, pygame.mouse.get_pos(), self.Player.getLineCounter(),
                              self.rainbowMaker(), self.Player.getLineWidth(), self.Player.getCurrentHash()))

            mouse = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LCTRL] and keys[pygame.K_s]:
                if not self.save:
                    self.savefileas()
                    self.save = True

            if mouse[2]:
                self.sendEvent(
                    Event("APPEND List", self.currentPlayer, pygame.mouse.get_pos(), self.Player.getLineCounter(),
                          (255, 255, 255), 10, self.Player.getCurrentHash()))
            if mouse[0]:
                self.sendEvent(
                    Event("APPEND List", self.currentPlayer, pygame.mouse.get_pos(), self.Player.getLineCounter(),
                          self.rainbowMaker(), self.Player.getLineWidth(), self.Player.getCurrentHash()))
            if keys[pygame.K_LEFT]:
                # self.sendEvent(Event("LEFT", self.currentPlayer))
                self.sendEvent(Event("PAUSE RENDER", None, None, None, None, None, self.Player.getCurrentHash()))
            if keys[pygame.K_RIGHT]:
                self.sendEvent(Event("RESUME RENDER", None, None, None, None, None, self.Player.getCurrentHash()))
            self.redrawwindow()
            time.sleep(.017)

    def savefileas(self):
        root = tkinter.Tk()
        save_file = filedialog.asksaveasfilename(initialdir="/",
                                                 title="Save File",
                                                 filetypes=(("Images", "*.png"), ("All Files", "*.*")))

        if save_file.strip == "":
            pass
        else:

            pygame.image.save(self.win, save_file + ".JPG")
            self.save = False
        root.destroy()

    def appendLines(self, xyTuple):
        self.Player.appendLines(xyTuple)

    def eventHandler(self, event):
        if event.action in self.playerEvents:
            self.Player.eventHandler(event)
        elif event.action in self.networkEvents:
            self.networkHandler(event)
        self.redrawwindow()

    def networkHandler(self, event):
        if event.action == "PAUSE RENDER":
            print("pause pressed")
            self.pauseNetwork = True
        elif event.action == "RESUME RENDER":
            print("resume pressed")
            self.pauseNetwork = False

    def receiveEvents(self):
        print("started receiving thread")
        while True:
            try:
                if not self.killReceivingThread:
                    if not self.pauseNetwork:
                        event = self.network.getEvent()
                        if not event:
                            pass
                        else:
                            self.eventHandler(event)
                    else:
                        Player = self.network.getUpdate()
                        if Player.event == "PASS":
                            print(Player.event)
                            self.Player = Player.players
                            self.currentPlayer = Player.currentPlayer
                        elif Player.event == "RESUME RENDER":
                            print(Player.event)
                            self.pauseNetwork = False
                            time.sleep(0.1)
                else:
                    break

            except socket.error as e:
                print(e)
                self.killReceivingThread = True

        print("client thread is dead")
        print("sleep for ", self.currentPlayer * 3, " seconds")


        print("connection attempted")

    def sendEvent(self, event):
        try:
            if not self.pauseNetwork:
                self.network.sendEvent(event)
            elif event.action in self.networkEvents:
                self.network.sendEvent(event)
        except socket.error as e:
            self.killReceivingThread = True

    def rainbowMaker(self):
        random = Random()
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def clientStarter():
    process = Process(target=Client, args=(), daemon=False)
    return process


if __name__ == "__main__":
    pass
