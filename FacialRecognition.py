import face_recognition
import os
import cv2
import numpy as np

STUDENT_COUNT = 8
test = cv2.imread("Students/1.jpg", cv2.IMREAD_COLOR)  # Change the path accordingly


def get_faces(img):
    name = "Unknown"
    # Load known student images
    student_images = []
    student_encodings = []

    for i in range(1, STUDENT_COUNT + 1):  # Fix: Ensure all students are included
        image_path = os.path.join("Students", f"{i}.jpg")  # Fix: Correct file path
        if not os.path.exists(image_path):  # Ensure file exists
            print(f"Warning: {image_path} not found.")
            continue

        image = face_recognition.load_image_file(image_path)
        resized_image = cv2.resize(image, (800, 600), interpolation=cv2.INTER_AREA)
        encodings = face_recognition.face_encodings(resized_image)

        if encodings:  # Ensure at least one encoding is found
            student_images.append(image)
            student_encodings.append(encodings[0])  # Fix: Extract first encoding only
        else:
            print(f"Warning: No face found in {image_path}")

    student_names = [str(i) for i in range(1, STUDENT_COUNT + 1)][:len(student_encodings)]

    return start_face_recognition(img, student_encodings, student_names)


def start_face_recognition(img, encodings, names):
    if img is None:
        print("Error: Image is None.")
        return

    print(f"Shape: {img.shape} | Data Type: {img.dtype}")

    # Resize and convert for processing
    small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect face
    face_locations = face_recognition.face_locations(rgb_small_frame)
    print(f"Face Locations: {face_locations}")

    if not face_locations:
        print("No face found!")
        return

    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    if face_encodings:
        face_encoding = face_encodings[0]
        matches = face_recognition.compare_faces(encodings, face_encoding)
        name = "Unknown"

        # Find best match
        face_distances = face_recognition.face_distance(encodings, face_encoding)
        best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else -1

        if best_match_index != -1 and matches[best_match_index]:
            name = names[best_match_index]

        # Print detected person's name
        print(f"Detected: {name}")
        print("Uploading name...")

        return name
    return "Unknown"

img = cv2.resize(test, (800, 600), interpolation=cv2.INTER_AREA)
print(get_faces(img))