import cv2
import numpy as np
import sqlite3
import face_recognition as fr
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import os
import imutils
import math
import winsound

class App:
    def __init__(self, video_source=0):
        self.appname = "CFIS - Criminal Face Identification System"
        self.window = Tk()
        self.window.title(self.appname)
        self.window.geometry('1350x720')
        self.window.state("zoomed")
        self.window["bg"] = '#382273'
        self.video_source = video_source
        self.vid = VideoCapture(self.video_source)
        
        # UI Setup
        Label(self.window, text=self.appname, font=("bold", 20), bg='blue', fg='white').pack(side=TOP, fill=BOTH)
        self.canvas = Canvas(self.window, height=700, width=700, bg='#382273')
        self.canvas.pack(side=LEFT, fill=BOTH)

        self.detected_people = []
        self.images = self.load_images_from_folder("images")

        # Load and encode images
        self.encodings, self.known_face_names = self.encode_images()
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

        # Treeview setup
        self.tree = ttk.Treeview(self.window, column=("column1", "column2", "column3", "column4", "column5"), show='headings')
        self.setup_treeview()

        # Database connection
        self.conn = sqlite3.connect("criminal.db")
        self.cursor = self.conn.cursor()

        self.update()
        self.window.mainloop()

    def load_images_from_folder(self, folder):
        """Load all image filenames from the folder."""
        return [filename for filename in os.listdir(folder) if filename.endswith(('.png', '.jpg', '.jpeg'))]

    def encode_images(self):
        """Encode images and prepare known face names."""
        encodings = []
        names = []
        for img_name in self.images:
            img_path = os.path.join("images", img_name)
            try:
                image = fr.load_image_file(img_path)
                encoding = fr.face_encodings(image)
                if encoding:
                    encodings.append(encoding[0])
                    names.append((os.path.splitext(img_name)[0]).split('.')[1])
            except Exception as e:
                print(f"Error encoding image {img_name}: {e}")
        return encodings, names

    def setup_treeview(self):
        """Configure TreeView widget."""
        self.tree.heading("#1", text="Cr-ID")
        self.tree.column("#1", minwidth=0, width=70, stretch=NO)

        self.tree.heading("#2", text="NAME")
        self.tree.column("#2", minwidth=0, width=200, stretch=NO)

        self.tree.heading("#3", text="CRIME")
        self.tree.column("#3", minwidth=0, width=150, stretch=NO)

        self.tree.heading("#4", text="Nationality")
        self.tree.column("#4", minwidth=0, width=100, stretch=NO)

        self.tree.heading("#5", text="MATCHING %")
        self.tree.column("#5", minwidth=0, width=120, stretch=NO)

        ttk.Style().configure("Treeview.Heading", font=('Calibri', 13, 'bold'), foreground="red", relief="flat")
        self.tree.place(x=710, y=50)
        self.tree.bind("<Double-1>", self.doubleclick)

    def doubleclick(self, event):
        item = self.tree.selection()
        if item:
            item_id = self.tree.item(item, "values")[0]
            self.view_details(int(item_id))

    def view_details(self, cr_id):
        """Display details of the selected individual."""
        query = "SELECT * FROM people WHERE Id=?"
        self.cursor.execute(query, (cr_id,))
        row = self.cursor.fetchone()

        if row:
            details = [
                ("Name", row[1]), ("FatherName", row[3]), ("MotherName", row[4]),
                ("Gender", row[2]), ("Religion", row[5]), ("Blood Group", row[6]),
                ("Body Mark", row[7]), ("Nationality", row[8]), ("Crime", row[9])
            ]

            for idx, (label_text, value) in enumerate(details):
                Label(self.window, text=label_text, bg="#382273", fg='yellow', width=20, font=("bold", 12)).place(x=930, y=400 + idx * 30)
                Label(self.window, text=value, bg="#382273", fg='white', width=20, font=("bold", 12)).place(x=1130, y=400 + idx * 30)

            # Display image
            image_path = f'images/user.{cr_id}.png'
            if os.path.exists(image_path):
                image = Image.open(image_path).resize((180, 180), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(image)
                Label(self.window, image=photo, width=180, height=180).place(x=750, y=450)
                self.window.image = photo  # Keep a reference

    def get_profile(self, id):
        """Fetch profile from the database."""
        query = "SELECT ID, name, crime, nationality FROM people WHERE ID=?"
        self.cursor.execute(query, (id,))
        return self.cursor.fetchone()

    def show_percentage_match(self, face_distance, face_match_threshold=0.6):
        """Calculate percentage match for the face."""
        if face_distance > face_match_threshold:
            range = (1.0 - face_match_threshold)
            linear_val = (1.0 - face_distance) / (range * 2.0)
            return linear_val
        else:
            range = face_match_threshold
            linear_val = 1.0 - (face_distance / (range * 2.0))
            return linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))

    def update(self):
        is_true, frame = self.vid.get_frame()
        if is_true:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            if self.process_this_frame:
                self.face_locations = fr.face_locations(rgb_small_frame)
                self.face_encodings = fr.face_encodings(rgb_small_frame, self.face_locations)
                self.face_names = []

                for face_encoding in self.face_encodings:
                    matches = fr.compare_faces(self.encodings, face_encoding)
                    face_distances = fr.face_distance(self.encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    confidence = str(round(self.show_percentage_match(face_distances[best_match_index]) * 100, 2)) + "%"

                    if matches[best_match_index]:
                        id = self.known_face_names[best_match_index]
                        profile = self.get_profile(id)

                        if profile and profile not in self.detected_people:
                            self.detected_people.append(profile)
                            self.tree.insert("", 'end', values=(*profile, confidence))
                            winsound.PlaySound("SystemExit", winsound.SND_ALIAS)

            self.process_this_frame = not self.process_this_frame

        self.window.after(15, self.update)

class VideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                frame = imutils.resize(frame, height=700)
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return False, None

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == "__main__":
    App()
