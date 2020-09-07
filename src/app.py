###########################################################
# Filename: app.py
# Author: Shaun Rasmusen <shaunrasmusen@gmail.com>
# Date: 09/04/2020
#
# Main application gui
#

import src.etsy_vars as ev
import src.get_tags as get_tags
import src.rank_tags as rank_tags
import src.get_price as get_price

import os
import re
import tkinter as tk
import tkinter.ttk as ttk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Etsy Tool")
        self.master.minsize(width=300, height=300)
        self.master.resizable(False, False)

        self.ranktags = None
        self.gettags = None

        self.create_styles()
        self.create_widgets()
        self.master.configure()
        self.configure()
        self.pack()

    def create_styles(self):
        self.master.style = ttk.Style()
        self.master.style.theme_use('clam')
        self.master.style.configure('TProgressbar', foreground=ev.orange, background=ev.orange, troughcolor="white")
        self.master.style.configure('h1.TLabel', foreground=ev.orange, background='white', font=("Georgia", 48, "bold"))
        self.master.style.configure('h2.TLabel', foreground=ev.orange, background='white', font=("Georgia", 32, "bold"), justify='center')
        self.master.style.configure('p.TLabel', background='white', font=("Roboto", 14))
        self.master.style.configure('footer.TLabel', foreground=ev.orange, background='white', font=("Georgia", 10))
        self.master.style.configure('TButton', font=("Roboto", 12), bordercolor="#666")
        self.master.style.configure('Main.TButton', font=("Roboto", 16), bordercolor="#666", padding=(10, 10))
        self.master.style.map('TButton',
            background=[('active', 'pressed', '#ccc'),
                        ('active', '#f0f0f0'),
                        ('!pressed', '#fff'),
                        ],
            relief    =[('pressed', 'sunken'),
                        ('!pressed', 'ridge')])


    def create_widgets(self):
        currRow = 0
        self.titleL = ttk.Label(self, text="Etsy Tool", style='h1.TLabel')
        self.titleL.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.aSpacer = tk.Frame(self, height=40)
        self.aSpacer.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.ranktags = ttk.Button(self, text="Rank Tags", command=self.runRankTags, style='Main.TButton')
        self.ranktags.grid(row=currRow, column=0)
        currRow = currRow + 1

        self.aSpacer5 = tk.Frame(self, height=10)
        self.aSpacer5.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.getprice = ttk.Button(self, text="Retreive Price", command=self.runGetPrice, style='Main.TButton')
        self.getprice.grid(row=currRow, column=0)
        currRow = currRow + 1

        self.aSpacer6 = tk.Frame(self, height=10)
        self.aSpacer6.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.gettags = ttk.Button(self, text="Get Listing Info", command=self.runGetTags, style='Main.TButton')
        self.gettags.grid(row=currRow, column=0)
        currRow = currRow + 1

        self.aSpacer2 = tk.Frame(self, height=25)
        self.aSpacer2.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.quit = ttk.Button(self, text="Quit", command=self.master.destroy, style='Main.TButton')
        self.quit.grid(row=currRow, column=0)
        currRow = currRow + 1

        self.aSpacer3 = tk.Frame(self, height=10)
        self.aSpacer3.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.requestsUsed = ttk.Label(self, text="0 / %d requests used (0%%)" % (ev.maxreq), style='footer.TLabel')
        self.requestsUsed.grid(row=currRow, column=0, sticky="s")
        currRow = currRow + 1

        self.aSpacer4 = tk.Frame(self, height=10)
        self.aSpacer4.grid(row=currRow, column=0)
        self.updateRequestCountWidget()

    def updateRequestCountWidget(self):
        count = 0
        filename_re = r'.etsy-tool*'
        for filename in os.listdir('.'):
            if re.search(filename_re, filename):
                with open(filename, 'r') as infile:
                    count = int(infile.read())

        self.requestsUsed.configure(text="%d / %d requests used (%d%%)" % (count, ev.maxreq, int(count * 100 / ev.maxreq)))

        self.master.after(1000, self.updateRequestCountWidget)

    def runRankTags(self):
        self.ranktags = rank_tags.RankTags(self)

    def runGetTags(self):
        self.gettags = get_tags.GetTags(self)
    
    def runGetPrice(self):
        self.getprice = get_price.GetPrice(self)