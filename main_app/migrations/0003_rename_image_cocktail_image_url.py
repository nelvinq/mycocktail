# Generated by Django 5.1.7 on 2025-03-25 08:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_alter_cocktail_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cocktail',
            old_name='image',
            new_name='image_url',
        ),
    ]
