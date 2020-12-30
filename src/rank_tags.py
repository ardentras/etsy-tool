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
        self.configure(bg="white")
        self.create_widgets()

    def exit(self, event):
        event.widget.winfo_toplevel().destroy()

    def create_widgets(self):
        currRow = 0
        self.titleL = ttk.Label(self, text="Rank Tags", style='h2.TLabel')
        self.titleL.grid(row=currRow, column=0, columnspan=9)
        currRow = currRow + 1
        self.aSpacer3 = tk.Frame(self, height=30)
        self.aSpacer3.grid(row=currRow, column=0, columnspan=9)

        currRow=currRow+1
        self.pagesL = ttk.Label(self, text="# Pages:", style='p.TLabel')
        self.pagesL.grid(row=currRow, column=1, sticky="e")
        self.pageEntry = tk.Spinbox(self, from_=1, to=100, width=3)
        self.pageEntry.grid(row=currRow, column=3, sticky="w")

        currRow=currRow+1
        self.tagsL = ttk.Label(self, text="Tag:", style='p.TLabel')
        self.tagsL.grid(row=currRow, column=1, sticky="e")
        self.tagsEntry = tk.Entry(self, takefocus=True, width=30)
        self.tagsEntry.bind("<Return>", self.addTag)
        self.tagsEntry.bind(helpers.ctlA(), helpers.selectAllCallback)
        self.tagsEntry.grid(row=currRow, column=3, columnspan=3)
        self.tagButton = ttk.Button(self, text="Add Tag", command=self.addTag)
        self.tagButton.grid(row=currRow, column=7, sticky="ew")

        currRow = currRow + 1
        self.aSpacer4 = tk.Frame(self, height=10)
        self.aSpacer4.grid(row=currRow, column=0, columnspan=9)
        
        currRow=currRow+1
        self.tagsList = tk.Listbox(self, width=57)
        self.tagsList.bind("<Double-Button-1>", self.removeTag)
        self.tagsList.grid(row=currRow, column=1, columnspan=7)
        self.scrollbar = tk.Scrollbar(self, orient="vertical")
        self.scrollbar.grid(row=currRow, column=8, sticky="nese")
        self.tagsList.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.tagsList.yview)

        currRow=currRow+1
        self.loading = ttk.Progressbar(self)
        self.loading.grid(row=currRow, column=1, columnspan=7)
        # the load_bar needs to be configured for indeterminate amount of bouncing
        self.loading.config(mode='determinate', maximum=100, value=0, length = 515)

        currRow = currRow + 1
        self.aSpacer = tk.Frame(self, height=10)
        self.aSpacer.grid(row=currRow, column=2)
        currRow=currRow+1
        self.help = ttk.Button(self, text="Help", command=self.getHelp)
        self.help.grid(row=currRow, column=1)
        self.quit = ttk.Button(self, text="Go Back", command=self.destroy)
        self.quit.grid(row=currRow, column=3, sticky="w")
        self.submit = ttk.Button(self, text="Get Tags", command=self.runQuery)
        self.submit.grid(row=currRow, column=7, sticky="ew")
        currRow = currRow + 1
        self.aSpacer2 = tk.Frame(self, height=10, width=15)
        self.aSpacer2.grid(row=currRow, column=0)

    def getHelp(self, *args):
        currRow = 0
        helpModal = tk.Toplevel(bg="white")
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
        if len(self.tagsList.get(0, "end")) == 0:
            currRow = 0
            errModal = tk.Toplevel(bg="white")
            errModal.focus()
            errModal.resizable(False, False)
            errModal.bind("<Escape>", self.exit)
            errModal.bind("<Return>", self.exit)
            errModal.title("Error")

            infotext="""
No tags provided. 
Please enter at least one tag to query.
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

        # 8 here is for speed of bounce
        self.loading.start()

        self.queryQueue = queue.Queue()
        ThreadedEtsyRankTagsTask(self.queryQueue, self.tagsList.get(0, "end"), self.pageEntry.get()).start()
        self.master.after(100, self.processQuery)

    def processQuery(self):
        try:
            currRow = 0
            tags = self.queryQueue.get(0)
            tagsListModal = tk.Toplevel(bg="white")
            tagsListModal.focus()
            tagsListModal.resizable(False, False)
            tagsListModal.bind("<Escape>", self.exit)
            tagsListModal.bind("<Return>", self.exit)
            tagsListModal.title("Tag List")
            tagsListModal.titleL = ttk.Label(tagsListModal, text="Results\n", style='h2.TLabel')
            tagsListModal.titleL.grid(row=currRow, column=1)
            currRow=currRow+1
            tagsListModal.aSpacer3 = tk.Frame(tagsListModal, height=20, bg="white")
            tagsListModal.aSpacer3.grid(row=currRow, column=0)

            if len(tags) == 0:
                currRow=currRow+1
                tagsListModal.error = ttk.Label(tagsListModal, text="\nNo tags found for search   \n\n", style='p.TLabel', bg="white")
                tagsListModal.error.grid(row=currRow, column=1)
            else:

                uniqTags = []
                counterTags = Counter(tags)
                for uniqTag in counterTags.keys():
                    uniqTags.append("%s %s" % (counterTags[uniqTag], uniqTag))

                uniqTags.sort(key=numericSort, reverse=True)

                tagsListModal.tagList = tk.Listbox(tagsListModal, width=48, height=20, selectmode="extended")
                for tag in uniqTags:
                    tagsListModal.tagList.insert("end", "   " + tag)

                currRow=currRow+1
                tagsListModal.tagList.grid(row=currRow, column=1)

                tagsListModal.scrollbar = tk.Scrollbar(tagsListModal, orient="vertical")
                tagsListModal.scrollbar.grid(row=currRow, column=2, sticky="nese")
                tagsListModal.tagList.config(yscrollcommand=tagsListModal.scrollbar.set, bg="white")
                tagsListModal.scrollbar.config(command=tagsListModal.tagList.yview)

            currRow=currRow+1
            tagsListModal.aSpacer2 = tk.Frame(tagsListModal, height=10, width=15, bg="white")
            tagsListModal.aSpacer2.grid(row=currRow, column=0)
            currRow=currRow+1
            tagsListModal.exit = ttk.Button(tagsListModal, text="Done", command=tagsListModal.destroy)
            tagsListModal.exit.grid(row=currRow, column=1)
            currRow = currRow + 1
            tagsListModal.aSpacer = tk.Frame(tagsListModal, height=10, bg="white")
            tagsListModal.aSpacer.grid(row=currRow, column=2)

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

        self.scrollbar.config(command=self.tagsList.yview)

        self.tagsEntry.delete(first=0, last="end")