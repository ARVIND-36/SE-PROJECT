from fastapi import FastAPI
from app.users.routes import router as user_router
from app.accounts.routes import router as account_router
from app.loans.routes import router as loan_router
from app.transactions.routes import router as transaction_router
from app.auth.auth_routes import router as auth_router

app = FastAPI(title="Internet Banking System")

# Register routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(loan_router)

@app.get("/")
def root():
    return {"message": "Banking System Backend Running"}
