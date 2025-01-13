from text_extraction import *
from preprocessing import process_image


MEDICINE_DATASET_PATH = r"resource\medicine_names.csv"

def processAndExtract(image_path):

   
    """Process the selected image and extract text"""
    
    #step1: Process the image
    processed_image_path=process_image(image_path)
    if not process_image:
        print("Image processing failed")
        return None

    #step2: Extract Text from the preprocessed image
    extracted_text = extract_text_from_image(processed_image_path,MEDICINE_DATASET_PATH)
    print(extracted_text)
    return extracted_text

# image_path=r"C:\Users\aujal\OneDrive\Desktop\Testing Images\image (23).jpg"
# processAndExtract(image_path)