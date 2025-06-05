import uuid
import logging
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import localtime
import pytz

# Set up logger
logger = logging.getLogger(__name__)

def generate_file_reference():
    """Generates a unique file reference using UUID."""
    return str(uuid.uuid4()).split('-')[0].upper()

# Firm Model
class Firm(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField()
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    acn = models.CharField(max_length=50, blank=True, null=True)  # Australian Company Number
    address = models.CharField(max_length=255, blank=True, default="")
    postcode = models.CharField(max_length=10, blank=True, default="")
    state = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return self.name

# Profession Choices
PROFESSION_CHOICES = [
    ('solicitor', 'Solicitor'),
    ('conveyancer', 'Conveyancer'),
    ('other', 'Other'),
]

# Solicitor Model
class Solicitor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="solicitor")
    instructing_solicitor = models.CharField(max_length=255)
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE, related_name="solicitors", null=True, blank=True)
    office_phone = models.CharField(max_length=20, blank=True, null=True)
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES, default='solicitor')
    law_society_number = models.CharField(max_length=50, blank=True, null=True)
    conveyancer_license = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.instructing_solicitor} ({self.firm.name if self.firm else 'No Firm'})"

# Instruction Model
class Instruction(models.Model):
    SETTLEMENT_CHOICES = [
        ("purchase", "Purchase"),
        ("sale", "Sale"),
        ("lodge_mortgage", "Lodge Mortgage"),
        ("discharge_mortgage", "Discharge Mortgage"),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('ready', 'Ready'),
        ('settling', 'Settling'),
        ('settled', 'Settled'),
    ]

    solicitor = models.ForeignKey(Solicitor, on_delete=models.CASCADE, related_name="instructions")
    file_reference = models.CharField(max_length=50, unique=True, default=generate_file_reference)
    purchaser_name = models.CharField(max_length=255, blank=True, null=True)
    purchaser_email = models.EmailField(blank=True, null=True)
    purchaser_address = models.CharField(max_length=255, blank=True, null=True)
    purchaser_mobile = models.CharField(max_length=20, blank=True, null=True)
    seller_name = models.CharField(max_length=255, blank=True, null=True)
    seller_address = models.CharField(max_length=255, blank=True, null=True)
    title_search = models.CharField(max_length=255, blank=True, null=True)
    property_address = models.CharField(max_length=255, blank=True, null=True)
    title_reference = models.TextField(blank=False, null=False)  # Required
    settlement_type = models.CharField(max_length=100, choices=SETTLEMENT_CHOICES, default="purchase")
    settlement_date = models.DateField(blank=True, null=True)
    settlement_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_reference} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        logger.info(f"Saving Instruction: {self.file_reference}")
        super().save(*args, **kwargs)
        logger.info(f"Instruction {self.file_reference} saved successfully.")

    def delete(self, *args, **kwargs):
        logger.info(f"Deleting Instruction: {self.file_reference}")
        super().delete(*args, **kwargs)
        logger.info(f"Instruction {self.file_reference} deleted successfully.")

# Document Model
DOCUMENT_TYPE_CHOICES = [
    ('contract', 'Contract'),
    ('title_search', 'Title Search'),
    ('id_verification', 'Verification of ID'),
    ('form_qro_d2', 'Form QRO D2'),
    ('trust_document', 'Trust Document'),
    ('asic_extract', 'ASIC Extract'),
    ('gst_withholding', 'GST Withholding'),
]

class Document(models.Model):
    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='settlements/documents/')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, default='contract')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.instruction.file_reference}"

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField(blank=True, null=True)  # Allow empty messages if file is present
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)  # Added file field
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def sender_name(self):
        """Return sender name or 'Settlex' for admin messages."""
        if self.sender.is_superuser:
            return "Settlex"
        return self.sender.get_full_name() or self.sender.username

    def formatted_timestamp(self):
        """Format timestamp for Brisbane timezone."""
        brisbane_tz = pytz.timezone("Australia/Brisbane")
        return localtime(self.timestamp, brisbane_tz).strftime('%d %b %Y, %I:%M %p')

    def __str__(self):
        return f"{self.sender_name()} -> {self.recipient.username}: {self.message[:50] if self.message else 'File'}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    two_factor_authenticated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'