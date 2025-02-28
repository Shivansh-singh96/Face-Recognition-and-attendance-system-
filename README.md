Face Recognition & Attendance System
This project is a Python-based application that uses face recognition technology to identify students and mark their attendance automatically. It leverages the face_recognition library alongside OpenCV for image processing and Tkinter for the graphical user interface (GUI). The system can register new students, mark attendance via webcam or uploaded images, and maintain an attendance log.

Features
Student Registration: Capture and encode a student's face using a webcam.
Attendance Marking: Recognize faces from uploaded images or webcam feeds and log attendance in a CSV file.
Attendance Viewing: Display attendance records in a GUI window.
Logging: Errors and events are logged into a face_recognition.log file for debugging.
Cooldown Period: Prevents duplicate attendance entries within 45 minutes for the same student.


Prerequisites
Before running the project, ensure you have the following installed:
Python 3.7+
Libraries:
opencv-python (cv2)
face_recognition
numpy
tkinter (usually comes with Python)
pillow (optional for image handling in Tkinter)
pickle (standard library, no separate installation needed)

Hardware Requirements
A webcam (for real-time recognition and student registration).
Storage space for student images and attendance logs.


