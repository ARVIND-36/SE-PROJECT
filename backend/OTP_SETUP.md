# 🔐 Banking System - OTP Authentication Setup

## ✅ Enhanced Authentication Features

Your banking system now has **real-time OTP authentication** like actual banks!

### 🎯 New Features:

1. **PAN Card Registration** - Required for KYC compliance
2. **Email OTP Verification** - Sent via Gmail SMTP
3. **Account Number Login** - More secure than username
4. **Two-Step Authentication** - Init + Verify flow
5. **Auto Account Creation** - Account number generated on registration

---

## 📧 Gmail SMTP Configuration

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** → **2-Step Verification**
3. Follow steps to enable

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** and **Other (Custom name)**
3. Enter name: "Banking App"
4. Click **Generate**
5. Copy the 16-character password

### Step 3: Update .env File
```bash
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # App password from step 2
BANK_NAME=SecureBank
```

---

## 🔄 Registration Flow (2-Step)

### Step 1: Initiate Registration
```bash
POST /auth/register/init
```
**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-9876543210",
  "pan_number": "ABCDE1234F",
  "date_of_birth": "1990-01-15",
  "address": "123 Street, City, State",
  "monthly_income": 50000.0,
  "employment_status": "EMPLOYED"
}
```

**Response:**
```json
{
  "message": "OTP sent to your email",
  "email": "john@example.com",
  "valid_for": "5 minutes"
}
```

### Step 2: Complete Registration with OTP
```bash
POST /auth/register/verify
```
**Request Body:**
```json
{
  "email": "john@example.com",
  "otp": "123456",
  "password": "SecurePass123",
  "registration_data": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+91-9876543210",
    "pan_number": "ABCDE1234F",
    "date_of_birth": "1990-01-15",
    "address": "123 Street, City, State",
    "monthly_income": 50000.0,
    "employment_status": "EMPLOYED"
  }
}
```

**Response:**
```json
{
  "message": "Registration successful",
  "account_number": "ACC123456789012",
  "username": "john",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

## 🔑 Login Flow (2-Step with Account Number)

### Step 1: Initiate Login
```bash
POST /auth/login/init
```
**Request Body:**
```json
{
  "account_number": "ACC123456789012"
}
```

**Response:**
```json
{
  "message": "OTP sent to your registered email",
  "email": "jo***@example.com",
  "valid_for": "5 minutes"
}
```

### Step 2: Complete Login with OTP
```bash
POST /auth/login/verify
```
**Request Body:**
```json
{
  "account_number": "ACC123456789012",
  "otp": "123456"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "name": "John Doe",
    "email": "john@example.com",
    "account_number": "ACC123456789012"
  }
}
```

---

## 🔄 Resend OTP

```bash
POST /auth/otp/resend
```
**Request Body:**
```json
{
  "email": "john@example.com",
  "purpose": "REGISTRATION"  // or "LOGIN"
}
```

**Response:**
```json
{
  "message": "New OTP sent to your email",
  "valid_for": "5 minutes"
}
```

---

## 🧪 Testing Without Gmail (Development)

If Gmail credentials are not configured, the system will:
- ✅ Still work normally
- 📋 Print OTP to console/logs
- 🔍 You can see OTP in Docker logs

```bash
# View OTP in logs
docker logs banking_backend -f
```

---

## 📋 PAN Card Format Validation

**Valid Format:** `ABCDE1234F`
- First 5 characters: Uppercase letters
- Next 4 characters: Digits
- Last character: Uppercase letter

**Examples:**
- ✅ `ABCDE1234F`
- ✅ `XYZPQ5678K`
- ❌ `ABC123456` (invalid format)
- ❌ `abcde1234f` (lowercase not allowed)

---

## 🔒 Security Features

1. **OTP Expiry** - 5 minutes validity
2. **One-time Use** - OTP marked as verified after use
3. **Email Verification** - Ensures valid email address
4. **PAN Uniqueness** - Each PAN can register only once
5. **Email Uniqueness** - Each email can register only once
6. **Secure Password** - Min 8 chars, must have letter + digit
7. **Account Number Generation** - Random 12-digit unique number

---

## 📊 Database Tables

### OTPs Table (New)
```sql
- id
- email
- otp_code (6 digits)
- purpose (REGISTRATION/LOGIN)
- is_verified
- created_at
- expires_at
```

---

## 🚀 Quick Test Commands

### 1. Start Services
```bash
cd /home/arvind/SE-PROJECT
docker-compose up -d --build
```

### 2. Run Migration (Add OTP table)
```bash
docker exec -it banking_backend python migrate_db.py
```

### 3. Test Registration
```bash
curl -X POST http://localhost:8000/auth/register/init \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "phone": "+91-1234567890",
    "pan_number": "ABCDE1234F",
    "date_of_birth": "1990-01-01",
    "address": "Test Address",
    "monthly_income": 50000,
    "employment_status": "EMPLOYED"
  }'
```

### 4. Check OTP in Logs
```bash
docker logs banking_backend --tail 10
```

### 5. Complete Registration
```bash
# Use OTP from logs
curl -X POST http://localhost:8000/auth/register/verify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "otp": "123456",
    "password": "Test123456"
  }'
```

---

## ✅ Benefits of This System

1. **Real Bank Experience** - OTP via email like actual banking
2. **Enhanced Security** - Two-factor authentication
3. **KYC Compliance** - PAN card validation
4. **Account Number Login** - Professional approach
5. **Auto Account Creation** - Seamless onboarding
6. **Masked Email Display** - Privacy protection
7. **OTP Expiry** - Time-bound security

---

## 🎯 Next Steps

1. Update `.env` with your Gmail credentials
2. Rebuild and restart Docker containers
3. Run database migration to add OTP table
4. Test the registration flow
5. Test the login flow with account number

**Your banking system is now production-grade! 🚀**
