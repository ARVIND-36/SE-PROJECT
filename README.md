# Internet Banking System - SE Project

A comprehensive banking system backend built with FastAPI, PostgreSQL, and Docker.

## 🏗️ Architecture

```
SE-PROJECT/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── auth/                # Authentication module
│   │   │   ├── security.py      # JWT & password hashing
│   │   │   ├── dependencies.py  # Auth dependencies
│   │   │   └── routes.py        # Auth routes (legacy)
│   │   ├── users/               # User management
│   │   │   ├── models.py        # User database models
│   │   │   └── routes.py        # User registration & login
│   │   ├── accounts/            # Bank account management
│   │   │   ├── models.py        # Account models
│   │   │   └── routes.py        # Account operations
│   │   ├── transactions/        # Transaction processing
│   │   │   ├── models.py        # Transaction models
│   │   │   └── routes.py        # Transfer & deposit logic
│   │   ├── loans/               # Loan management
│   │   │   ├── models.py        # Loan models
│   │   │   ├── routes.py        # Loan applications
│   │   │   └── cibil.py         # CIBIL score calculation
│   │   └── db/
│   │       └── database.py      # Database connection
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Backend container config
│   └── .env                    # Environment variables
├── docker-compose.yml          # Docker orchestration
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## ✨ Features

### 1. **User Management**
- User registration with role validation (customer/employee/admin)
- Password validation (min 8 chars, must contain letters & digits)
- JWT-based authentication
- Secure password hashing with bcrypt

### 2. **Account Management**
- Create savings/current accounts
- Unique account number generation
- Account status management (ACTIVE/FROZEN)
- Freeze/unfreeze accounts
- Get user accounts

### 3. **Transaction System**
- Money transfers between accounts
- Cash deposits
- Transaction history tracking
- Real-time balance calculation
- **Daily withdrawal limit: ₹25,000**
- **Account freeze protection** - blocks debits from frozen accounts

### 4. **Loan Management**
- Loan applications with CIBIL score check
- Minimum CIBIL requirement: 600
- Dynamic interest rates:
  - 10% for CIBIL ≥ 700
  - 14% for CIBIL 600-699
- Automatic loan approval/rejection

### 5. **Security Features**
- JWT token authentication
- Environment-based secret key management
- Password hashing with bcrypt 3.2.2
- Role-based access control (RBAC) ready
- Account freeze mechanism

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local development)
- PostgreSQL 15 (if running without Docker)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd SE-PROJECT
```

2. **Environment Configuration**

The `.env` file is already configured with:
```env
DB_USER=bank_user
DB_PASSWORD=bank_pass
DB_HOST=postgres
DB_PORT=5432
DB_NAME=banking_db

SECRET_KEY=your-secret-key-change-this-to-something-secure-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**⚠️ Important:** Change `SECRET_KEY` in production!

3. **Run with Docker**

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

The API will be available at `http://localhost:8000`

### Local Development (Without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update .env DB_HOST to localhost
# DB_HOST=localhost

# Start PostgreSQL separately
docker-compose up -d postgres

# Run server
uvicorn app.main:app --reload
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick API Reference

#### **Users**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/register` | Register new user |
| POST | `/users/login` | Login & get JWT token |

#### **Accounts**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/accounts/create` | Create new account |
| GET | `/accounts/` | Get user accounts |
| POST | `/accounts/freeze?account_id=X` | Freeze account |
| POST | `/accounts/unfreeze?account_id=X` | Unfreeze account |

#### **Transactions**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transactions/transfer` | Transfer money |
| POST | `/transactions/deposit` | Deposit money |

#### **Loans**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/loans/apply` | Apply for loan |

## 🧪 Testing

### 1. Register a User
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123",
    "role": "customer"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

### 3. Create Account
```bash
curl -X POST "http://localhost:8000/accounts/create?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{"account_type": "savings"}'
```

### 4. Deposit Money
```bash
curl -X POST http://localhost:8000/transactions/deposit \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "amount": 10000
  }'
```

### 5. Transfer Money
```bash
curl -X POST http://localhost:8000/transactions/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from_account": 1,
    "to_account": 2,
    "amount": 500
  }'
```

### 6. Apply for Loan
```bash
curl -X POST http://localhost:8000/loans/apply \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "amount": 100000
  }'
```

### 7. Test Daily Limit
```bash
# Try transferring more than ₹25,000 in a day
curl -X POST http://localhost:8000/transactions/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from_account": 1,
    "to_account": 2,
    "amount": 26000
  }'
# Expected: "Daily withdrawal limit exceeded"
```

### 8. Test Account Freeze
```bash
# Freeze account
curl -X POST "http://localhost:8000/accounts/freeze?account_id=1"

# Try transfer (should fail)
curl -X POST http://localhost:8000/transactions/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from_account": 1,
    "to_account": 2,
    "amount": 500
  }'
# Expected: "Account is frozen"
```

## 🔧 Technology Stack

- **Backend Framework**: FastAPI 0.115.6
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0.36
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib + bcrypt 3.2.2
- **Containerization**: Docker & Docker Compose
- **ASGI Server**: Uvicorn

## 📋 Business Rules

### Daily Withdrawal Limit
- Maximum ₹25,000 per day per account
- Applies only to DEBIT transactions
- Calculated from midnight to midnight
- Enforced before balance check

### Account Freeze
- Frozen accounts cannot make debits
- Can still receive credits
- Admin can freeze/unfreeze accounts
- Status: ACTIVE or FROZEN

### Loan Approval Logic
- Minimum CIBIL score: 600
- Interest rates:
  - CIBIL ≥ 700: 10% interest
  - CIBIL 600-699: 14% interest
- Below 600: Automatic rejection

## 🐛 Known Issues & Fixes

### bcrypt Version Error
If you see `"password cannot be longer than 72 bytes"` error:
```bash
pip install bcrypt==3.2.2
```

### Database Connection Issues
Ensure PostgreSQL is running:
```bash
docker-compose up -d postgres
docker-compose logs postgres
```

## 🔒 Security Considerations

- ✅ Environment variables for secrets
- ✅ Password hashing with bcrypt
- ✅ JWT token expiration (60 minutes)
- ✅ Input validation on all endpoints
- ✅ Role-based validation
- ⚠️ TODO: Add rate limiting
- ⚠️ TODO: Implement HTTPS in production
- ⚠️ TODO: Add refresh token mechanism


## 📝 Development Notes

### Adding New Endpoints
1. Create model in appropriate `models.py`
2. Create routes in `routes.py`
3. Register router in `main.py`
4. Run migrations (if using Alembic)

### Database Migrations
Currently using `Base.metadata.create_all()` for table creation. For production, consider:
```bash
pip install alembic
alembic init migrations
```

