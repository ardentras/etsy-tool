###########################################################
# Filename: get_tags.py
# Author: Shaun Rasmusen <shaunrasmusen@gmail.com>
# Date: 09/04/2020
#
# GetTags modal
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
import webbrowser

class ThreadedEtsyGetTagsTask(threading.Thread):
    def __init__(self, queue, listingID):
        threading.Thread.__init__(self)
        self.queue = queue
        self.listingID = listingID

    def run(self):
        tags = []
        try:
            params = {
                'api_key': ev.api_key
            }

            response = json.loads(requests.get("https://openapi.etsy.com/v2/listings/%s" % (self.listingID), params).text)

            helpers.updateRequestCount(1)

            for result in response["results"]:
                for tag in result["tags"]:
                    tags.append(tag)
        except Exception as e:
            print(e)
                
        self.queue.put(tags)

class GetTags(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.tagsEntryMaxLen = 1024

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
        self.title = tk.Label(self, text="Retrieve Tags From Listing", fg="black", bg="white")
        self.title.grid(row=currRow, column=0, columnspan=5)

        currRow=currRow+1
        self.idL = tk.Label(self, text="Listing ID / URL:", fg="black", bg="white")
        self.idL.grid(row=currRow, column=0, sticky="e")
        self.idEntry = tk.Entry(self, takefocus=True, width=32)
        self.idEntry.bind(helpers.ctlA(), helpers.selectAllCallback)
        self.idEntry.grid(row=currRow, column=1, columnspan=3)

        currRow=currRow+1
        self.link = tk.Label(self, text="", fg="blue", cursor="hand1", justify="left")
        self.link.grid(row=currRow, column=1, columnspan=4)
        
        currRow=currRow+1
        self.tagsList = tk.Listbox(self, width=48, height=15, selectmode="extended")
        self.tagsList.grid(row=currRow, column=0, columnspan=5)

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
        self.submit = tk.Button(self, text="Get Tags", fg="red", command=self.runQuery)
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
Enter the Listing ID or URL to retreive all tags for a listing.

The listing ID is the number immediately following etsy.com/listing/
in the address bar.
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
        if len(self.idEntry.get()) == 0:
            currRow=0
            errModal = tk.Toplevel()
            errModal.focus()
            errModal.resizable(False, False)
            errModal.bind("<Escape>", self.exit)
            errModal.bind("<Return>", self.exit)
            errModal.title("Error")

            infotext="""
No listing ID provided. 
Please enter an ID to query.
            """
            errModal.info = tk.Label(errModal, text=infotext, justify="center", padx=15)
            errModal.info.grid(row=currRow, column=0, sticky="ew")

            currRow=currRow+1
            errModal.exit = tk.Button(errModal, text="Okay", command=errModal.destroy)
            errModal.exit.grid(row=currRow, column=0)

            return
	
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

        self.link.configure(text="View Listing #%s" % (listingID))
        self.link.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.etsy.com/listing/%s" % (listingID)))

    def processQuery(self):
        try:
            tags = self.queryQueue.get(0)

            for tag in tags:
                self.tagsList.insert("end", "   " + tag)

            self.loading.stop()

        except queue.Empty:
            self.master.after(100, self.processQuery)
