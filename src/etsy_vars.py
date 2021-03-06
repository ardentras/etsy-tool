###########################################################
# Filename: etsy_vars.py
# Author: Shaun Rasmusen <shaunrasmusen@gmail.com>
# Date: 09/04/2020
#
# Global variables for Esty API
#

import os

orange="#f1651f"
darkorange="#d14500"
lightorange="#f1853f"

etsy_api_key = ''
try:
    with open('.api_key', 'r') as infile:
        etsy_api_key = "".join(infile.read().split())
except:
    print("could not read api key")

api_key = os.getenv("ETSY_API_KEY", default=etsy_api_key)
page_limit = 25
maxreq = 5000