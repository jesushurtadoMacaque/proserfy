import os

# Directory for images of services
UPLOAD_DIRECTORY = "uploaded_images/services"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
