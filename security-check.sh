#!/bin/bash

# Security Pre-Push Verification Script
# Run this before pushing to GitHub

echo "🔍 Checking security before GitHub push..."
echo ""

# Check 1: .env file is not tracked
echo "1️⃣  Checking if .env is ignored..."
if git ls-files --error-unmatch backend/.env 2>/dev/null; then
    echo "   ❌ DANGER: backend/.env is tracked by git!"
    echo "   Run: git rm --cached backend/.env"
    EXIT_CODE=1
else
    echo "   ✅ backend/.env is properly ignored"
fi

# Check 2: No credentials in staged changes
echo ""
echo "2️⃣  Checking staged files for credentials..."
SUSPICIOUS=$(git diff --cached | grep -i "password.*=.*[^a-z]" | grep -v "getenv\|SMTP_PASSWORD\|DB_PASSWORD\|hash_password\|verify_password\|your-" || true)
if [ ! -z "$SUSPICIOUS" ]; then
    echo "   ⚠️  WARNING: Possible credentials found:"
    echo "$SUSPICIOUS"
    EXIT_CODE=1
else
    echo "   ✅ No obvious credentials in staged files"
fi

# Check 3: .env.example exists
echo ""
echo "3️⃣  Checking for .env.example..."
if [ -f "backend/.env.example" ]; then
    echo "   ✅ backend/.env.example exists"
else
    echo "   ⚠️  WARNING: backend/.env.example not found"
fi

# Check 4: .gitignore includes .env
echo ""
echo "4️⃣  Checking .gitignore..."
if grep -q "^\.env$" .gitignore; then
    echo "   ✅ .env is in .gitignore"
else
    echo "   ❌ WARNING: .env not found in .gitignore"
    EXIT_CODE=1
fi

# Check 5: No actual emails/passwords in code
echo ""
echo "5️⃣  Scanning code files for hardcoded credentials..."
HARDCODED=$(git diff --cached | grep -E "@gmail\.com|[0-9]{16}" | grep -v "example\|your-\|test@\|getenv" || true)
if [ ! -z "$HARDCODED" ]; then
    echo "   ⚠️  WARNING: Possible hardcoded email/password:"
    echo "$HARDCODED"
    EXIT_CODE=1
else
    echo "   ✅ No hardcoded credentials detected"
fi

echo ""
echo "================================"
if [ -z "$EXIT_CODE" ]; then
    echo "✅ ALL CHECKS PASSED - Safe to push!"
    exit 0
else
    echo "❌ SECURITY ISSUES DETECTED - DO NOT PUSH!"
    echo ""
    echo "Fix the issues above before pushing to GitHub"
    exit 1
fi
