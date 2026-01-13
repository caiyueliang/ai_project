from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .routers import auth, funds, backtest, users
from .models import Fund

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
app.include_router(users.router)
app.include_router(funds.router)
app.include_router(backtest.router)


@app.on_event("startup")
def ensure_seed_data():
    db = SessionLocal()
    try:
        has_funds = db.query(Fund.id).first() is not None
        if not has_funds:
            db.add_all(
                [
                    Fund(code="000001", name="华夏成长", fund_type="混合型"),
                    Fund(code="000002", name="华夏大盘精选", fund_type="混合型"),
                    Fund(code="110011", name="易方达中小盘", fund_type="混合型"),
                ]
            )
            db.commit()
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Fund Quant Platform API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
