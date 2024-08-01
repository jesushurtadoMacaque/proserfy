import os

# Directory for images of services
UPLOAD_DIRECTORY_SERVICES = "uploaded_images/services"
UPLOAD_DIRECTORY_PROFILES = "uploaded_images/profiles"

if not os.path.exists(UPLOAD_DIRECTORY_SERVICES):
    os.makedirs(UPLOAD_DIRECTORY_SERVICES)


if not os.path.exists(UPLOAD_DIRECTORY_PROFILES):
    os.makedirs(UPLOAD_DIRECTORY_PROFILES)