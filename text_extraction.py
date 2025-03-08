import re
import pytesseract
from PIL import Image
from preprocessing import process_image
import pandas as pd
from google.cloud import vision
import boto3
from rapidfuzz import fuzz, process

#initialize the aws textract client
textract_client= boto3.client("textract", region_name= "ap-south-1")

medicine_dataset=r"resource/medicine_names.csv"

# Load the medicine dataset
def load_medicine_dataset(medicine_dataset):
    """Load medicine names from the dataset."""
    df = pd.read_csv(medicine_dataset)
    return [name.lower().strip() for name in df['name'].tolist()]

GENERIC_WORDS = [""]

def is_valid_medicine_name(text):
    """Check if extracted text looks like a valid medicine name."""
    if len(text) < 3:  # Ignore very short words like 'I', 'O', 'X'
        return False
    if re.search(r'\d', text) and len(text) < 5:  # Ignore isolated numbers like '2', '107'
        return False
    if text.lower() in ["age", "sex", "date", "information", "adh", "o"]:  # Ignore unwanted words
        return False
    return True

def normalize_text(text):
    return text.lower().replace("mg", "").strip()


#get the confidence score from tesseract to decide whether to use vision api or tesserect ocr
def get_tesseract_confidence(image):

    """Get confidence score for Tesseract OCR"""
    # Use pytesseract to confidences get detailed information
    data= pytesseract.image_to_data(image, output_type= pytesseract.Output.DICT)

    #Get the confidence score, (removing -1 which means to detection)
    confidences = [int(conf) for conf in data['conf'] if conf != '-1']

    #return average confidence score
    return sum(confidences)/len(confidences) if len(confidences) >0 else 0

# Match extracted text against medicine
def match_medicine(extracted_text, medicine_names, threshold=55): #default threshold = 55
    """Match extracted text with the medicine dataset."""
    results = []
    normalized_dataset = [normalize_text(name) for name in medicine_names] 
    for text in extracted_text.split("\n"):
        text = normalize_text(text.strip())

        if not text or not is_valid_medicine_name(text):
            continue

        if text in normalized_dataset:
            results.append(text)
            continue
        match= process.extractOne(text,normalized_dataset,scorer=fuzz.partial_token_sort_ratio)
        if match and match[1]>=threshold:
            
            results.append(match[0])
    return results if results else None

def extract_text_with_textract(image_path):
    """Extract text from an image using AWS Textract."""
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    response = textract_client.detect_document_text(Document={"Bytes": image_bytes})

    extracted_text = ""
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":  # Extract line-level text
            extracted_text += item["Text"] + "\n"

    return extracted_text



def extract_text_from_image(image_path,medicine_dataset,confidence_threshold=70): #default threshold = 70
    """Extract only medicine names from the image."""
    # Load the medicine dataset
    medicine_names = load_medicine_dataset(medicine_dataset)

    """Extract text from a preprocessed image using Tesseract and Amazon Textract."""
    # Load the preprocessed image using Pillow
    preprocessed_image = Image.open(image_path)

    # Get Tesseract confidence score
    confidence = get_tesseract_confidence(preprocessed_image)

    # Step 2: If confidence is low, switch to AWS Textract API
    if confidence > confidence_threshold:
        # Custom Tesseract configurations for better results
        custom_config = r'--oem 3 --psm 6'  # Use best OCR engine mode and automatic page segmentation
        # Step 1: Try the Tesseract OCR first with custom configuration
        extracted_text = pytesseract.image_to_string(preprocessed_image, lang='eng', config=custom_config)
        print(f"Using Tesseract (confidence: {confidence:.2f})")

    else:
        try:
            extracted_text = extract_text_with_textract(image_path)
            print(f"Extracted using textract: {extracted_text}")
        except Exception as e:
            print(f"Textract failed: {e}. Falling back to Tesseract.")
            custom_config = r'--oem 3 --psm 6'
            extracted_text = pytesseract.image_to_string(preprocessed_image, lang='eng', config=custom_config)

    # Check if text is empty before proceeding
    if not extracted_text or not extracted_text.strip():
        print("No text detected in image")
        return None  # Return None instead of an empty string
    
    # Step 3: Match extracted text with medicine dataset
    results = match_medicine(extracted_text, medicine_names)
    return results


# Kept for standalone testing
# if __name__ == "__main__":
#      # Paths to files
#     image_path = r"C:\Users\aujal\OneDrive\Desktop\Testing Images\image image (23).jpg"
#     dataset_path = r"resource\medicine_names.csv"
#     # Extract medicine names
#     extracted_text = extract_text_from_image(image_path,medicine_dataset)
    
#     # Display the extracted medicine names
#     print("Extracted Medicine Names:\n",extracted_text)
