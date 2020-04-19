import urllib.request  # instead of urllib2 like in Python 2.7
import json
import pandas as pd
from datetime import date, datetime, time, timedelta
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from corona import CoronaInfo
from earthquake import EarthquakeInfo


class DataStructures():

    def __init__(self):
        self.root = Tk()  # Main window
        self.sel_country = StringVar()  # Selected country

        # Main window attibutes
        self.root.geometry("1000x800")
        self.root.title("Data structures and TKInter practices")

        # General styles
        self.style = ttk.Style()
        self.style.configure('TLabel', background='white', font=('Consolas', 12))
        self.style.configure('Header.TLabel', font=('Arial', 18, 'bold'))
        self.style.configure('GREY.TLabel', font=('Consolas', 12, 'italic'))
        self.style.configure("Treeview", font=('consolas', 12))
        self.style.configure("Treeview.Heading", font=('consolas', 12, "bold"))
        self.style.configure("TButton", font=('consolas', 12, "bold"))

        # Main menu
        self.menu_font = ('Consolas', 10)
        self.root.option_add('*tearOff', False)  # Remove automatic separator lines
        self.main_menubar = Menu(self.root)
        self.main_menubar.config(font=self.menu_font)
        self.root.config(menu=self.main_menubar)

        # Data menu
        self.menu_item_stats = Menu(self.main_menubar)
        self.menu_item_stats.config(font=self.menu_font)
        self.main_menubar.add_cascade(menu=self.menu_item_stats, label="Data")
        self.menu_item_stats.add_command(label="Corona Virus", font=self.menu_font, command=self.corona_info)
        self.menu_item_stats.add_command(label="Earthquakes Magnitude > 2.5", font=self.menu_font, command=self.earthquake_info)

        # Main loop
        self.root.mainloop()

    def corona_info(self):
        corona_window = CoronaInfo(self.root)

    def earthquake_info(self):
        earthquake_window = EarthquakeInfo(self.root)


def main():
    demo = DataStructures()


if __name__ == "__main__":
    main()
