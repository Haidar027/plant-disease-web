from django.db import models
import os

# Create your models here.
def increment_image_name(instance, filename):
    base_name, extension = os.path.splitext(filename)
    counter = PlantImage.objects.count() + 1
    return f'image{counter}{extension}'

class PlantImage(models.Model):
    image = models.ImageField(upload_to=increment_image_name)
    camera_source = models.CharField(max_length=20, default='esp32cam')  # Adjust the max_length as needed

    def __str__(self):
        return self.image.name
