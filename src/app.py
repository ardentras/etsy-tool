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

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Etsy Tool")
        self.master.minsize(width=200, height=200)
        self.master.maxsize(width=200, height=200)

        self.ranktags = None
        self.gettags = None

        self.create_widgets()
        self.pack()

    def create_widgets(self):
        currRow = 0
        self.title = tk.Label(self, text="Etsy Tool")
        self.title.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.aSpacer = tk.Frame(self, height=10)
        self.aSpacer.grid(row=currRow, column=0)
        self.ranktags = tk.Button(self, text="Rank Tags", fg="black", command=self.runRankTags)
        self.ranktags.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.gettags = tk.Button(self, text="Retreive Tags", fg="black", command=self.runGetTags)
        self.gettags.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.getprice = tk.Button(self, text="Retreive Price", fg="black", command=self.runGetPrice)
        self.getprice.grid(row=currRow, column=0)
        currRow = currRow + 1

        self.aSpacer2 = tk.Frame(self, height=25)
        self.aSpacer2.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.grid(row=currRow, column=0)
        currRow = currRow + 1

        self.aSpacer3 = tk.Frame(self, height=10)
        self.aSpacer3.grid(row=currRow, column=0)
        currRow = currRow + 1
        self.requestsUsed = tk.Label(self, font=(None, 10), text="0 / %d requests used (0%%)" % (ev.maxreq), )
        self.requestsUsed.grid(row=currRow, column=0)
        currRow = currRow + 1
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