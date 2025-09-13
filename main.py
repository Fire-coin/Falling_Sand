import tkinter as tk
from time import sleep
from copy import deepcopy
from random import randint
from enum import IntEnum

class Block(IntEnum):
    AIR = 0
    SAND = 1
    WALL = 2
    WATER = 3



class PixelWindow(tk.Canvas):
    def __init__(self, master: tk.Tk, rows: int, columns: int, background: str, blockSize: int) -> None:
        self.__master = master
        self.__cols = columns
        self.__rows = rows
        self.__blockSize = blockSize
        self.__bg = background
        self.__matrix: list[list[Block]] = []
        self.fillMatrix(self.__matrix)
        self.__colors = {
            Block.SAND : "yellow",
            Block.WALL: "grey",
            Block.WATER: "light blue"
        }
        self.__curBlock = Block.SAND

        super().__init__(master, width= columns * blockSize, height= rows * blockSize,
                         bg= background)

    def createSelectionMenu(self) -> None:
        def changeBlock():
            self.__curBlock = Block(iVar.get())

        frame1 = tk.Frame(self.__master)
        frame1.pack()
        iVar = tk.IntVar()
        sandButton = tk.Radiobutton(frame1, text= "Sand", variable= iVar, value= int(Block.SAND), command= changeBlock)
        sandButton.pack(side= "left")
        wallButton = tk.Radiobutton(frame1, text= "Wall", variable= iVar, value= int(Block.WALL), command= changeBlock)
        wallButton.pack(side= "left")
        waterButton = tk.Radiobutton(frame1, text= "Water", variable= iVar, value= int(Block.WATER), command= changeBlock)
        waterButton.pack(side= "left")

    

    def fillMatrix(self, matrix: list[list[Block]]) -> None:
        for _ in range(self.__rows):
            row = [Block.AIR] * self.__cols
            matrix.append(row)

    def fillBlock(self, row: int, column: int, value: Block) -> None:
        try:
            if (self.__matrix[row][column] != Block.AIR): return
            self.__matrix[row][column] = value
        except IndexError:
            pass
    def simulate(self) -> None:
        tempMatrix: list[list[Block]] = deepcopy(self.__matrix)

        for row in range(self.__rows):
            for col in range(self.__cols):
                match (self.__matrix[row][col]):
                    case Block.SAND:
                        if (row + 1 >= self.__rows):
                            continue
                        # Falling down rule
                        if (self.__matrix[row + 1][col] == Block.AIR):
                            tempMatrix[row + 1][col] = Block.SAND
                            tempMatrix[row][col] = Block.AIR
                        else: # Falling to the side rule
                            if (col + 1 >= self.__cols):
                                right = -1
                            else:
                                right = self.__matrix[row + 1][col + 1]

                            if (col - 1 < 0):
                                left = -1
                            else:
                                left = self.__matrix[row + 1][col - 1]
                                
                            if (right != Block.AIR):
                                if (left == Block.AIR):
                                    tempMatrix[row + 1][col - 1] = Block.SAND
                                    tempMatrix[row][col] = Block.AIR
                            else:
                                if (left != Block.AIR):
                                    tempMatrix[row + 1][col + 1] = Block.SAND
                                    tempMatrix[row][col] = Block.AIR
                                else:
                                    # Choosing randomly either to the left or right down
                                    tempMatrix[row + 1][col + (1 if randint(1, 2) == 2 else -1)] = Block.SAND
                                    tempMatrix[row][col] = Block.AIR
                    case Block.WALL: # It is stationery
                        pass
                    case Block.WATER:
                        pass
                    case _:
                        pass


        self.__matrix = tempMatrix

    def render(self) -> None:
        self.delete("Cell")
        for row in range(self.__rows):
            for col in range(self.__cols):
                if (self.__matrix[row][col] != Block.AIR):
                    self.create_rectangle(col * self.__blockSize,
                                          row * self.__blockSize,
                                          (col + 1) * self.__blockSize,
                                          (row + 1) * self.__blockSize,
                                          fill= self.__colors[self.__matrix[row][col]],
                                          width= 0,
                                          tags= [f"Cell"])
    
    def getBlockSize(self) -> int:
        return self.__blockSize



def createBlock(e: tk.Event, w: PixelWindow, block: Block, event: str) -> None:
    w.unbind(event)
    row = e.y // w.getBlockSize()
    col = e.x // w.getBlockSize()

    w.fillBlock(row, col, block)
    w.bind(event, lambda e : createBlock(e, w, block, event))

def terminate(e: tk.Event) -> None:
    global running
    running = False


if (__name__ == "__main__"):
    global running
    running = True
    root = tk.Tk()
    rows = 70
    columns = 50

    pixelW = PixelWindow(root, rows, columns, "black", 10)
    pixelW.pack()
    pixelW.createSelectionMenu()

    pixelW.bind("<B1-Motion>", lambda e : createBlock(e, pixelW, Block.SAND, "<B1-Motion>"))
    pixelW.bind("<B3-Motion>", lambda e : createBlock(e, pixelW, Block.WALL, "<B3-Motion>"))
    root.bind("<Escape>", terminate)

    while (running):
        pixelW.simulate()
        pixelW.render()
        pixelW.update()
        sleep(0.01)
    
    root.destroy()

    root.mainloop()