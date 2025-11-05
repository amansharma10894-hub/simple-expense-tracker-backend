from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
import json
import os

DATA_FILE = "expenses.json"

class Category(str, Enum):
    food = "Food"
    transport = "Transport"
    utilities = "Utilities"
    entertainment = "Entertainment"
    other = "Other"

class Expense(BaseModel):
    id: str
    amount: float
    category: Category
    description: Optional[str] = None
    date: str

def load_expenses() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_expenses(data: list):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/expenses", response_model=List[Expense])
async def list_expenses():
    return load_expenses()

@app.post("/expenses", response_model=List[Expense])
async def create_expense(expense: Expense):
    expenses = load_expenses()
    expenses.append(expense.dict())
    save_expenses(expenses)
    return expenses

@app.put("/expenses/{expense_id}", response_model=List[Expense])
async def update_expense(expense_id: str, updated: Expense):
    expenses = load_expenses()
    for i, e in enumerate(expenses):
        if e["id"] == expense_id:
            expenses[i] = updated.dict()
            save_expenses(expenses)
            return expenses
    raise HTTPException(status_code=404, detail="Expense not found")

@app.delete("/expenses/{expense_id}", response_model=List[Expense])
async def delete_expense(expense_id: str):
    expenses = load_expenses()
    updated = [e for e in expenses if e["id"] != expense_id]
    if len(updated) == len(expenses):
        raise HTTPException(status_code=404, detail="Expense not found")
    save_expenses(updated)
    return updated