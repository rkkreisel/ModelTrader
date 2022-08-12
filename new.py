import asyncio
from sys import exit as sys_exit
import sys
from ib_insync import IB, util, objects, Ticker, Watchdog
from datetime import *
import tkinter as tk
import pytz
from datetime import datetime, timedelta
import random
from indicator import Indicator
root = tk.Tk()
root.title("My First GUI")

#root.minsize(width=300, height=100)
root.geometry('800x800')
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)


frame1 = tk.LabelFrame(root, text="This is my Frame1", width=300, height=300, padx=5, pady=5)
frame1.pack(padx=10, pady=10)
frame2 = tk.LabelFrame(root, text="This is my Frame2", padx=5, pady=5)
#frame2.pack(padx=10, pady=10)

frame1.grid(row=0, column=0, sticky="nsew")
frame2.grid(row=1, column=1, sticky="nsew")

label4 = Indicator(frame1, "Positions","",1)
shares = Indicator(frame1, "Shares", "",1)
qtrhour = Indicator(frame1, "Time of Check","",1)
connected = Indicator(frame1, "Connected", "True",1)
contract = Indicator(frame1, "Contract", "",1)
label3 = Indicator(frame1, "15 Minutes ","",1)
crossover = Indicator(frame1, "Crossover", "False",1)
spread = Indicator(frame1, "CCI/CCIA Spread","",1)

cci15 = Indicator(frame1, "CCI      ", "",1)        
cci15_av = Indicator(frame1, "CCI Avg ", "",1)
atr15 = Indicator(frame1, "ATR ", "",1)
bband15_width = Indicator(frame1, "BBAND Width", "",1)
bband15_b = Indicator(frame1, "BBAND %B ", "",1)
label1 = Indicator(frame1, " ","",1)
cci15p = Indicator(frame1, "CCI ", "",1)
cci15p_av = Indicator(frame1, "CCIP Avg", "",1)
            
label2 = Indicator(frame1, "1 Hour ","",1)
cci1h = Indicator(frame1, "CCI ", "",2)
cci1h_av = Indicator(frame1, "CCI Avg ","",2)
atr1h = Indicator(frame1, "ATR ","",2)
bband1h_width = Indicator(frame1, "BBand Width ","",2)
bband1h_b = Indicator(frame1, "BBand %p ","",2)

label1 = Indicator(frame1, "1 Day ","",1)
cci1d = Indicator(frame1, "CCI ", "",3)
cci1d_av = Indicator(frame1, "CCI Avg ","",3)
atr1d = Indicator(frame1, "ATR ","",3)
bband1d_width = Indicator(frame1, "BBand Width ","",3)
bband1d_b = Indicator(frame1, "BBand %p ","",3)
status1 = Indicator(frame1, "Status1 ","",0)

frame1.grid(row=0, column=0)
frame2.grid(row=0, column=1)

text1 = tk.Text(frame2, height=10, width=250)
text1.insert(tk.INSERT,"line 1")
text1.insert(tk.INSERT,"line 2 and more more more")
text1.config(state="disabled")
#text1.pack()
text1.grid()


