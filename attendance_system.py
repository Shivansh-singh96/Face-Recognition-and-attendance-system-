import cv2
import face_recognition
import pickle
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import csv
import time
from datetime import datetime, timedelta
import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox

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
    name = simpledialog.askstring("Input", "Enter Student Name:")
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
            # Compute and save encoding
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
    file_path = filedialog.askopenfilename()
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
        
        win = tk.Toplevel(root)
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

# GUI setup
root = tk.Tk()
root.title("Face Recognition & Attendance System")
root.geometry("600x700")
root.configure(bg="#2C3E50")

# Style configuration
style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", font=("Arial", 12, "bold"), padding=10)
style.map("TButton", background=[("active", "#3498DB"), ("!active", "#2980B9")],
          foreground=[("active", "white"), ("!active", "white")])

# Main frame
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(expand=True)

# Animated Title (Fade-in effect)
title_label = ttk.Label(main_frame, text="Face Recognition System", 
                        font=("Arial", 20, "bold"), foreground="#ECF0F1")
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
title_label.configure(anchor="center")

def fade_in_title(step=0):
    if step <= 10:
        alpha = step / 10
        title_label.configure(foreground=f"#ECF0F1{int(alpha * 255):02x}")
        root.after(100, fade_in_title, step + 1)

# Status label with pulse effect
status_var = tk.StringVar(value="Ready")
status_label = ttk.Label(main_frame, textvariable=status_var, foreground="#BDC3C7", font=("Arial", 10))
status_label.grid(row=1, column=0, columnspan=2, pady=10)
status_label.pulse = False

def pulse_status():
    if status_label.pulse:
        current_color = status_label.cget("foreground")
        new_color = "#ECF0F1" if current_color == "#BDC3C7" else "#BDC3C7"
        status_label.configure(foreground=new_color)
        root.after(500, pulse_status)

# Button slide-in animation (using row instead of pady)
def slide_in_button(button, target_row, step=0):
    if step == 0:
        button.current_row = 0  # Start at row 0 (top of frame)
        button.grid(row=button.current_row, column=0, columnspan=2, sticky="ew", pady=10)
    steps = 20
    if step < steps:
        new_row = button.current_row + (target_row - button.current_row) * 0.2  # Easing
        button.current_row = int(new_row + 0.5)  # Round to nearest int
        button.grid(row=button.current_row, column=0, columnspan=2, sticky="ew", pady=10)
        root.after(50, slide_in_button, button, target_row, step + 1)
    elif step == steps:
        button.grid(row=target_row, column=0, columnspan=2, sticky="ew", pady=10)

# Button functions with animations
def update_status(text, pulse=False):
    status_var.set(text)
    status_label.pulse = pulse
    if pulse:
        pulse_status()
    else:
        status_label.configure(foreground="#BDC3C7")
        status_label.pulse = False

def capture_student_image_wrapper():
    update_status("Capturing student image...", True)
    capture_student_image()
    update_status("Ready")

def upload_group_image_wrapper():
    update_status("Processing uploaded image...", True)
    upload_group_image()
    update_status("Ready")

def webcam_match_wrapper():
    update_status("Scanning webcam...", True)
    webcam_match()
    update_status("Ready")

def view_attendance_wrapper():
    update_status("Loading attendance records...", True)
    view_attendance()
    update_status("Ready")

# Buttons with animation setup
btn_register = ttk.Button(main_frame, text="Register New Student", command=capture_student_image_wrapper)
slide_in_button(btn_register, 2)

btn_upload = ttk.Button(main_frame, text="Upload Group Image", command=upload_group_image_wrapper)
slide_in_button(btn_upload, 3)

btn_mark = ttk.Button(main_frame, text="Mark Attendance (Webcam)", command=webcam_match_wrapper)
slide_in_button(btn_mark, 4)

btn_view = ttk.Button(main_frame, text="View Attendance", command=view_attendance_wrapper)
slide_in_button(btn_view, 5)

btn_exit = ttk.Button(main_frame, text="Exit", command=root.quit, style="Exit.TButton")
style.configure("Exit.TButton", background="#E74C3C")
slide_in_button(btn_exit, 6)

# Hover effect for buttons
def on_enter(event):
    event.widget.configure(style="Hover.TButton")
style.configure("Hover.TButton", background="#3498DB")

def on_leave(event):
    event.widget.configure(style="TButton")

for btn in [btn_register, btn_upload, btn_mark, btn_view]:
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

# Start animations
root.after(100, fade_in_title)
main_frame.columnconfigure(0, weight=1)

# Start the GUI event loop
root.mainloop()