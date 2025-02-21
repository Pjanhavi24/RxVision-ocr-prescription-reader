import requests
import re

EXCLUDED_TERMS= ["tablet", "syrup", "injection", "nasal spray", "cream", "ointment", "drop", "sachet"]

def preprocess_medicine_name(medicine_name):
    """
    Removes unwanted terms from the medicine name.

    Args:
        medicine_name (str): The raw medicine name.

    Returns:
        str: The cleaned medicine name.
    """

    if not isinstance(medicine_name, str):
        raise TypeError(f"Expected a string, but got {type(medicine_name)}: {medicine_name}")

    # Create a regex pattern to match the unwanted terms
    pattern = r"\b(" + "|".join(map(re.escape, EXCLUDED_TERMS)) + r")\b"

    # Remove unwanted terms and extra spaces
    cleaned_name = re.sub(pattern, "", medicine_name, flags=re.IGNORECASE).strip()

    return cleaned_name

def get_medicine_data(medicine_name):
     """
    Calls the API with the given medicine name and returns the response.

    Args:
        medicine_name (str): The name of the medicine to query.

    Returns:
        dict: A dictionary containing the API response or an error message.
    """
     
     try:
        cleaned_name=preprocess_medicine_name(medicine_name)
        url=f"https://vyt5wo7z44.execute-api.ap-south-1.amazonaws.com/default/api/v1/medicines?name={cleaned_name}"

        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors
        # Parse and return the JSON response
        return response.json()
     
     except requests.RequestException as e:
        print(f"Error calling the API: {e}")
        return {"error": "Failed to fetch data from the API. Please try again later."}