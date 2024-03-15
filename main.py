# main.py
from gui import SerialTCPGUI
import tkinter as tk

def main():

    root = tk.Tk()
    app = SerialTCPGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
