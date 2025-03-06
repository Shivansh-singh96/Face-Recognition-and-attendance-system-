import cv2
import face_recognition
import pickle
import numpy as np
import csv
from datetime import datetime, timedelta
import os
import logging
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog  

# Setup logging
logging.basicConfig(filename='face_recognition.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load data without encryption
try:
    with open('Encodefile.p', 'rb') as file:
        EncodeListKnown, StudentName = pickle.load(file)
except (FileNotFoundError, pickle.UnpicklingError) as e:
    logging.error(f"Error loading file 'Encodefile.p': {e}")
    messagebox.showerror("Error", "Failed to load the data file. Ensure 'Encodefile.p' exists.")
    exit()

def mark_attendance(name):
    current_time = datetime.now()
    current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
    
    if not os.path.exists('Attendance.csv'):
        with open('Attendance.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Time'])

    try:
        with open('Attendance.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2 and row[0] == name:
                    try:
                        last_entry = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                        if current_time - last_entry < timedelta(minutes=45):
                            messagebox.showwarning("Warning", f"Attendance for '{name}' already marked.")
                            return
                    except ValueError:
                        logging.warning(f"Invalid timestamp in CSV for {name}: {row[1]}")
    except IOError as e:
        logging.error(f"Error reading attendance file: {e}")
    
    try:
        with open('Attendance.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, current_time_str])
        messagebox.showinfo("Attendance", f"Attendance marked for '{name}'")
    except IOError as e:
        logging.error(f"Error writing to attendance file: {e}")
        messagebox.showerror("Error", "Failed to save attendance.")

def check_match(image):
    encodes = face_recognition.face_encodings(image)
    if not encodes:
        messagebox.showwarning("Warning", "No faces detected in the image.")
        return

    matches = []
    for e in encodes:
        if True in face_recognition.compare_faces(EncodeListKnown, e):
            match = StudentName[np.argmin(face_recognition.face_distance(EncodeListKnown, e))]
            matches.append(match)
            mark_attendance(match)
        else:
            matches.append("Unknown")

    if matches:
        messagebox.showinfo("Results", f"Matches: {', '.join(matches)}")
    else:
        messagebox.showinfo("Results", "No matches found.")

def capture_student_image():
    name = simpledialog.askstring("Input", "Enter Student ID:")
    if not name or name in StudentName:
        messagebox.showwarning("Warning", f"'{name}' already exists!" if name in StudentName else "No name entered!")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Failed to open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture frame.")
            break
        cv2.imshow("Capture Mode", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            save_path = os.path.join('D:/Project New/Students', f"{name}.jpg")
            cv2.imwrite(save_path, frame)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(frame_rgb)
            if encodings:
                EncodeListKnown.append(encodings[0])
                StudentName.append(name)
                with open('Encodefile.p', 'wb') as file:
                    pickle.dump((EncodeListKnown, StudentName), file)
                messagebox.showinfo("Success", f"Registered and encoded {name}!")
            else:
                messagebox.showwarning("Warning", "No face detected in captured image!")
            break
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def upload_group_image():
    file_path = filedialog.askopenfilename()  # Changed from tk.simpledialog to filedialog
    if file_path:
        image = cv2.imread(file_path)
        if image is None:
            messagebox.showerror("Error", "Failed to load image.")
        else:
            check_match(image)

def webcam_match():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Failed to open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture frame.")
            break
        cv2.imshow("Matching...", frame)
        encodings = face_recognition.face_encodings(frame)
        if encodings:  # Face detected, process it
            check_match(frame)
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def view_attendance():
    try:
        with open('Attendance.csv', 'r') as file:
            reader = csv.reader(file)
            attendance = list(reader)
        if len(attendance) <= 1:  # Only header or empty
            messagebox.showinfo("Attendance", "No attendance records yet.")
            return
        
        win = tb.Window(themename="lumen")
        win.title("Attendance Records")
        win.geometry("400x300")
        
        text = tk.Text(win, height=15, width=50)
        text.pack(pady=10)
        for row in attendance[1:]:  # Skip header
            text.insert(tk.END, f"{row[0]} - {row[1]}\n")
        text.config(state='disabled')
    except FileNotFoundError:
        messagebox.showinfo("Attendance", "No attendance file found.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load attendance: {e}")

# GUI Setup with ttkbootstrap
root = tb.Window(themename="lumen")
root.title("Face Recognition & Attendance System")
root.geometry("500x500")
root.resizable(False, False)

# Title Label (Centered)
title_label = tb.Label(root, text="Face Recognition & Attendance", font=("Arial", 16, "bold"), bootstyle="primary")
title_label.place(relx=0.5, y=25, anchor="center")

# Buttons
buttons = [
    ("Register New Student", capture_student_image, "success"),
    ("Upload Image", upload_group_image, "warning"),
    ("Mark Attendance", webcam_match, "info"),
    ("View Attendance", view_attendance, "secondary"),  # Added View Attendance button
    ("Exit", root.quit, "danger"),
]

y_position = 80
for text, command, style in buttons:
    tb.Button(root, text=text, command=command, bootstyle=f"{style}-outline", width=40, padding=10).place(x=80, y=y_position)
    y_position += 60

# Load and Place Logo in Bottom-Left
def place_logo():
    try:
        logo = Image.open("D:/Project New/logo/logo.png")  # Replace with your logo image path
        logo = logo.resize((120, 100), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(logo)
        
        logo_label = tk.Label(root, image=logo_img, bg="white")
        logo_label.image = logo_img  # Keep reference to avoid garbage collection
        logo_label.place(x=10, y=root.winfo_height() - 90)  # Bottom-left position
    except Exception as e:
        print(f"Logo not found or error occurred: {e}. Skipping...")

# Ensure logo is placed correctly after window loads
root.after(100, place_logo)

# Start the GUI event loop
root.mainloop()