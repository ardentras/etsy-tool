from datetime import datetime
import os
import platform
import re
import tkinter as tk

def ctlA():
    if platform.system() == "Darwin":
        return "<Command-a>"
    else:
        return "<Control-a>"

def ctlEnter():
    if platform.system() == "Darwin":
        return "<Command-Return>"
    else:
        return "<Control-Return>"

def getCtlShort():
    if platform.system() == "Darwin":
        return "Cmd"
    else:
        return "Ctl"

def select_all(widget):
    # select text
    widget.select_range(0, 'end')
    # move cursor to the end
    widget.icursor('end')

def selectAllCallback(event):
    event.widget.master.after(10, select_all, event.widget)

def updateRequestCount(inc):
    found = False
    oldfilename = ''
    newfilename = '.etsy-tool-%s' % (datetime.today().strftime('%Y%m%d'))

    filename_re = r'.etsy-tool*'
    for filename in os.listdir('.'):
        if re.search(filename_re, filename):
            oldfilename = filename
            found = True

    count = 0
    filename = ''
    if found:
        if newfilename > oldfilename:
            os.remove(oldfilename)
            filename = newfilename
        else:
            filename = oldfilename

            with open(filename, 'r') as infile:
                count = int(infile.read())
    else:
        filename = newfilename

    with open(filename, 'w') as outfile:
        outfile.write(str(count + inc))
        