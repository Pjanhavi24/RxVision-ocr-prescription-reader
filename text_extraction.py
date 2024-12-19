`# extract_text.py
import pytesseract
from PIL import Image
from preprocessing import process_image
# from crop import confirm_crop
from google.cloud import vision

#initialize the Google vision api client using the json key
client= vision.ImageAnnotatorClient.from_service_account_json(r"resource\client_secret_code.json")

#get the confidence score from tesseract to decide whether to use vision api or tesserect ocr
def get_tesseract_confidence(image):
    """Get confidence score for Tesseract OCR"""
    # Use pytesseract to confidencesget detailed information
    data= pytesseract.image_to_data(image, output_type= pytesseract.Output.DICT)

    #Get the confidence score, (removing -1 which means to detection)
    = [int(conf) for conf in data['conf'] if conf != '-1']

    #return average confidence score
    return sum(confidences)/len(confidences) if confidences else 0


def extract_text_from_image(image_path, confidence_threshold=60):
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

    return extracted_text





#Kept for standalone testing

# if __name__ == "__main__":
#     # Input the path of the preprocessed image
#     print("Enter the path of the preprocessed image for text extraction:")
#     preprocessed_image_path = input()

#     # Extract text from the image
#     text = extract_text_from_image(preprocessed_image_path)
    
#     # Output the extracted text
#     print("Extracted Text:\n", text)`