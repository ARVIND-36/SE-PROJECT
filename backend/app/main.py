from fastapi import FastAPI
from app.users.routes import router as user_router

app = FastAPI(title="Internet Banking System")

# Register routers
app.include_router(user_router)

@app.get("/")
def root():
    return {"message": "Banking System Backend Running"}
