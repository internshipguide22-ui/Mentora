# Password Reset Email Setup Guide

## Current Behavior
Emails are printed to the **console/terminal** where Django server runs, not sent to actual email addresses.

## How to Test Password Reset NOW

1. Start your Django server:
   ```bash
   python manage.py runserver
   ```

2. Go to password reset page and enter an email

3. **Check your terminal/console** where the server is running - you'll see the email output with the reset link

4. Copy the reset link from the console and paste it in your browser

## How to Send Real Emails (Gmail)

### Step 1: Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Enable 2-Step Verification (Security → 2-Step Verification)
3. Go to Security → App passwords
4. Generate an app password for "Mail"
5. Copy the 16-character password

### Step 2: Update settings.py

Open `lms_project/settings.py` and find the email configuration section (around line 186).

**Comment out** the console backend:
```python
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Uncomment and configure** the SMTP settings:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your Gmail
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # Replace with your App Password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'  # Replace with your Gmail
```

### Step 3: Test

1. Restart Django server
2. Go to password reset page
3. Enter a valid email address
4. Check your email inbox for the reset link

## Alternative Email Providers

### Outlook/Hotmail
```python
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@outlook.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### Yahoo
```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@yahoo.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Troubleshooting

**Issue**: "SMTPAuthenticationError"
- Solution: Use App Password, not regular password (for Gmail)

**Issue**: "Connection refused"
- Solution: Check firewall/antivirus blocking port 587

**Issue**: Email not received
- Solution: Check spam folder

## Security Note

⚠️ **Never commit email passwords to Git!**

Use environment variables in production:
```python
import os
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```
