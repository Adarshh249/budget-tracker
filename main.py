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