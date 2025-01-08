import cv2
import numpy as np
import os


def create_temp_directory():
    """Create a temporary directory to store processed images."""
    if not os.path.exists("temp"):
        os.makedirs("temp")

def load_image(image_path):
    """Load the image from the specified path."""
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to load image at {image_path}")
    return img

def invert_image(img):
    """Invert the colors of the image."""
    return cv2.bitwise_not(img)

def grayscale(image):
    """Convert the image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def binarize(image):
    """Convert the grayscale image to binary."""
    adaptive_thresh_image = cv2.adaptiveThreshold(
        image, 255,                          
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,      
        cv2.THRESH_BINARY,                  
        11,                                  
        2                                  
    )
    
    return adaptive_thresh_image

def noise_removal(image):
    """Remove noise from the image."""
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
    return image

def apply_dynamic_erosion(image):
    """Dynamically apply erosion based on the number of connected components."""
    # Find connected components in the binary image
    num_labels, labels = cv2.connectedComponents(image)
    
    # Threshold to decide whether to apply erosion or not
    erosion_applied = False
    if num_labels < 30:  # This threshold can be adjusted based on your data
        print("Applying erosion since connected components are too few.")
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
        erosion_applied = True
    else:
        print("Skipping erosion, the image seems fine.")
    
    return image, erosion_applied

def apply_dynamic_dilation(image):
    """Dynamically apply dilation based on the number of connected components."""
    # Find connected components in the binary image
    num_labels, labels = cv2.connectedComponents(image)
    
    # Boolean flag to track whether dilation was applied
    dilation_applied = False
    
    # Threshold to decide whether to apply dilation or not
    if num_labels > 100:  # This threshold can be adjusted based on your data
        print("Applying dilation since connected components are too many.")
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        dilation_applied = True
    else:
        print("Skipping dilation, the image seems fine.")
    
    return image, dilation_applied


def get_skew_angle(cvImage) -> float:
    """Calculate the skew angle of the image."""
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=2)

    contours, _ = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    largestContour = contours[0]

    minAreaRect = cv2.minAreaRect(largestContour)
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle

def rotate_image(cvImage, angle: float):
    (h,w)= cvImage.shape[:2]

    # Check if the image is in portrait mode (height > width)
    if h>w:
        print("Image is in portrait mode (height>width)")
        #Rotate image by 90 degree , rotating landscape mode
        rotate_image= cv2.rotate(cvImage, cv2.ROTATE_90_CLOCKWISE)
        return rotate_image
    else:
        print("Image is in landscape mode (width>height) No rotation needed.")
        return cvImage


def deskew(cvImage):
    """Deskew the image based on its skew angle."""
    angle = get_skew_angle(cvImage)
    return rotate_image(cvImage, -1.0 * angle)

def add_borders(image, border_size=150):
    """Add white borders around the image."""
    color = [255, 255, 255]
    return cv2.copyMakeBorder(image, border_size, border_size, border_size, border_size,
                               cv2.BORDER_CONSTANT, value=color)

def detect_edges(image):
    
    # Apply GaussianBlur to smooth the image before edge detection
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Adaptive thresholding to handle shadows and lighting variation
    adaptive_thresh = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY_INV, 11, 2)
    
    # Edge detection with Canny, focusing on prominent edges
    edges = cv2.Canny(adaptive_thresh, 50, 150)
    
    return edges

def overlay_edges_on_original(original_image, edges):
    """
    Overlay the detected edges on the original image to preserve important information.
    """
    # Convert edges to 3-channel image (so it can be merged with original)
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # Overlay the edges onto the original image by adding them together
    overlay = cv2.addWeighted(original_image, 0.8, edges_colored, 0.5, 0)
    
    return overlay



def process_image(image_path):
    final_image_path=image_path

    """Process the image by applying all functions."""
    create_temp_directory()
    img = load_image(image_path)
    if img is None:
        return

    # Step 1: Invert Image
    inverted_image = invert_image(img)
    cv2.imwrite("temp/inverted.jpg", inverted_image)
    print("Inverted image saved as: temp/inverted.jpg\n")
    inverted_image_path="temp/inverted.jpg"
    final_image_path=inverted_image_path

    # Step 2: Grayscale
    gray_image = grayscale(img)
    cv2.imwrite("temp/gray.jpg", gray_image)
    print("Grayscale image saved as: temp/gray.jpg\n")
    grayscale_image_path= "temp/gray.jpg"
    final_image_path=grayscale_image_path


    # Step 3: Binarization
    binary_image = binarize(gray_image)
    cv2.imwrite("temp/bw_image.jpg", binary_image)
    print("Binary image saved as: temp/bw_image.jpg\n")
    binary_image_path= "temp/bw_image.jpg"
    final_image_path=binary_image_path

    # Step 4: Edge Detection
    edge_detected_image = detect_edges(gray_image)  # Edge detection on the grayscale image
    cv2.imwrite("temp/edge_detected_image.jpg", edge_detected_image)
    print("Edge detected image saved as: temp/edge_detected_image.jpg\n")
    edge_detectedImage_path= "temp/edge_detected_image.jpg"
    final_image_path=edge_detectedImage_path

    # Step 5: Overlay
    overlaid_image = overlay_edges_on_original(img, edge_detected_image)
    cv2.imwrite("temp/edge_overlay_image.jpg", overlaid_image)
    print("Image with edge overlay saved as: temp/edge_overlay_image.jpg\n")
    overlaid_image_path= "temp/edge_overlay_image.jpg"
    final_image_path=overlaid_image_path

    # Step 6: Noise Removal
    no_noise = noise_removal(binary_image)
    cv2.imwrite("temp/no_noise.jpg", no_noise)
    print("Noise removed image saved as: temp/no_noise.jpg\n")
    noiseremoved_path= "temp/no_noise.jpg"
    final_image_path=noiseremoved_path

    # Step 7: Erode Image
    erosion_needed = np.mean(no_noise) < 120  
    if erosion_needed:
        eroded_image_path = "temp/eroded_image.jpg"
        # Logic for erosion here
        print(f"Eroded image saved as: {eroded_image_path}")
        final_image_path = eroded_image_path  # Update final path
    else:
        print("Skipping erosion, the image seems fine.")

    # Step 8: Dilate Image
    dilation_needed=np.mean(no_noise)>150
    dilated_image, dilation_applied = apply_dynamic_dilation(no_noise)
    if dilation_applied:  # Save only if dilation was applied
        cv2.imwrite("temp/dilated_image.jpg", dilated_image)
        print("Dilated image saved as: temp/dilated_image.jpg\n")
        dilated_image_path= "temp/dilated_image.jpg"
        final_image_path=dilated_image_path
    else:
        print("Dilation not needed, skipping saving dilated image.\n")

    # Step 9: Rotate image
    rotated_image = rotate_image(img, angle=90)
    if rotated_image is not img:  # Save only if rotation was applied
        cv2.imwrite("temp/rotated_image.jpg", rotated_image)
        print("Image rotated and saved as: temp/rotated_image.jpg\n")
        rotated_image_path="temp/rotated_image.jpg"
        final_image_path= rotated_image_path
    else:
        print("Rotation not needed, image remains unchanged.\n")
        final_image_path=dilated_image_path
    
    # Print the final image path before returning
    print("Final image path after preprocessing:", final_image_path)

    return final_image_path
        

    

    # # Step 9: Deskewing
    # fixed = deskew(img)
    # cv2.imwrite("temp/rotated_fixed.jpg", fixed)
    # print("Deskewed image saved as: temp/rotated_fixed.jpg\n")

    # Step 10: Adding Borders
    # bordered_image = add_borders(fixed)
    # cv2.imwrite("temp/image_with_border.jpg", bordered_image)
    # print("Image with borders saved as: temp/image_with_border.jpg\n")
    
    #Kept this for standalone testing

# if __name__ == "__main__":
#     # Prompt the user for the image path
#     print("enter the path :")
#     user_image_path = input()
#     process_image(user_image_path)