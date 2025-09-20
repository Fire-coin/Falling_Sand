import tkinter as tk
from time import sleep
from copy import deepcopy
from random import randint
from enum import IntEnum

class Block(IntEnum):
    MOVED = -1
    AIR = 0
    SAND = 1
    WALL = 2
    WATER = 3
    ACID = 4



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
            Block.WATER: "light blue",
            Block.ACID: "#8FFE09"
        }
        self.__curBlock = Block.SAND
        self.disolvable = set(Block._member_map_.values())
        self.disolvable.remove(Block.ACID)
        self.disolvable.remove(Block.AIR)
        self.disolvable.remove(Block.MOVED)

        self.lighterMap: dict[Block, set[Block]] = {
           Block.SAND : set((Block.AIR, Block.WATER, Block.ACID)),
           Block.WATER : set((Block.AIR, Block.ACID)) 
        }

        # self.lighterMap[Block.SAND]: set[Block] = set((Block.AIR, Block.WATER, Block.ACID))

        super().__init__(master, width= columns * blockSize, height= rows * blockSize,
                         bg= background)

        self.bind("<B1-Motion>", self.createBlock)

    def createSelectionMenu(self) -> None:
        def changeBlock():
            self.__curBlock = Block(iVar.get())

        frame1 = tk.Frame(self.__master)
        frame1.pack()
        iVar = tk.IntVar(value= 1)
        airButton = tk.Radiobutton(frame1, text= "Air", variable= iVar, value= int(Block.AIR), command= changeBlock)
        airButton.pack(side= "left")
        sandButton = tk.Radiobutton(frame1, text= "Sand", variable= iVar, value= int(Block.SAND), command= changeBlock)
        sandButton.pack(side= "left")
        wallButton = tk.Radiobutton(frame1, text= "Wall", variable= iVar, value= int(Block.WALL), command= changeBlock)
        wallButton.pack(side= "left")
        waterButton = tk.Radiobutton(frame1, text= "Water", variable= iVar, value= int(Block.WATER), command= changeBlock)
        waterButton.pack(side= "left")
        acidButton = tk.Radiobutton(frame1, text= "Acid", variable= iVar, value= int(Block.ACID), command= changeBlock)
        acidButton.pack(side= "left")

    

    def fillMatrix(self, matrix: list[list[Block]]) -> None:
        for _ in range(self.__rows):
            row = [Block.AIR] * self.__cols
            matrix.append(row)

    def fillBlock(self, row: int, column: int, value: Block) -> None:
        try:
            if (self.__matrix[row][column] != Block.AIR and self.__curBlock != Block.AIR): return
            self.__matrix[row][column] = value
        except IndexError:
            pass
    
    def liquidSpill(self, liquid: Block, row: int, col: int) -> None:
        if (col + 1 >= self.__cols):
            right = -1
        else:
            right = self.tempMatrix[row][col + 1]

        if (col - 1 < 0):
            left = -1
        else:
            left = self.tempMatrix[row][col - 1]
            
        if (right != Block.AIR):
            if (left == Block.AIR):
                self.tempMatrix[row][col - 1] = liquid
                self.tempMatrix[row][col] = Block.AIR
        else:
            if (left != Block.AIR):
                self.tempMatrix[row][col + 1] = liquid
                self.tempMatrix[row][col] = Block.AIR
            else:
                # Choosing randomly either to the left or right down
                self.tempMatrix[row][col + (1 if randint(1, 2) == 2 else -1)] = liquid
                self.tempMatrix[row][col] = Block.AIR

    def simulate(self) -> None:
        self.tempMatrix: list[list[Block]] = deepcopy(self.__matrix)

        for row in range(self.__rows):
            for col in range(self.__cols):
                match (self.__matrix[row][col]):
                    case Block.SAND:
                        if (row + 1 >= self.__rows):
                            continue
                        # Falling down rule
                        match (self.__matrix[row + 1][col]):
                            case Block.AIR:
                                self.tempMatrix[row + 1][col] = Block.SAND
                                self.tempMatrix[row][col] = Block.AIR
                            case Block.WATER:
                                self.tempMatrix[row + 1][col] = Block.SAND
                                self.tempMatrix[row][col] = Block.WATER
                                self.__matrix[row + 1][col] = Block.MOVED
                                self.__matrix[row][col] = Block.MOVED
                            case Block.MOVED:
                                pass
                            case _: # Falling to the side rule
                                if (col + 1 >= self.__cols):
                                    right = -1
                                else:
                                    right = self.__matrix[row + 1][col + 1]

                                if (col - 1 < 0):
                                    left = -1
                                else:
                                    left = self.__matrix[row + 1][col - 1]
                                    
                                if (right not in self.lighterMap[Block.SAND]):
                                    if (left in self.lighterMap[Block.SAND]):
                                        self.tempMatrix[row + 1][col - 1] = Block.SAND
                                        self.tempMatrix[row][col] = Block(left)
                                else:
                                    if (left not in self.lighterMap[Block.SAND]):
                                        self.tempMatrix[row + 1][col + 1] = Block.SAND
                                        self.tempMatrix[row][col] = Block(right)
                                    else:
                                        # Choosing randomly either to the left or right down
                                        choice = randint(1, 2)
                                        self.tempMatrix[row + 1][col + (1 if choice == 2 else -1)] = Block.SAND
                                        self.tempMatrix[row][col] = Block(right) if choice == 2 else Block(left)
                    case Block.WALL: # It is stationery
                        pass
                    case Block.WATER:
                        # Falling down rule
                        if (row + 1 < self.__rows and self.__matrix[row + 1][col] in self.lighterMap[Block.WATER]):
                            match self.__matrix[row + 1][col]:
                                case Block.AIR:
                                    self.tempMatrix[row + 1][col] = Block.WATER
                                    self.tempMatrix[row][col] = Block.AIR
                                case Block.ACID:
                                    self.tempMatrix[row + 1][col] = Block.AIR
                                    self.tempMatrix[row][col] = Block.AIR
                                    self.__matrix[row + 1][col] = Block.MOVED
                                case _:
                                    pass
                        else: # Moving to the side rule
                            self.liquidSpill(Block.WATER, row, col)
                    case Block.ACID:
                        if (row + 1 >= self.__rows or self.__matrix[row + 1][col] == Block.ACID):
                            if (col + 1 >= self.__cols):
                                right = Block.ACID
                            else:
                                right = self.tempMatrix[row][col + 1]

                            if (col - 1 < 0):
                                left = Block.ACID
                            else:
                                left = self.tempMatrix[row][col - 1]
                            


                            if (right != Block.ACID):
                                if (left != Block.ACID):
                                    result = randint(1, 2)
                                    self.tempMatrix[row][col + (1 if result == 2 else -1)] = (Block.AIR if (right if result == 2 else left) in self.disolvable else Block.ACID)
                                    self.tempMatrix[row][col] = Block.AIR
                                    if (result == 2):
                                        self.__matrix[row][col + 1] = Block.MOVED
                                else:
                                    self.tempMatrix[row][col + 1] = (Block.AIR if right in self.disolvable else Block.ACID)
                                    self.tempMatrix[row][col] = Block.AIR
                                    self.__matrix[row][col + 1] = Block.MOVED
                            else:
                                if (left != Block.ACID):
                                    self.tempMatrix[row][col - 1] = (Block.AIR if left in self.disolvable else Block.ACID)
                                    self.tempMatrix[row][col] = Block.AIR
                            continue

                        # Falling down rule
                        if (self.__matrix[row + 1][col] in self.disolvable):
                            self.tempMatrix[row][col] = Block.AIR
                            self.tempMatrix[row + 1][col] = Block.AIR
                            self.__matrix[row + 1][col] = Block.MOVED
                        else:
                            self.tempMatrix[row][col] = Block.AIR
                            self.tempMatrix[row + 1][col] = Block.ACID
                    case _:
                        pass


        self.__matrix = self.tempMatrix

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

    def createBlock(self, e: tk.Event) -> None:
        self.unbind("<B1-Motion>")
        row = e.y // self.getBlockSize()
        col = e.x // self.getBlockSize()

        self.fillBlock(row, col, self.__curBlock)
        self.bind("<B1-Motion>", self.createBlock)

def terminate(e: tk.Event) -> None:
    global running
    running = False


if (__name__ == "__main__"):
    global running
    running = True
    root = tk.Tk()
    rows = 70
    columns = 50

    BLOCK_SIZE = 10
    pixelW = PixelWindow(root, rows, columns, "black", BLOCK_SIZE)
    pixelW.pack()
    pixelW.createSelectionMenu()

    root.bind("<Escape>", terminate)

    while (running):
        pixelW.simulate()
        pixelW.render()
        pixelW.update()
        sleep(0.01)
    
    root.destroy()

    root.mainloop()