# app/utils/constants.py

# API Details
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Supported Crops (Future Phase Reference)
CROP_CLASSES = [
    "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas",
    "mothbeans", "mungbean", "blackgram", "lentil", "pomegranate",
    "banana", "mango", "grapes", "watermelon", "muskmelon", "apple",
    "orange", "papaya", "coconut", "cotton", "jute", "coffee"
]

# Error Messages
MSG_INTERNAL_SERVER_ERROR = "An unexpected error occurred on the server."
MSG_VALIDATION_ERROR = "One or more validation checks failed."
MSG_RESOURCE_NOT_FOUND = "The requested resource could not be found."
MSG_UNAUTHORIZED = "Authentication credentials are missing or invalid."
MSG_FORBIDDEN = "You do not have permission to perform this action."
