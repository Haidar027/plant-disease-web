import os
import uuid
from django.conf import settings

def save_uploaded_image(image):
    # Generate a unique filename for the image
    filename = f'image_{uuid.uuid4().hex}.jpg'
    # Build the file path where the image will be saved
    save_path = os.path.join(settings.MEDIA_ROOT, filename)
    
    # Open the file in write-binary mode and save the image
    with open(save_path, 'wb') as f:
        for chunk in image.chunks():
            f.write(chunk)
    
    # Return the relative path of the saved image (to be used in the template)
    return os.path.join(settings.MEDIA_URL, filename)
