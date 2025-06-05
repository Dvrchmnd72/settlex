from pathlib import Path
import os
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-y%h2!$!-^(2!)$dcs2bfbbnxq&)5e@%gw9!-hg%1o--e-31t3@'

# Set DEBUG to False in production to avoid exposing error details
DEBUG = True  # Changed from True for production; use True only during development

ALLOWED_HOSTS = [
    "settlex.onestoplegal.com.au",
    "testserver",  # Allow test client requests
]

# Trusted CSRF & Secure Cookies
CSRF_TRUSTED_ORIGINS = [
    "https://settlex.onestoplegal.com.au",
    "https://onestoplegal.com.au",
]

# Secure Headers for Reverse Proxy & HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django_extensions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'settlements_app.apps.SettlementsAppConfig',
    'corsheaders',  # Fix Cross-Origin Requests
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'qrcode',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Basic security middleware
    'django.contrib.sessions.middleware.SessionMiddleware',  # Manages session data
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Handles authentication
    'django_otp.middleware.OTPMiddleware',  # OTP handling for 2FA (should be placed early)
    'corsheaders.middleware.CorsMiddleware',  # Ensure CORS Middleware is included
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'Settlex.middleware.enforce_2fa.Enforce2FAMiddleware',  # Custom middleware for 2FA enforcement
    'django.contrib.messages.middleware.MessageMiddleware',  # For flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Protection against clickjacking
    'two_factor.middleware.threadlocals.ThreadLocals',  # Optional: Useful for managing 2FA context
]


ROOT_URLCONF = 'Settlex.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'settlements_app', 'templates'),
            os.path.join(BASE_DIR, 'settlements_app', 'templates', 'admin'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "settlements_app.context_processors.chat_visibility",
            ],
        },
    },
]

WSGI_APPLICATION = 'Settlex.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Set Australia/Brisbane Timezone
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Brisbane'
USE_I18N = True
USE_TZ = True

# Static & Media Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure media directory permissions
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT, mode=0o775)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'info@onestoplegal.com.au'
EMAIL_HOST_PASSWORD = 'bxkystkrmmrcpdyz'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Authentication Backend
AUTHENTICATION_BACKENDS = [
    'settlements_app.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Avoid reverse_lazy here, just use the resolved path
LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URL = reverse_lazy("settlements_app:my_settlements")
LOGOUT_REDIRECT_URL = reverse_lazy("settlements_app:home")



# Extend session duration to avoid logout on refresh
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = True  # Ensure this is True in production with HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF & Security Enhancements
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF Token
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = True  # Store CSRF token in session

# 🔐 Two-Factor Authentication Wizard Storage
TWO_FACTOR_WIZARD_CLASS = 'two_factor.views.utils.WizardStorageSession'

# (Optional) Dummy gateways for development or if SMS/call are unused
TWO_FACTOR_CALL_GATEWAY = 'two_factor.gateways.fake.Fake'
TWO_FACTOR_SMS_GATEWAY = 'two_factor.gateways.fake.Fake'


# Additional Security Headers
SECURE_BROWSER_XSS_FILTER = True  # Prevent Cross-Site Scripting (XSS)
SECURE_HSTS_SECONDS = 31536000  # Enforce HTTPS for 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME sniffing attacks
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Fix Cross-Origin Login & Chat Issues
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://settlex.onestoplegal.com.au",
    "https://onestoplegal.com.au",
]

SILENCED_SYSTEM_CHECKS = ["admin.E404"]

# Logging for Debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'settlements_app': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Ensure file permissions for logs
if not os.path.exists(os.path.join(BASE_DIR, 'django.log')):
    with open(os.path.join(BASE_DIR, 'django.log'), 'a'):
        os.utime(os.path.join(BASE_DIR, 'django.log'), None)
    os.chmod(os.path.join(BASE_DIR, 'django.log'), 0o664)