# Generated by Django 4.2.3 on 2023-07-16 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0005_remove_plantimage_camera_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='plantimage',
            name='camera_source',
            field=models.CharField(default='esp32cam', max_length=20),
        ),
    ]
