from tkinter import *
import shutil
from PIL import ImageTk, Image
from tkinter import filedialog
import tkinter.messagebox as tmsg
from subprocess import call

def register():
    try:
        call(["python", "registerGUI.py"])
    except Exception as e:
        tmsg.showerror("Error", f"Failed to run register script: {e}")

def VideoSurveillance():
    try:
        call(["python", "surveillance.py"])
    except Exception as e:
        tmsg.showerror("Error", f"Failed to run surveillance script: {e}")

def detectCriminal():
    try:
        call(["python", "detect.py"])
    except Exception as e:
        tmsg.showerror("Error", f"Failed to run detect script: {e}")

root = Tk()
root.geometry('800x500')
root.minsize(800, 500)
root.maxsize(800, 500)
root.title("CFIS- Criminal Face Identification System")
root.configure(bg="#382273")

image_path = "image.jpg"
try:
    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)
    photo_label = Label(image=photo, width=800, height=0, bg='white').place(x=0, y=0)
except Exception as e:
    tmsg.showerror("Error", f"Failed to load background image: {e}")

label_0 = Label(
    root,
    text="Criminal Face Identification System",
    width=50,
    font=("bold", 20),
    anchor=CENTER,
    bg="#386184",
    fg="white",
)
label_0.place(x=0, y=100)

Button(
    root, 
    text='REGISTER CRIMINAL', 
    width=35, 
    height=3, 
    bg='blue', 
    fg='white', 
    font=("bold", 11), 
    command=register
).place(x=250, y=180)

Button(
    root, 
    text='PHOTO MATCH', 
    width=35, 
    height=3, 
    bg='blue', 
    fg='white', 
    font=("bold", 11), 
    command=detectCriminal
).place(x=250, y=260)

Button(
    root, 
    text='VIDEO SURVEILLANCE', 
    width=35, 
    height=3, 
    bg='red', 
    fg='white', 
    font=("bold", 11), 
    command=VideoSurveillance
).place(x=250, y=340)

root.mainloop()
