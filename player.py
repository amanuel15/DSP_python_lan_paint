import pygame


class Player():
    def __init__(self,x,y,lineWidth,height,color):
        self.x = x
        self.y = y
        # self.width = width
        self.height = height
        self.color = color
        # self.rect = (x,y,width,height)
        self.lineWidth = lineWidth
        self.val = 1
        self.lineList = []
        self.line = []
        self.lineCounter = 0

    def getLineCounter(self):
        return self.lineCounter

    def getCurrentHash(self):
        return hash(str(self.line))

    def getColor(self):
        return self.color

    def getLineWidth(self):
        return self.lineWidth

    def setLineWidth(self,lineWidth):
        self.lineWidth = lineWidth

    def increaseLineCounter(self):
        self.lineCounter += 1
        self.line = []

    def appendLines(self,xyTuple,color,width):
        self.line.append(xyTuple)
        if len(self.lineList) == self.lineCounter:
            self.lineList.append([self.line,color,width])
        if len(self.line) !=0:
            self.lineList[self.lineCounter] = [self.line,color,width]



    def updateLines(self,lineList,lineCounter):
        self.lineList = lineList
        self.lineCounter = lineCounter

    def draw(self,win):
        self.drawLine(win)

    def drawLine(self,win):
        if len(self.lineList)==0:
            pygame.draw.lines(win,self.color,False,[(0,0),(0,0)])
        else:
            for lines in self.lineList:

                if len(lines[0]) <2:
                    pygame.draw.lines(win, self.color, False, [(0, 0), (0, 0)])
                else:
                    # print(lines[1])
                    pygame.draw.lines(win, lines[1], False, lines[0],lines[2])

    def moveUp(self):
        self.y -= self.val
        self.update()

    def moveDown(self):
        self.y += self.val
        self.update()

    def moveLeft(self):
        self.x -= self.val
        self.update()

    def moveRight(self):
        self.x += self.val
        self.update()


    def eventHandler(self, event):
        if event.action == "UP":
            self.moveUp()
        elif event.action == "DOWN":
            self.moveDown()
        elif event.action == "LEFT":
            self.moveLeft()
        elif event.action == "RIGHT":
            self.moveRight()
        elif event.action == "UPDATE List":
            self.updateLines(event.data,event.lineCounter)
        elif event.action == "APPEND List":
            self.lineCounter = event.lineCounter
            self.appendLines(event.data,event.color,event.width)
        elif event.action == "INCREASE COUNTER":
            self.increaseLineCounter()




    def update(self):
        self.rect = (self.x, self.y, self.width, self.height)