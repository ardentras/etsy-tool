###########################################################
# Filename: rank_tags.py
# Author: Shaun Rasmusen <shaunrasmusen@gmail.com>
# Date: 09/04/2020
#
# RankTags modal
#

from collections import Counter

import src.etsy_vars as ev
import src.helpers as helpers

import json
import queue
import re
import requests
import threading
import tkinter as tk
import tkinter.ttk as ttk

def numericSort(e):
    return int(e[:e.find(" ")])

class ThreadedEtsyRankTagsTask(threading.Thread):
    def __init__(self, queue, tags, pages):
        threading.Thread.__init__(self)
        self.queue = queue
        self.tags = tags
        self.pages = pages

    def run(self):
        taglist = ""

        for tag in self.tags:
            tag = tag.lstrip()
            tag = tag.rstrip()
            taglist = taglist + re.sub(r'[^A-Za-z0-9 ]+', '', tag) + ","

        taglist = taglist[:-1]

        print(taglist)  

        tags = []
        for i in range(int(self.pages)):
            offset = i * ev.page_limit
            params = {
                'api_key': ev.api_key, 
                'tags': taglist, 
                'sort_on': 'score',
                'limit': ev.page_limit, 
                'offset': offset
            }
            try:
                thejson = requests.get("https://openapi.etsy.com/v2/listings/active", params).text
                response = json.loads(thejson)
                
                helpers.updateRequestCount(1)

                ids = ""
                for result in response["results"]:
                    ids = "%s%d%s" % (ids, result["listing_id"], ",")

                if len(ids) == 0:
                    break

                ids = ids[:-1]

                params = {
                    'api_key': ev.api_key
                }

                response = json.loads(requests.get("https://openapi.etsy.com/v2/listings/%s" % (ids), params).text)

                helpers.updateRequestCount(1)

                for result in response["results"]:
                    for tag in result["tags"]:
                        tags.append(tag.lower())
            except Exception as e:
                print(e)
                break
                
        self.queue.put(tags)

class RankTags(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.tagsEntryMaxLen = 1024

        self.master = master
        self.focus()
        self.resizable(False, False)
        self.title("Rank Tags")
        self.bind(helpers.ctlEnter(), self.runQuery)
        self.bind("<Escape>", self.exit)
        self.create_widgets()

    def exit(self, event):
        event.widget.winfo_toplevel().destroy()

    def create_widgets(self):
        titlerow=0
        self.title = tk.Label(self, text="Rank Tags", fg="black", bg="white")
        self.title.grid(row=titlerow, column=0, columnspan=5)

        pagerow=titlerow+1
        self.pagesL = tk.Label(self, text="# Pages:")
        self.pagesL.grid(row=pagerow, column=0, sticky="e")
        self.pageEntry = tk.Spinbox(self, from_=1, to=100, width=3)
        self.pageEntry.grid(row=pagerow, column=1, sticky="w")

        labelrow=pagerow+1
        self.tagsL = tk.Label(self, text="Tag:", fg="black", bg="white")
        self.tagsL.grid(row=labelrow, column=0, sticky="e")
        self.tagsEntry = tk.Entry(self, takefocus=True, width=32)
        self.tagsEntry.bind("<Return>", self.addTag)
        self.tagsEntry.bind(helpers.ctlA(), helpers.selectAllCallback)
        self.tagsEntry.grid(row=labelrow, column=1, columnspan=3)
        self.tagButton = tk.Button(self, text="Add Tag", command=self.addTag)
        self.tagButton.grid(row=labelrow, column=4)
        
        listrow=labelrow+1
        self.tagsList = tk.Listbox(self, width=48)
        self.tagsList.bind("<Double-Button-1>", self.removeTag)
        self.tagsList.grid(row=listrow, column=0, columnspan=5)

        loadingrow=listrow+1
        self.loading = ttk.Progressbar(self)
        self.loading.grid(row=loadingrow, column=0, columnspan=5)
        # the load_bar needs to be configured for indeterminate amount of bouncing
        self.loading.config(mode='determinate', maximum=100, value=0, length = 400)

        buttonsrow=loadingrow+1
        self.help = tk.Button(self, text="Help", fg="red", command=self.getHelp)
        self.help.grid(row=buttonsrow, column=0)
        self.quit = tk.Button(self, text="Go Back", fg="red", command=self.destroy)
        self.quit.grid(row=buttonsrow, column=1, sticky="ew")
        self.submit = tk.Button(self, text="Get Tags", fg="red", command=self.runQuery)
        self.submit.grid(row=buttonsrow, column=3, sticky="ew")

    def getHelp(self, *args):
        helpModal = tk.Toplevel()
        helpModal.focus()
        helpModal.resizable(False, False)
        helpModal.bind("<Escape>", self.exit)
        helpModal.bind("<Return>", self.exit)
        helpModal.title("Help: Rank Tags")

        infotext="""
Select the number of pages to query using '# Pages'.
The more pages, the higher the sample size for ranking.

Enter tags using 'Tag'. Tags may contain whitespace.
Double click a tag to remove it from the list.
        """
        hotkeytext = """
Hotkeys:
Press <Return> to add a tag to the list
Press <%s + Return> to submit the query
Press <Escape> to exit subcommand
        """ % (helpers.getCtlShort())
        helpModal.info = tk.Label(helpModal, text=infotext, justify="left", padx=15)
        helpModal.info.grid(row=0, column=0, sticky="ew")
        helpModal.info = tk.Label(helpModal, text=hotkeytext, justify="center", padx=15)
        helpModal.info.grid(row=1, column=0, sticky="ew")

        helpModal.exit = tk.Button(helpModal, text="Back", command=helpModal.destroy)
        helpModal.exit.grid(row=2, column=0)

    def runQuery(self, *args):
        if len(self.tagsList.get(0, "end")) == 0:
            errModal = tk.Toplevel()
            errModal.focus()
            errModal.resizable(False, False)
            errModal.bind("<Escape>", self.exit)
            errModal.bind("<Return>", self.exit)
            errModal.title("Error")

            infotext="""
No tags provided. 
Please enter at least one tag to query.
            """
            errModal.info = tk.Label(errModal, text=infotext, justify="center", padx=15)
            errModal.info.grid(row=0, column=0, sticky="ew")

            errModal.exit = tk.Button(errModal, text="Okay", command=errModal.destroy)
            errModal.exit.grid(row=1, column=0)

            return

        # 8 here is for speed of bounce
        self.loading.start()

        self.queryQueue = queue.Queue()
        ThreadedEtsyRankTagsTask(self.queryQueue, self.tagsList.get(0, "end"), self.pageEntry.get()).start()
        self.master.after(100, self.processQuery)

    def processQuery(self):
        try:
            tags = self.queryQueue.get(0)
            tagsListModal = tk.Toplevel()
            tagsListModal.focus()
            tagsListModal.resizable(False, False)
            tagsListModal.bind("<Escape>", self.exit)
            tagsListModal.bind("<Return>", self.exit)

            if len(tags) == 0:
                tagsListModal.error = tk.Label(tagsListModal, text="\nNo tags found for search\n\n", justify="center", width=48)
                tagsListModal.error.grid(row=0, column=0)
            else:
                tagsListModal.good = tk.Label(tagsListModal, text="Rank Tags results\n", justify="center", width=48)
                tagsListModal.good.grid(row=0, column=0)

                uniqTags = []
                counterTags = Counter(tags)
                for uniqTag in counterTags.keys():
                    uniqTags.append("%s %s" % (counterTags[uniqTag], uniqTag))

                uniqTags.sort(key=numericSort, reverse=True)

                tagsListModal.tagList = tk.Listbox(tagsListModal, width=48, height=20, selectmode="extended")
                for tag in uniqTags:
                    tagsListModal.tagList.insert("end", "   " + tag)

                tagsListModal.tagList.grid(row=1, column=0)
            tagsListModal.exit = tk.Button(tagsListModal, text="Done", command=tagsListModal.destroy)
            tagsListModal.exit.grid(row=2, column=0)

            self.loading.stop()

        except queue.Empty:
            self.master.after(100, self.processQuery)


    def removeTag(self, *args):
        tags = self.tagsList.curselection()

        self.tagsList.delete(tags)

    def addTag(self, *args):
        tag = self.tagsEntry.get()

        if len(tag) > 0:
            self.tagsList.insert("end", "   " + tag)

        self.tagsEntry.delete(first=0, last="end")