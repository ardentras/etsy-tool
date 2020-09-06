###########################################################
# Filename: get_price.py
# Author: Shaun Rasmusen <shaunrasmusen@gmail.com>
# Date: 09/05/2020
#
# GetPrice modal
#

from collections import Counter

import src.etsy_vars as ev
import src.helpers as helpers

import json
import requests
import threading
import tkinter as tk
import tkinter.ttk as ttk
import queue
import urllib
import webbrowser

class ThreadedEtsyGetPriceTask(threading.Thread):
    def __init__(self, queue, url):
        threading.Thread.__init__(self)
        self.queue = queue
        self.url = url

    def run(self):
        info = {}
        try:
            params = {
                'uri': urllib.parse.quote(self.url)
            }
            headers = {
                'origin': 'https://www.flippertools.com',
                'referer': 'https://www.flippertools.com/tools/etsySoldPrice/etsy-sold-price.htm',
                'user-agent': 'Mozilla/5.0',
                'accept': 'application/json, text/javascript, */*; 1',
                'cache-control': 'no-cache',
                'pragma': 'no-cache'
            }

            response = json.loads(requests.get("https://api.flippertools.com/api/etsy", params=params, headers=headers).text)

            info = response["results"]
        except Exception as e:
            print(e)
                
        self.queue.put(info)

class GetPrice(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)

        self.master = master
        self.focus()
        self.resizable(False, False)
        self.title("Rank Tags")
        self.bind("<Return>", self.runQuery)
        self.bind("<Escape>", self.exit)
        self.create_widgets()

    def exit(self, event):
        event.widget.winfo_toplevel().destroy()

    def create_widgets(self):
        currRow=0
        self.titleL = tk.Label(self, text="Retrieve Price From Listing", fg="black", bg="white")
        self.titleL.grid(row=currRow, column=0, columnspan=5)

        currRow=currRow+1
        self.urlL = tk.Label(self, text="Listing URL:", fg="black", bg="white")
        self.urlL.grid(row=currRow, column=0, sticky="e")
        self.urlEntry = tk.Entry(self, takefocus=True, width=32)
        self.urlEntry.bind(helpers.ctlA(), helpers.selectAllCallback)
        self.urlEntry.bind("<Return>", self.runQuery)
        self.urlEntry.grid(row=currRow, column=1, columnspan=3)

        currRow=currRow+1
        self.listingTitle = tk.Label(self, text="")
        self.listingTitle.grid(row=currRow, column=1, columnspan=4)

        currRow=currRow+1
        self.link = tk.Label(self, text="", fg="blue", cursor="hand1", justify="left")
        self.link.grid(row=currRow, column=1, columnspan=4)
        
        currRow=currRow+1
        self.sold = tk.Label(self, text="Sold for: ", justify="right")
        self.sold.grid(row=currRow, column=1, columnspan=1)
        self.priceHigh = tk.Label(self, text="")
        self.priceHigh.grid(row=currRow, column=2, columnspan=1)
        self.priceLow = tk.Label(self, text="")
        self.priceLow.grid(row=currRow, column=3, columnspan=1)

        currRow=currRow+1
        self.aSpacer = tk.Frame(self, height=10)
        self.aSpacer.grid(row=currRow, column=0)

        currRow=currRow+1
        self.loading = ttk.Progressbar(self)
        self.loading.grid(row=currRow, column=0, columnspan=5)
        # the load_bar needs to be configured for indeterminate amount of bouncing
        self.loading.config(mode='determinate', maximum=100, value=0, length = 400)

        currRow=currRow+1
        self.help = tk.Button(self, text="Help", fg="red", command=self.getHelp)
        self.help.grid(row=currRow, column=0)
        self.quit = tk.Button(self, text="Go Back", fg="red", command=self.destroy)
        self.quit.grid(row=currRow, column=1, sticky="ew")
        self.submit = tk.Button(self, text="Get Price", fg="red", command=self.runQuery)
        self.submit.grid(row=currRow, column=3, sticky="ew")
        
    def getHelp(self, *args):
        currRow=0
        helpModal = tk.Toplevel()
        helpModal.focus()
        helpModal.resizable(False, False)
        helpModal.bind("<Escape>", self.exit)
        helpModal.bind("<Return>", self.exit)
        helpModal.title("Help: Retrieve Tags")

        infotext="""
Enter the Listing URL to retreive its price.
        """
        hotkeytext="""
Hotkeys:
Press <Return> to submit the query
Press <Escape> to exit subcommand
        """
        helpModal.info = tk.Label(helpModal, text=infotext, justify="left", padx=15)
        helpModal.info.grid(row=currRow, column=0, sticky="ew")
        currRow=currRow+1
        helpModal.info = tk.Label(helpModal, text=hotkeytext, justify="center", padx=15)
        helpModal.info.grid(row=currRow, column=0, sticky="ew")

        currRow=currRow+1
        helpModal.exit = tk.Button(helpModal, text="Back", command=helpModal.destroy)
        helpModal.exit.grid(row=currRow, column=0)

    def runQuery(self, *args):
        if len(self.urlEntry.get()) == 0:
            currRow=0
            errModal = tk.Toplevel()
            errModal.focus()
            errModal.resizable(False, False)
            errModal.bind("<Escape>", self.exit)
            errModal.bind("<Return>", self.exit)
            errModal.title("Error")

            infotext="""
No listing URL provided. 
Please enter an URL to query.
            """
            errModal.info = tk.Label(errModal, text=infotext, justify="center", padx=15)
            errModal.info.grid(row=currRow, column=0, sticky="ew")
            currRow=currRow+1
            errModal.exit = tk.Button(errModal, text="Okay", command=errModal.destroy)
            errModal.exit.grid(row=currRow, column=0)

            return
    

        self.priceHigh.configure(text="")
        self.priceLow.configure(text="")
        self.listingTitle.configure(text="")
        self.link.configure(text="")

        url = self.urlEntry.get()
        if url.find("listing/") >= 0:
            start = url.find("listing/") + len("listing/")
            end = url.find("/", start)
            listingID = url[start:end]

        # 8 here is for speed of bounce
        self.loading.start()

        self.queryQueue = queue.Queue()
        ThreadedEtsyGetPriceTask(self.queryQueue, url).start()
        self.master.after(100, self.processQuery)

        self.link.configure(text="View Listing #%s" % (listingID))
        self.link.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.etsy.com/listing/%s" % (listingID)))

    def processQuery(self):
        try:
            info = self.queryQueue.get(0)

            if info:
                self.listingTitle.configure(text=info['title'][:40])
                if info['highPrice'] != info['lowPrice']:
                    self.priceHigh.configure(text="High: %d %s" % (info['highPrice'], info['currency']))
                    self.priceLow.configure(text="Low: %d %s" % (info['lowPrice'], info['currency']))
                else:
                    self.priceHigh.configure(text="%d %s" % (info['highPrice'], info['currency']))
            else:
                self.listingTitle.configure(text="Failed to retreive listing")

            self.loading.stop()

        except queue.Empty:
            self.master.after(100, self.processQuery)
