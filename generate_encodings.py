import cv2
import face_recognition
import pickle
import os

# Folder containing student images
folderPath = 'D:/Project New/Students'
PathList = os.listdir(folderPath)
print("Images found:", PathList)

imgList = []
StudentName = []
skipped_files = []

for path in PathList:
    img = cv2.imread(os.path.join(folderPath, path))
    if img is None:
        print(f"Failed to load image: {path}")
        skipped_files.append(path)
        continue
    imgList.append(img)
    StudentName.append(os.path.splitext(path)[0])

# Function to encode all images
def findEncodings(imagesList, names):
    encodeList = []
    for img, name in zip(imagesList, names):
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        except IndexError:
            print(f"Face not detected in image: {name}")
            skipped_files.append(f"{name}.jpg")
    return encodeList

# Encode images and save to file
print("Encoding Started...")
EncodeListKnown = findEncodings(imgList, StudentName)
if skipped_files:
    print("Skipped files:", skipped_files)
EncodeListKnownWithIds = [EncodeListKnown, StudentName]
print(f"Encoding Completed: {len(EncodeListKnown)} faces encoded")

# Save encodings to pickle file
try:
    with open("Encodefile.p", 'wb') as file:
        pickle.dump(EncodeListKnownWithIds, file)
    print("File Saved")
except Exception as e:
    print(f"Failed to save file: {e}")