# 🔒 Security Setup Guide

## Environment Variables Configuration

This project uses environment variables to keep sensitive data secure. **NEVER commit the `.env` file to git**.

### Step 1: Create Your Local .env File

Copy the example file:
```bash
cp backend/.env.example backend/.env
```

### Step 2: Configure Your Environment Variables

Edit `backend/.env` with your actual credentials:

```env
# Database Configuration
DB_USER=bank_user
DB_PASSWORD=your_secure_database_password
DB_HOST=postgres
DB_PORT=5432
DB_NAME=banking_db

# JWT Configuration (Generate a secure random key)
SECRET_KEY=your-secure-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Gmail SMTP Configuration for OTP
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
BANK_NAME=YourBankName
```

### Step 3: Generate Gmail App Password

To enable OTP email functionality:

1. **Enable 2-Step Verification** on your Gmail account:
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification" if not already enabled

2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" or "Other" and give it a name like "Banking App"
   - Copy the 16-character password
   - Paste it in `SMTP_PASSWORD` (remove spaces)

3. **Update .env**:
   ```env
   SMTP_EMAIL=youremail@gmail.com
   SMTP_PASSWORD=abcdefghijklmnop  # 16 characters, no spaces
   ```

### Step 4: Generate Secure SECRET_KEY

Use Python to generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as your `SECRET_KEY` in `.env`

## ⚠️ Security Checklist Before Pushing to GitHub

- [ ] Verify `.env` is in `.gitignore`
- [ ] Check no credentials in git: `git status` (should not show `.env`)
- [ ] `.env.example` has placeholder values only
- [ ] No hardcoded passwords in code files
- [ ] All sensitive data loaded via `os.getenv()`
- [ ] Remove any test credentials from code

## 🚫 What NOT to Commit

**NEVER commit these to git:**
- `backend/.env` - Contains real credentials
- Any file with actual passwords, API keys, or tokens
- Database connection strings with credentials
- Gmail passwords or app passwords

## ✅ What TO Commit

**Safe to commit:**
- `backend/.env.example` - Template with placeholders
- `.gitignore` - Ensures `.env` is ignored
- Code using `os.getenv()` to load variables
- Documentation about setup process

## 🔍 Verify Before Pushing

Run these commands to verify security:

```bash
# Check .env is not tracked
git status | grep -q ".env" && echo "⚠️  WARNING: .env detected!" || echo "✅ Safe"

# Check no credentials in staged files
git diff --cached | grep -i "password\|secret\|smtp" || echo "✅ No credentials found"
```

## 📝 Team Setup

When team members clone the repo:

1. Copy `.env.example` to `.env`
2. Ask admin for credentials (via secure channel, NOT git)
3. Configure their own Gmail app password if needed
4. Never commit `.env` file

## 🛡️ Production Deployment

For production:
- Use environment variables from hosting platform
- Never store credentials in code or docker-compose.yml
- Use secrets management (AWS Secrets Manager, etc.)
- Rotate credentials regularly
- Use strong, unique passwords for database
