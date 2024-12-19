from text_extraction import extract_text_from_image
from text_extraction import extract_text_from_image
from preprocessing import process_image

def processAndExtract(image_path):

    # excel_file_path=r"C:\Users\aujal\OneDrive\Desktop\ocr prescription reader\OCR-Prescription-Reader\gui\resource\medicine_names.csv"
    # known_medicine= load_medicine_names(excel_file_path)
    
    """Process the selected image and extract text"""
    
    #step1: Process the image
    process_image(image_path)

    #step2: Extract Text from the preprocessed image
    extracted_text = extract_text_from_image(image_path)

    return extracted_text