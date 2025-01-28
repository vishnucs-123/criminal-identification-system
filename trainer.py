import os
import cv2
import numpy as np
from PIL import Image

recognizer = cv2.face.LBPHFaceRecognizer_create()
path = r"Face-identificaton/dataSet"

# Check if path exists
if not os.path.exists(path):
    print(f"Error: The path {path} does not exist.")
    exit()

def getImgID(path):
    valid_extensions = ('.jpg', '.jpeg', '.png')
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(valid_extensions)]
    faces = []
    Ids = []
    for imagePath in imagePaths:
        try:
            filename = os.path.split(imagePath)[-1]
            parts = filename.split(".")
            if len(parts) < 3:
                print(f"Skipping invalid file format: {filename}")
                continue
            Id = int(parts[1])
            faceImage = Image.open(imagePath).convert('L')
            faceNp = np.array(faceImage, 'uint8')
            faces.append(faceNp)
            Ids.append(Id)
        except Exception as e:
            print(f"Error processing file {imagePath}: {e}")
    return Ids, faces

Ids, faces = getImgID(path)

print(f"Found {len(faces)} faces and {len(Ids)} IDs.")

if len(faces) == 0 or len(Ids) == 0:
    print("No training data found. Ensure the 'dataSet' directory contains valid images.")
    exit()

# Ensure the save directory exists
save_dir = r'recognizer'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

recognizer.train(faces, np.array(Ids))
recognizer.write(os.path.join(save_dir, 'training_data.yml'))
print(f"Training data saved to {os.path.join(save_dir, 'training_data.yml')}")

cv2.destroyAllWindows()
