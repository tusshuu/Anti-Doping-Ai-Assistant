import easyocr
import cv2
import os

reader = easyocr.Reader(['en'])

def preprocess_image(image_path: str):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    cv2.imwrite(image_path, gray)

def extract_text_from_image(image_path: str):
    preprocess_image(image_path)
    results = reader.readtext(image_path)
    extracted_text = " ".join([res[1] for res in results])
    return extracted_text