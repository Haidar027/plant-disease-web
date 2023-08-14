from django import forms
from .models import PlantImage

class PlantImageForm(forms.ModelForm):
    # camera_source = forms.ChoiceField(choices=(('esp32cam', 'ESP32-CAM'), ('laptop', 'Laptop Camera')))
    image = forms.ImageField()

    class Meta:
        model = PlantImage
        # fields = ['image', 'camera_source']
        fields = ['image']