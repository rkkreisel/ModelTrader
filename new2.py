# Import the library tkinter
from tkinter import *
  
# Create a GUI app
app = Tk()
  
# Give a title to your app
app.title("Vinayak App")
  
# Constructing the first frame, frame1
frame1 = LabelFrame(app, text="Fruit", bg="green",
                    fg="white", padx=15, pady=15)
  
# Displaying the frame1 in row 0 and column 0
frame1.grid(row=0, column=0)
  
# Constructing the button b1 in frame1
b1 = Button(frame1, text="Apple")
  
# Displaying the button b1
b1.pack()
  
# Constructing the second frame, frame2
frame2 = LabelFrame(app, text="Vegetable", bg="yellow", padx=15, pady=15)
  
# Displaying the frame2 in row 0 and column 1
frame2.grid(row=0, column=1)
  
# Constructing the button in frame2
b2 = Button(frame2, text="Tomato")
  
# Displaying the button b2
b2.pack()