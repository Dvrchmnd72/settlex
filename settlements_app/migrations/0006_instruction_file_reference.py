# Generated by Django 4.0.6 on 2025-02-05 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settlements_app', '0005_remove_instruction_client_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='instruction',
            name='file_reference',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
