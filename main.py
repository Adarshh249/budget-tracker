from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from sklearn.linear_model import LinearRegression
from pydantic import BaseModel
import numpy as np
import models

# Create app
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Monthly budget
MONTHLY_BUDGET = 10000


# -----------------------------
# Schema
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
# CREATE USER
# -----------------------------
@app.post("/create-user")
def create_user(name: str, db: Session = Depends(get_db)):
    user = models.User(name=name)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# -----------------------------
# ADD TRANSACTION
# -----------------------------
@app.post("/transactions")
def add_transaction(
    t: TransactionSchema,
    user_id: int,
    db: Session = Depends(get_db)
):
    new_transaction = models.Transaction(
        **t.dict(),
        user_id=user_id
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


# -----------------------------
# GET TRANSACTIONS
# -----------------------------
@app.get("/transactions")
def get_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    return transactions


# -----------------------------
# TOTAL EXPENSE
# -----------------------------
@app.get("/total-expense")
def total_expense(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    total = sum(
        t.amount for t in transactions
        if t.type == "EXPENSE"
    )

    return {
        "total_expense": total
    }


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
            category_totals[t.category] = (
                category_totals.get(t.category, 0) + t.amount
            )

    insights = []

    insights.append(f"Total spending is ₹{total}")

    if category_totals:
        max_category = max(
            category_totals,
            key=category_totals.get
        )

        insights.append(
            f"You spent most on {max_category}"
        )

        percentage = (
            category_totals[max_category] / total
        ) * 100

        insights.append(
            f"{max_category} takes {percentage:.2f}% of spending"
        )

    return {
        "insights": insights
    }


# -----------------------------
# BUDGET STATUS
# -----------------------------
@app.get("/budget-status")
def budget_status(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    total = sum(
        t.amount for t in transactions
        if t.type == "EXPENSE"
    )

    remaining = MONTHLY_BUDGET - total

    percentage = (
        (total / MONTHLY_BUDGET) * 100
        if MONTHLY_BUDGET > 0 else 0
    )

    return {
        "budget": MONTHLY_BUDGET,
        "spent": total,
        "remaining": remaining,
        "percentage_used": round(percentage, 2)
    }


# -----------------------------
# ML PREDICTION
# -----------------------------
@app.get("/prediction")
def prediction(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    expenses = [
        t.amount for t in transactions
        if t.type == "EXPENSE"
    ]

    # Need minimum data
    if len(expenses) < 2:
        return {
            "predicted_monthly_spend": 0,
            "algorithm": "Linear Regression",
            "message": "Not enough data"
        }

    # Training data
    X = np.array(
        range(len(expenses))
    ).reshape(-1, 1)

    y = np.array(expenses)

    # Train ML model
    model = LinearRegression()
    model.fit(X, y)

    # Predict next expense
    future_day = np.array([
        [len(expenses) + 1]
    ])

    predicted_value = model.predict(
        future_day
    )[0]

    return {
        "predicted_monthly_spend": round(
            float(predicted_value), 2
        ),
        "algorithm": "Linear Regression"
    }


# -----------------------------
# SMART ALERTS
# -----------------------------
@app.get("/alerts")
def get_alerts(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id
    ).all()

    alerts = []

    total = sum(
        t.amount for t in transactions
        if t.type == "EXPENSE"
    )

    # Budget alerts
    if total > MONTHLY_BUDGET:
        alerts.append(
            "⚠ You exceeded your monthly budget!"
        )

    elif total > 0.8 * MONTHLY_BUDGET:
        alerts.append(
            "⚠ You are close to your budget limit"
        )

    # Category anomaly detection
    category_totals = {}

    for t in transactions:
        if t.type == "EXPENSE":
            category_totals[t.category] = (
                category_totals.get(t.category, 0)
                + t.amount
            )

    if category_totals:
        max_category = max(
            category_totals,
            key=category_totals.get
        )

        max_value = category_totals[max_category]

        if max_value > 0.5 * total:
            alerts.append(
                f"⚠ High spending detected in {max_category}"
            )

    # Default alert
    if not alerts:
        alerts.append(
            "✅ Spending is under control"
        )

    return {
        "alerts": alerts
    }


# -----------------------------
# HOME
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "Smart Budget Tracker API is running"
    }