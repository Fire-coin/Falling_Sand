import tkinter as tk
from time import sleep
from copy import deepcopy


class PixelWindow(tk.Canvas):
    def __init__(self, master: tk.Tk, rows: int, columns: int, background: str, blockSize: int) -> None:
        self.__master = master
        self.__cols = columns
        self.__rows = rows
        self.__blockSize = blockSize
        self.__bg = background
        self.__matrix: list[list[int]] = []
        self.fillMatrix(self.__matrix)

        super().__init__(master, width= columns * blockSize, height= rows * blockSize,
                         bg= background)
    
    def fillMatrix(self, matrix: list[list[int]]) -> None:
        for _ in range(self.__rows):
            row: list[int] = []
            for __ in range(self.__cols):
                row.append(0)
            matrix.append(row)

    def fillCell(self, row: int, column: int, value: int) -> None:
        try:
            self.__matrix[row][column] = value
        except IndexError:
            pass
    def simulate(self) -> None:
        tempMatrix: list[list[int]] = deepcopy(self.__matrix)

        for row in range(self.__rows):
            for col in range(self.__cols):
                # Falling down rule
                #TODO set the value 1 to stationary block, and value 2 to the falling block
                if (self.__matrix[row][col] != 0):
                    if (row + 1 < self.__rows and self.__matrix[row + 1][col] == 0):
                        tempMatrix[row + 1][col] = self.__matrix[row][col]
                        tempMatrix[row][col] = 0
        


        self.__matrix = tempMatrix

    def render(self) -> None:
        self.delete("Cell")
        for row in range(self.__rows):
            for col in range(self.__cols):
                if (self.__matrix[row][col] != 0):
                    self.create_rectangle(col * self.__blockSize,
                                          row * self.__blockSize,
                                          (col + 1) * self.__blockSize,
                                          (row + 1) * self.__blockSize,
                                          fill= "white",
                                          width= 0,
                                          tags= ["Cell"])
    
    def getBlockSize(self) -> int:
        return self.__blockSize



def createCell(e: tk.Event, w: PixelWindow) -> None:
    w.unbind("<B1-Motion>")
    row = e.y // w.getBlockSize()
    col = e.x // w.getBlockSize()

    w.fillCell(row, col, 1)
    w.bind("<B1-Motion>", lambda e : createCell(e, w))

running: bool = True

root = tk.Tk()

rows = 70
columns = 50

pixelW = PixelWindow(root, rows, columns, "black", 10)
pixelW.pack()

pixelW.bind("<B1-Motion>", lambda e : createCell(e, pixelW))

while (running):
    pixelW.simulate()
    pixelW.render()
    pixelW.update()
    sleep(0.01)

root.mainloop()