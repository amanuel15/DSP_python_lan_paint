import tkinter
from tkinter import filedialog
import pygame



def openFIle():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Open File",
                                          filetypes = (("Text Files", "*.txt"),("All Files","*.*")))
    print(filename)


def savefileas(win):
    root = tkinter.Tk()
    save_file = filedialog.asksaveasfilename(initialdir = "/",
                                             title = "Save File",
                                             filetypes = (("Images","*.png"),("All Files","*.*")))

    if save_file.strip == "":
        pass
    else:

        pygame.image.save(win, save_file + ".JPG")
        save = True
    root.destroy()





