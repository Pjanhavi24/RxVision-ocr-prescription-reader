import pytesseract
from PIL import Image
from preprocessing import process_image
import pandas as pd
from google.cloud import vision
from rapidfuzz import fuzz, process

#initialize the Google vision api client using the json key
client= vision.ImageAnnotatorClient.from_service_account_json(r"resource\client_secret_code.json")
medicine_dataset=r"resource/medicine_names.csv"

# Load the medicine dataset
def load_medicine_dataset(medicine_dataset):
    """Load medicine names from the dataset."""
    df = pd.read_csv(medicine_dataset)
    return [name.lower().strip() for name in df['name'].tolist()]

GENERIC_WORDS = ["tablet", "syrup","suspension", "capsule", "ointment", "mg", "ml", "cream", "Injection","","10", "20", "5", "60", "100"]

def is_valid_medicine_name(text):
    for word in GENERIC_WORDS:
        if word in text.split():
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
    return sum(confidences)/len(confidences) if confidences else 0

# Generate n-grams from a text
# def generate_ngrams(text, n=3):
#     """Generate n-grams from a given text."""
#     return [text[i:i + n] for i in range(len(text) - n + 1)]

# def match_chunk(chunk, query, threshold=70):
#         results = []
#         for name in chunk:
#             score = fuzz.partial_ratio(query, name)
#             if score >= threshold:
#                 results.append(name)
#         return results

# Match extracted text against medicine
def match_medicine(extracted_text, medicine_names, threshold=68):
    """Match extracted text with the medicine dataset."""
    results = []
    for text in extracted_text.split("\n"):
        text = normalize_text(text.strip())
        normalized_dataset = [normalize_text(name) for name in medicine_names]  # Normalize dataset
        match= process.extractOne(text,normalized_dataset,scorer=fuzz.token_sort_ratio)
        if match and match[1]>=threshold:
            
            results.append(match[0])
    return results

def extract_text_from_image(image_path,medicine_dataset,confidence_threshold=70):
    """Extract only medicine names from the image."""
    # Load the medicine dataset
    medicine_names = load_medicine_dataset(medicine_dataset)

    """Extract text from a preprocessed image using Tesseract and Google Vision."""
    # Load the preprocessed image using Pillow
    preprocessed_image = Image.open(image_path)

    # Custom Tesseract configurations for better results
    custom_config = r'--oem 3 --psm 6'  # Use best OCR engine mode and automatic page segmentation

    # Step 1: Try the Tesseract OCR first with custom configuration
    extracted_text = pytesseract.image_to_string(preprocessed_image, lang='eng', config=custom_config)

    # Get Tesseract confidence score
    confidence = get_tesseract_confidence(preprocessed_image)

    # Step 2: If confidence is low, switch to Google Vision API
    if confidence < confidence_threshold:
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()

            # Prepare the image for Google Vision API
            image = vision.Image(content=content)
            # Add language hints to improve OCR accuracy
            image_context = vision.ImageContext(language_hints=['en'])
            # Call the document text detection API with language hints
            response = client.document_text_detection(image=image, image_context=image_context)

            # Handle any API errors
            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")
            
            # Extract text from the Google Vision API response
            extracted_text = response.full_text_annotation.text
            # print("Raw ocr text: ",extracted_text)
        
        except Exception as e:
            print(f"Error during vision api processing:{e}")
            return ""
        
    # Step 3: Match extracted text with medicine dataset
    results = match_medicine(extracted_text, medicine_names)
    return results


# Kept for standalone testing
# if __name__ == "__main__":
#      # Paths to files
#     image_path = r"C:\Users\aujal\OneDrive\Desktop\Testing Images\image (23).jpg"
#     dataset_path = r"resource\medicine_names.csv"
#     # Extract medicine names
#     extracted_text = extract_text_from_image(image_path,medicine_dataset)
    
#     # Display the extracted medicine names
#     print("Extracted Medicine Names:\n",extracted_text)
