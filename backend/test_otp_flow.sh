#!/bin/bash

echo "=========================================="
echo "🏦 Banking System OTP Authentication Test"
echo "=========================================="

BASE_URL="http://localhost:8000"

echo -e "\n📝 Step 1: Register - Send OTP"
echo "Registering new user..."

REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register/init" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "phone": "+91-9876543210",
    "pan_number": "ABCDE1234F",
    "date_of_birth": "1990-01-15",
    "address": "123 Test Street, Test City",
    "monthly_income": 75000.0,
    "employment_status": "EMPLOYED"
  }')

echo "$REGISTER_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_RESPONSE"

echo -e "\n🔍 Check Docker logs for OTP:"
echo "Run: docker logs banking_backend --tail 5"
echo ""
read -p "Enter the OTP from logs: " OTP

echo -e "\n✅ Step 2: Complete Registration with OTP"

VERIFY_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register/verify" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"test@example.com\",
    \"otp\": \"$OTP\",
    \"password\": \"Test123456\",
    \"registration_data\": {
      \"full_name\": \"Test User\",
      \"email\": \"test@example.com\",
      \"phone\": \"+91-9876543210\",
      \"pan_number\": \"ABCDE1234F\",
      \"date_of_birth\": \"1990-01-15\",
      \"address\": \"123 Test Street, Test City\",
      \"monthly_income\": 75000.0,
      \"employment_status\": \"EMPLOYED\"
    }
  }")

echo "$VERIFY_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$VERIFY_RESPONSE"

ACCOUNT_NUMBER=$(echo "$VERIFY_RESPONSE" | grep -oP '(?<="account_number": ")[^"]*' | head -1)

if [ -n "$ACCOUNT_NUMBER" ]; then
  echo -e "\n✅ Registration successful!"
  echo "Account Number: $ACCOUNT_NUMBER"
  
  echo -e "\n🔐 Step 3: Login with Account Number - Send OTP"
  
  LOGIN_INIT=$(curl -s -X POST "$BASE_URL/auth/login/init" \
    -H "Content-Type: application/json" \
    -d "{\"account_number\": \"$ACCOUNT_NUMBER\"}")
  
  echo "$LOGIN_INIT" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_INIT"
  
  echo -e "\n🔍 Check Docker logs for new OTP:"
  echo "Run: docker logs banking_backend --tail 5"
  echo ""
  read -p "Enter the OTP from logs: " LOGIN_OTP
  
  echo -e "\n✅ Step 4: Complete Login with OTP"
  
  LOGIN_VERIFY=$(curl -s -X POST "$BASE_URL/auth/login/verify" \
    -H "Content-Type: application/json" \
    -d "{
      \"account_number\": \"$ACCOUNT_NUMBER\",
      \"otp\": \"$LOGIN_OTP\"
    }")
  
  echo "$LOGIN_VERIFY" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_VERIFY"
  
  TOKEN=$(echo "$LOGIN_VERIFY" | grep -oP '(?<="access_token": ")[^"]*' | head -1)
  
  if [ -n "$TOKEN" ]; then
    echo -e "\n🎉 Login successful! Token received."
    echo -e "\n📊 Step 5: Check CIBIL Score"
    
    CIBIL=$(curl -s "$BASE_URL/loans/cibil-score" \
      -H "Authorization: Bearer $TOKEN")
    
    echo "$CIBIL" | python3 -m json.tool 2>/dev/null || echo "$CIBIL"
    
    echo -e "\n✅ All tests completed successfully!"
  fi
else
  echo -e "\n❌ Registration failed"
fi
