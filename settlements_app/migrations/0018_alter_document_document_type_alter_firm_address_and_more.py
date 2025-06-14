# Generated by Django 5.1.6 on 2025-02-20 01:44

import django.db.models.deletion
import settlements_app.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("settlements_app", "0017_chatmessage"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="document_type",
            field=models.CharField(
                choices=[
                    ("contract", "Contract"),
                    ("title_search", "Title Search"),
                    ("id_verification", "Verification of ID"),
                    ("form_qro_d2", "Form QRO D2"),
                    ("trust_document", "Trust Document"),
                    ("asic_extract", "ASIC Extract"),
                    ("gst_withholding", "GST Withholding"),
                ],
                default="contract",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="firm",
            name="address",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="firm",
            name="contact_number",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name="firm",
            name="postcode",
            field=models.CharField(blank=True, default="", max_length=10),
        ),
        migrations.AlterField(
            model_name="firm",
            name="state",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="instruction",
            name="file_reference",
            field=models.CharField(
                default=settlements_app.models.generate_file_reference,
                max_length=50,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="solicitor",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="solicitor",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
