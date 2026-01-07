import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

print("=== SMTP Configuration Test ===")
print(f"Email: {SMTP_EMAIL}")
print(f"Password length: {len(SMTP_PASSWORD) if SMTP_PASSWORD else 0}")
print(f"Password (hidden): {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")

try:
    print("\n🔄 Connecting to Gmail SMTP...")
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.set_debuglevel(1)  # Show detailed debug info
    print("✅ Connected to SMTP server")
    
    print("\n🔄 Starting TLS...")
    server.starttls()
    print("✅ TLS started")
    
    print(f"\n🔄 Logging in as {SMTP_EMAIL}...")
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    print("✅ LOGIN SUCCESSFUL!")
    
    server.quit()
    print("\n✅ All tests passed! Gmail authentication is working.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPossible issues:")
    print("1. 2-Step Verification is not enabled on the Gmail account")
    print("2. App Password is incorrect or revoked")
    print("3. Password has extra spaces or characters")
