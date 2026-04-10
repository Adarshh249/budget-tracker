from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create DB tables
Base.metadata.create_all(bind=engine)

# -----------------------------
# Schema (for validation)
# -----------------------------
class TransactionSchema(BaseModel):
    type: str
    category: str
    amount: float
    description: str


# -----------------------------
# Database Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# POST API (Add Transaction)
# -----------------------------
@app.post("/transactions")
def add_transaction(t: TransactionSchema, db: Session = Depends(get_db)):
    new_t = models.Transaction(**t.dict())
    db.add(new_t)
    db.commit()
    db.refresh(new_t)
    return new_t


# -----------------------------
# GET API (Fetch Transactions)
# -----------------------------
@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()


@app.get("/total-expense")
def total_expense(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()

    total = sum(t.amount for t in transactions if t.type == "EXPENSE")

    return {"total_expense": total}

@app.get("/category-summary")
def category_summary(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()

    summary = {}

    for t in transactions:
        if t.type == "EXPENSE":
            if t.category in summary:
                summary[t.category] += t.amount
            else:
                summary[t.category] = t.amount

    return summary

@app.get("/insights")
def get_insights(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()

    total = 0
    category_totals = {}

    # Calculate totals
    for t in transactions:
        if t.type == "EXPENSE":
            total += t.amount

            if t.category in category_totals:
                category_totals[t.category] += t.amount
            else:
                category_totals[t.category] = t.amount

    insights = []

    # Insight 1: Total spending
    insights.append(f"Total spending is {total}")

    # Insight 2: Highest category
    if category_totals:
        max_category = max(category_totals, key=category_totals.get)
        insights.append(f"You spent most on {max_category}")

        percentage = (category_totals[max_category] / total) * 100
        insights.append(f"{max_category} takes {percentage:.2f}% of your spending")

    return {"insights": insights}

@app.get("/")
def home():
    return {"message": "Budget Tracker API is running"}

# -----------------------------
# Budget + Prediction API
# -----------------------------
MONTHLY_BUDGET = 10000  # you can change this

@app.get("/budget-status")
def budget_status(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()

    total = sum(t.amount for t in transactions if t.type == "EXPENSE")

    remaining = MONTHLY_BUDGET - total
    percentage = (total / MONTHLY_BUDGET) * 100 if MONTHLY_BUDGET > 0 else 0

    return {
        "budget": MONTHLY_BUDGET,
        "spent": total,
        "remaining": remaining,
        "percentage_used": round(percentage, 2)
    }


@app.get("/prediction")
def prediction(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()

    total = sum(t.amount for t in transactions if t.type == "EXPENSE")

    days_passed = 10  # simple assumption (later dynamic)
    if days_passed == 0:
        return {"prediction": 0}

    daily_avg = total / days_passed
    predicted_monthly = daily_avg * 30

    return {
        "predicted_monthly_spend": round(predicted_monthly, 2)
    }