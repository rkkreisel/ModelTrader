import tkinter as tk


class Indicator():
    def __init__(self, master: tk.Tk, name: str, value: str,col: int):
        frame = tk.Frame(master,bg='red')
        self.data = tk.IntVar()                                                         # store integer variables
        self.data.set(value)                                                            # set value of self.data
        nameLabel = tk.Label(master=frame, text=name + ":", anchor="w", padx=5)
        nameLabel.grid(row=0, column=0, sticky="ew")
        valueLabel = tk.Label(master=frame, textvariable=self.data, anchor="e", padx=5)
        valueLabel.grid(row=0, column=1, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.pack(fill=tk.X)

    def update(self, value: str):
        self.data.set(value)
