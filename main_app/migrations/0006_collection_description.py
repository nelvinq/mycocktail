# Generated by Django 5.1.7 on 2025-03-28 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_alter_cocktail_shared'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
