import logging
from django import forms
from urllib.parse import quote
from django.contrib.auth.models import User
from .models import Instruction, Document, Firm, Solicitor
from two_factor.forms import TOTPDeviceForm, AuthenticationTokenForm
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import base64
from io import BytesIO
from django.core.exceptions import ValidationError
from binascii import unhexlify, Error as BinasciiError

logger = logging.getLogger(__name__)



class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    firm_name = forms.CharField(max_length=100)
    acn = forms.CharField(max_length=50, required=False)
    office_phone = forms.CharField(max_length=20)
    mobile_phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255)
    postcode = forms.CharField(max_length=10)
    state = forms.CharField(max_length=50)
    profession = forms.ChoiceField(choices=[('solicitor', 'Solicitor'), ('conveyancer', 'Conveyancer')])

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

class InstructionForm(forms.ModelForm):
    class Meta:
        model = Instruction
        fields = [
            'file_reference', 'settlement_type', 'purchaser_name', 'purchaser_email',
            'purchaser_mobile', 'purchaser_address', 'seller_name', 'seller_address',
            'property_address', 'title_search', 'settlement_date', 'status'
        ]
        widgets = {
            'settlement_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        logger.info(f"Saving InstructionForm for property: {self.cleaned_data.get('property_address')}")
        instruction = super().save(commit=False)
        if commit:
            instruction.save()
            logger.info(f"Instruction for property '{instruction.property_address}' has been saved.")
        return instruction

    def clean_file_reference(self):
        file_reference = self.cleaned_data.get('file_reference')
        if Instruction.objects.filter(file_reference=file_reference).exists():
            raise forms.ValidationError('This file reference already exists. Please choose a different one.')
        return file_reference

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file']

    def save(self, instruction_instance, commit=True):
        document = super().save(commit=False)
        document.instruction = instruction_instance
        if commit:
            document.save()
            logger.info(f"Document '{document.name}' uploaded for instruction {document.instruction.file_reference}")
        return document

class DummyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        logger.debug("👤 DummyForm initialized with user: %s", self.user)
        super().__init__(*args, **kwargs)

class WelcomeStepForm(DummyForm):
    """Placeholder form for the welcome step."""
    pass

class ValidationStepForm(AuthenticationTokenForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.device = kwargs.pop('device', None)
        logger.debug("🔐 ValidationStepForm initialized with user: %s and device: %s", self.user, self.device)
        super().__init__(self.user, self.device, *args, **kwargs)

    def clean_token(self):
        token = self.cleaned_data.get("token")
        if not self.device:
            logger.warning("⚠️ No device assigned to ValidationStepForm.")
            raise ValidationError("Internal error: device missing.")

        if not self.device.verify_token(token):
            logger.warning("❌ Invalid token entered for device ID: %s", self.device.id)
            raise ValidationError("Entered token is not valid. Please check your device time and try again.")

        logger.info("✅ Token validated for device ID: %s", self.device.id)
        return token

    def save(self):
        """Mark device as confirmed after successful token validation."""
        if self.device:
            self.device.confirmed = True
            self.device.save()
            logger.info("✅ Device %s confirmed and saved", self.device.id)
        return self.device

class CustomTOTPDeviceForm(TOTPDeviceForm):
    token = forms.CharField(label="Token", max_length=6)

    def __init__(self, *args, **kwargs):
        self.device = kwargs.pop('device', None)
        logger.debug("🛠 CustomTOTPDeviceForm INIT: device=%s", self.device)
        super().__init__(*args, **kwargs)

        self.qr_code = None
        self.secret_b32 = None
        if self.device:
            try:
                # Convert hex key to base32
                key_bytes = unhexlify(self.device.key.encode())
                self.secret_b32 = base64.b32encode(key_bytes).decode("utf-8").replace("=", "")
                issuer = "Settlex"
                label = quote(f"{issuer}:{self.device.user.email}")
                config_url = (
                    f"otpauth://totp/{label}?secret={self.secret_b32}"
                    f"&issuer={issuer}&algorithm=SHA1&digits=6&period=30"
                )

                # Generate QR Code
                qr = qrcode.make(config_url)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                self.qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")

                logger.debug("📡 QR code generated for: %s", config_url)
            except BinasciiError:
                logger.error("🚨 Device key is not a valid hex string: %s", self.device.key)
            except Exception as e:
                logger.exception("⚠️ Failed to generate QR code")

    def clean_token(self):
        token = self.cleaned_data.get("token")
        if not self.device or not self.device.verify_token(token):
            raise ValidationError("Entered token is not valid. Ensure your device time is accurate.")
        return token

    def save(self):
        if self.device:
            self.device.confirmed = True
            self.device.save()
            logger.debug("✅ TOTP device confirmed and saved: %s", self.device)
        return self.device

    def get_context_data(self):
        context = {
            'qr_code_base64': self.qr_code,
            'totp_secret': self.secret_b32,
        }
        logger.debug("📡 CustomTOTPDeviceForm.get_context_data(): %s", context)
        return context