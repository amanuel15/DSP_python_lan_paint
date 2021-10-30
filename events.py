
class Event:
    def __init__(self,action, playerNumber,data,lineCounter,color,width,currentHash):
        self.action = action
        self.playerNumber = playerNumber
        self.data = data
        self.lineCounter = lineCounter
        self.color = color
        self.width = width
        self.currentHash = currentHash

class recvSize:
    def __init__(self,bufferSize):
        self.bufferSize = bufferSize


class Players:
    def __init__(self,players,currentPlayer,event = None,openServerIP = None):
        self.players = players
        self.currentPlayer = currentPlayer
        self.event = event
