from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, funds, backtest, users

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fund Quant Platform API")

# CORS
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(funds.router)
app.include_router(backtest.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Fund Quant Platform API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
