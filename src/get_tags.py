###########################################################
# Filename: get_tags.py
# Author: Shaun Rasmusen <shaunrasmusen@gmail.com>
# Date: 09/04/2020
#
# GetTags modal
#

from collections import Counter
from datetime import datetime

import src.etsy_vars as ev
import src.helpers as helpers

import json
import requests
import threading
import tkinter as tk
import tkinter.ttk as ttk
import queue
import webbrowser

class ThreadedEtsyGetTagsTask(threading.Thread):
    def __init__(self, queue, listingID):
        threading.Thread.__init__(self)
        self.queue = queue
        self.listingID = listingID

    def run(self):
        data = {}
        data['title'] = ''
        data['listing_id'] = 0
        data['tags'] = []
        data['views'] = 0
        data['made'] = 0
        data['sold'] = 0
        data['failed'] = False
        try:
            params = {
                'api_key': ev.api_key
            }

            response = json.loads(requests.get("https://openapi.etsy.com/v2/listings/%s" % (self.listingID), params).text)

            helpers.updateRequestCount(1)

            for result in response["results"]:
                data['title'] = result['title'][:32]
                if len(result['title']) > 32:
                    data['title'] = data['title'] + '...'
                data['listing_id'] = result['listing_id']
                data['views'] = result['views']
                data['made'] = result['original_creation_tsz']
                if result['state'] == 'sold_out':
                    data['sold'] = result['state_tsz']

                for tag in result["tags"]:
                    data['tags'].append(tag)

                    
        except Exception as e:
            data['failed'] = True
            print(e)

        self.queue.put(data)

class GetTags(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.tagsEntryMaxLen = 1024

        self.master = master
        self.focus()
        self.resizable(False, False)
        self.title("Get Listing Info")
        self.bind("<Return>", self.runQuery)
        self.bind("<Escape>", self.exit)
        self.configure(bg="white")
        self.create_widgets()

    def exit(self, event):
        event.widget.winfo_toplevel().destroy()

    def create_widgets(self):
        currRow=0
        self.titleL = ttk.Label(self, text="Retrieve Info", style='h2.TLabel')
        self.titleL.grid(row=currRow, column=1, columnspan=5)

        currRow=currRow+1
        self.idL = ttk.Label(self, text="Listing ID / URL:", style='p.TLabel')
        self.idL.grid(row=currRow, column=1, sticky="e")
        self.idEntry = tk.Entry(self, takefocus=True, width=32)
        self.idEntry.bind(helpers.ctlA(), helpers.selectAllCallback)
        self.idEntry.grid(row=currRow, column=2, columnspan=3)

        currRow=currRow+1
        self.link = ttk.Label(self, text="", style='a.TLabel')
        self.link.grid(row=currRow, column=1, columnspan=5)

        currRow=currRow+1
        self.viewsL = ttk.Label(self, text="Views: n/a", style='p.TLabel', font=('Roboto', 12))
        self.viewsL.grid(row=currRow, column=1)
        self.createdL = ttk.Label(self, text="", style='p.TLabel', font=('Roboto', 12))
        self.createdL.grid(row=currRow, column=2, columnspan=2)
        self.soldL = ttk.Label(self, text="", style='p.TLabel', font=('Roboto', 12))
        self.soldL.grid(row=currRow, column=4, columnspan=2)
        
        currRow=currRow+1
        self.tagsList = tk.Listbox(self, width=48, height=15, selectmode="extended")
        self.tagsList.grid(row=currRow, column=1, columnspan=5)

        currRow=currRow+1
        self.loading = ttk.Progressbar(self)
        self.loading.grid(row=currRow, column=1, columnspan=5)
        # the load_bar needs to be configured for indeterminate amount of bouncing
        self.loading.config(mode='determinate', maximum=100, value=0, length = 434)

        currRow=currRow+1
        self.help = ttk.Button(self, text="Help", command=self.getHelp)
        self.help.grid(row=currRow, column=1)
        self.quit = ttk.Button(self, text="Go Back", command=self.destroy)
        self.quit.grid(row=currRow, column=2, sticky="ew")
        self.submit = ttk.Button(self, text="Get Info", command=self.runQuery)
        self.submit.grid(row=currRow, column=4, sticky="ew")

        currRow=currRow+1
        self.aSpacer2 = tk.Frame(self, height=10, width=15, bg="white")
        self.aSpacer2.grid(row=currRow, column=0)
        self.aSpacer3 = tk.Frame(self, height=10, width=15, bg="white")
        self.aSpacer3.grid(row=currRow, column=6)
        
    def getHelp(self, *args):
        currRow=0
        helpModal = tk.Toplevel(bg="white")
        helpModal.focus()
        helpModal.resizable(False, False)
        helpModal.bind("<Escape>", self.exit)
        helpModal.bind("<Return>", self.exit)
        helpModal.title("Help: Get Listing Info")

        infotext="""
Enter the Listing ID or URL to retrieve all tags, view count, creation, and
sold date for a listing.

If a listing is unavailable and no sold date is shown, then the listing
has been disabled or expired.
        """
        hotkeytext="""
Hotkeys:
Press <Return> to submit the query
Press <Escape> to exit subcommand
        """
        helpModal.info = tk.Label(helpModal, text=infotext, justify="left", padx=15, bg="white", font=('Roboto', 12))
        helpModal.info.grid(row=currRow, column=0, sticky="ew")
        currRow=currRow+1
        helpModal.info = tk.Label(helpModal, text=hotkeytext, justify="center", padx=15, bg="white", font=('Roboto', 12))
        helpModal.info.grid(row=currRow, column=0, sticky="ew")

        currRow=currRow+1
        helpModal.exit = ttk.Button(helpModal, text="Back", command=helpModal.destroy)
        helpModal.exit.grid(row=currRow, column=0)
        currRow=currRow+1
        helpModal.aSpacer = tk.Frame(helpModal, height=10, bg="white")
        helpModal.aSpacer.grid(row=currRow, column=0)

    def runQuery(self, *args):
        if len(self.idEntry.get()) == 0:
            currRow=0
            errModal = tk.Toplevel(bg="white")
            errModal.focus()
            errModal.resizable(False, False)
            errModal.bind("<Escape>", self.exit)
            errModal.bind("<Return>", self.exit)
            errModal.title("Error")

            infotext="""
No listing ID provided. 
Please enter an ID or URL to query.
            """
            errModal.info = tk.Label(errModal, text=infotext, justify="center", padx=15, bg="white", font=('Roboto', 12))
            errModal.info.grid(row=currRow, column=0, sticky="ew")

            currRow=currRow+1
            errModal.exit = ttk.Button(errModal, text="Okay", command=errModal.destroy)
            errModal.exit.grid(row=currRow, column=0)
            currRow=currRow+1
            errModal.aSpacer = tk.Frame(errModal, height=10, bg="white")
            errModal.aSpacer.grid(row=currRow, column=0)

            return
	
        self.viewsL.configure(text="Views: n/a")
        self.link.configure(text="")
        self.createdL.configure(text="")
        self.soldL.configure(text="")

        self.tagsList.delete(0, "end")
        listingID = self.idEntry.get()
        if listingID.find("listing/") >= 0:
            start = listingID.find("listing/") + len("listing/")
            end = listingID.find("/", start)
            listingID = listingID[start:end]

        # 8 here is for speed of bounce
        self.loading.start()

        self.queryQueue = queue.Queue()
        ThreadedEtsyGetTagsTask(self.queryQueue, listingID).start()
        self.master.after(100, self.processQuery)

    def processQuery(self):
        try:
            data = self.queryQueue.get(0)

            if data['failed']:
                self.link.configure(text="Failed to retrieve listing", cursor="arrow")
            else:
                self.link.configure(text="View Listing #%s: %s" % (data['listing_id'], data['title']))
                self.link.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.etsy.com/listing/%s" % (data['listing_id'])))

                self.viewsL.configure(text='Views: %d' % (data['views']))
                self.createdL.configure(text='Created: %s' % (datetime.fromtimestamp(data['made']).strftime('%m/%d/%Y')))
                if data['sold'] > 0:
                    self.soldL.configure(text='Sold: %s' % (datetime.fromtimestamp(data['sold']).strftime('%m/%d/%Y')))
                else:
                    self.soldL.configure(text='Not yet sold')

                for tag in data['tags']:
                    self.tagsList.insert("end", "   " + tag)

            self.loading.stop()

        except queue.Empty:
            self.master.after(100, self.processQuery)
