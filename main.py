#!/usr/bin/env python3
###########################################################
# Filename: main.py
# Author: Shaun Rasmusen <shaunrasmusen@gmail.com>
# Date: 09/04/2020
#
# Entrypoint for running from the command line.
#

import src.app as a
import src.helpers as helpers
import tkinter as tk

helpers.updateRequestCount(0)

root = tk.Tk()
app = a.Application(master=root)
app.mainloop()