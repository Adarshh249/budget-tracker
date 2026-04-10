from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from pydantic import BaseModel

# Create app
app = FastAPI()

# CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# -----------------------------
# Schema
# -----------------------------
class TransactionSchema(BaseModel):
    type: str
    category: str
    amount: float
    description: str


# -----------------------------
# DB Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# USER API
# -----------------------------
@app.post("/create-user")
def create_user(name: str, db: Session = Depends(get_db)):
    user = models.User(name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# -----------------------------
# TRANSACTION APIs
# -----------------------------
@app.post("/transactions")
def add_transaction(
    t: TransactionSchema,
    user_id: int,
    db: Session = Depends(get_db)
):
    new_t = models.Transaction(**t.dict(), user_id=user_id)
    db.add(new_t)
    db.commit()
    db.refresh(new_t)
    return new_t


@app.get("/transactions")
def get_transactions(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()


# -----------------------------
# TOTAL EXPENSE
# -----------------------------
@app.get("/total-expense")
def total_expense(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    total = sum(t.amount for t in transactions if t.type == "EXPENSE")
    return {"total_expense": total}


# -----------------------------
# CATEGORY SUMMARY
# -----------------------------
@app.get("/category-summary")
def category_summary(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    summary = {}

    for t in transactions:
        if t.type == "EXPENSE":
            summary[t.category] = summary.get(t.category, 0) + t.amount

    return summary


# -----------------------------
# INSIGHTS
# -----------------------------
@app.get("/insights")
def get_insights(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    total = 0
    category_totals = {}

    for t in transactions:
        if t.type == "EXPENSE":
            total += t.amount
            category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

    insights = []

    insights.append(f"Total spending is {total}")

    if category_totals:
        max_category = max(category_totals, key=category_totals.get)
        insights.append(f"You spent most on {max_category}")

        percentage = (category_totals[max_category] / total) * 100
        insights.append(f"{max_category} takes {percentage:.2f}% of your spending")

    return {"insights": insights}


# -----------------------------
# BUDGET STATUS
# -----------------------------
MONTHLY_BUDGET = 10000

@app.get("/budget-status")
def budget_status(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    total = sum(t.amount for t in transactions if t.type == "EXPENSE")

    remaining = MONTHLY_BUDGET - total
    percentage = (total / MONTHLY_BUDGET) * 100 if MONTHLY_BUDGET > 0 else 0

    return {
        "budget": MONTHLY_BUDGET,
        "spent": total,
        "remaining": remaining,
        "percentage_used": round(percentage, 2)
    }


# -----------------------------
# PREDICTION
# -----------------------------
@app.get("/prediction")
def prediction(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    total = sum(t.amount for t in transactions if t.type == "EXPENSE")

    days_passed = 10  # simple assumption
    if days_passed == 0:
        return {"predicted_monthly_spend": 0}

    daily_avg = total / days_passed
    predicted = daily_avg * 30

    return {"predicted_monthly_spend": round(predicted, 2)}


# -----------------------------
# ALERTS
# -----------------------------
@app.get("/alerts")
def get_alerts(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    alerts = []

    total = sum(t.amount for t in transactions if t.type == "EXPENSE")

    # Budget alerts
    if total > MONTHLY_BUDGET:
        alerts.append("⚠ You exceeded your budget!")
    elif total > 0.8 * MONTHLY_BUDGET:
        alerts.append("⚠ You are near your budget limit")

    # Category anomaly
    category_totals = {}
    for t in transactions:
        if t.type == "EXPENSE":
            category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

    if category_totals:
        max_category = max(category_totals, key=category_totals.get)
        if category_totals[max_category] > 0.5 * total:
            alerts.append(f"⚠ High spending in {max_category}")

    if not alerts:
        alerts.append("✅ Spending is under control")

    return {"alerts": alerts}


# -----------------------------
# HOME
# -----------------------------
@app.get("/")
def home():
    return {"message": "Budget Tracker API is running"}