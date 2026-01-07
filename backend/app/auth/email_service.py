import smtplib
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Gmail Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SMTP_EMAIL")
SENDER_PASSWORD = os.getenv("SMTP_PASSWORD")  # Gmail App Password
BANK_NAME = os.getenv("BANK_NAME", "SecureBank")

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(recipient_email: str, otp: str, purpose: str = "verification"):
    """Send OTP via Gmail SMTP"""
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("⚠️  Gmail credentials not configured. OTP not sent.")
        print(f"📧 OTP for {recipient_email}: {otp}")
        return True
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = f"{BANK_NAME} - OTP Verification"
        message["From"] = f"{BANK_NAME} <{SENDER_EMAIL}>"
        message["To"] = recipient_email
        
        # Email body
        if purpose == "REGISTRATION":
            text = f"""
Dear Customer,

Your OTP for account registration is: {otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.

Regards,
{BANK_NAME} Team
            """
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2563eb;">Welcome to {BANK_NAME}!</h2>
                <p>Your OTP for account registration is:</p>
                <h1 style="color: #059669; letter-spacing: 5px;">{otp}</h1>
                <p style="color: #dc2626;">This OTP is valid for 5 minutes.</p>
                <p><strong>Do not share this OTP with anyone.</strong></p>
                <hr style="margin: 20px 0;">
                <p style="color: #6b7280; font-size: 12px;">
                  If you didn't request this, please ignore this email.
                </p>
              </body>
            </html>
            """
        elif purpose == "LOGIN":
            text = f"""
Dear Customer,

Your OTP for login verification is: {otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.

Regards,
{BANK_NAME} Team
            """
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #2563eb;">Login Verification</h2>
                <p>Your OTP for login is:</p>
                <h1 style="color: #059669; letter-spacing: 5px;">{otp}</h1>
                <p style="color: #dc2626;">This OTP is valid for 5 minutes.</p>
                <p><strong>Do not share this OTP with anyone.</strong></p>
                <hr style="margin: 20px 0;">
                <p style="color: #6b7280; font-size: 12px;">
                  If you didn't request this, please contact support immediately.
                </p>
              </body>
            </html>
            """
        else:
            text = f"Your OTP is: {otp}"
            html = f"<p>Your OTP is: <strong>{otp}</strong></p>"
        
        # Attach both plain text and HTML
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        print(f"✅ OTP sent to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send OTP: {e}")
        print(f"📧 OTP for {recipient_email}: {otp}")
        return False

def validate_pan_format(pan: str) -> bool:
    """
    Validate PAN card format: ABCDE1234F
    - First 5 characters: Alphabets
    - Next 4 characters: Numbers
    - Last character: Alphabet
    """
    import re
    pan_pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]$')
    return bool(pan_pattern.match(pan.upper()))
