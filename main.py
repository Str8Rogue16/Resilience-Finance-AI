from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
import os
import json

from dotenv import load_dotenv
from anthropic import Anthropic
from fastapi import HTTPException
from opik import track
from opik.integrations.anthropic import track_anthropic

load_dotenv()
anthropic_client = track_anthropic(Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")))

app = FastAPI(title="Resilience Finance AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    transactions_summary: dict = {}

@app.get("/")
def root():
    return {"app": "Resilience Finance AI", "status": "running"}

@track(name="financial_analysis")
def get_ai_insights(income, expenses, df, basic_analysis):
    """Use Claude to provide enhanced financial insights"""
    
    net = income - expenses
    savings_rate = (net / income * 100) if income > 0 else 0
    expense_ratio = (expenses / income * 100) if income > 0 else 100
    
    # Get top spending categories
    if 'category' in df.columns:
        spending_summary = df[df['amount'] < 0].groupby('category')['amount'].sum().abs().to_dict()
        top_categories = sorted(spending_summary.items(), key=lambda x: x[1], reverse=True)[:3]
        categories_text = '\n'.join([f"- {cat}: ${amt:,.2f}" for cat, amt in top_categories])
    else:
        categories_text = "Categories not available"
    
    prompt = f"""You are a financial literacy educator. Analyze this financial data and provide helpful, educational insights.

Financial Summary:
- Income (6 months): ${income:,.2f}
- Expenses (6 months): ${expenses:,.2f}
- Net: ${net:,.2f}
- Savings Rate: {savings_rate:.1f}%
- Expense Ratio: {expense_ratio:.1f}%
- Current Risk Score: {basic_analysis['score']}

Top Spending Categories:
{categories_text}

IMPORTANT: If analyzing data over multiple months, look for trends:
- Has income increased or decreased over the timeframe?
- Are expenses changing significantly?
- Are there large one-time transactions that skew averages?
- Note if the financial situation appears to be improving or worsening over time.

Provide:
1. A brief assessment (2-3 sentences) of overall financial health
2. 3-4 KEY concerns with educational context (why each matters)
3. 3-4 actionable next steps (educational, not advice - use "consider" not "you should")

IMPORTANT: Be educational, not prescriptive. Include disclaimer.

Format as JSON only, no markdown:
{{
  "assessment": "brief overview",
  "concerns": ["concern with context"],
  "recommendations": ["educational next step"]
}}"""

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        # Find JSON between first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
        
        text = text.strip()
        print(f"Parsing JSON: {text[:200]}...")
        
        ai_analysis = json.loads(text)
        return ai_analysis
        
    except Exception as e:
        print(f"AI analysis failed: {e}")
        return None

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Upload CSV and get analysis"""
    
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    
    # Try to find the right columns (handle different bank formats)
    # Look for date column
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'posted' in col.lower()]
    # Look for amount/transaction columns
    amount_cols = [col for col in df.columns if 'amount' in col.lower() or 'transaction' in col.lower()]
    # Look for description columns
    desc_cols = [col for col in df.columns if 'desc' in col.lower() or 'merchant' in col.lower() or 'name' in col.lower()]
    
    # Handle debit/credit columns
    debit_cols = [col for col in df.columns if 'debit' in col.lower()]
    credit_cols = [col for col in df.columns if 'credit' in col.lower()]
    
    # Rename to standard names
    if date_cols:
        df = df.rename(columns={date_cols[0]: 'date'})
    if desc_cols:
        df = df.rename(columns={desc_cols[0]: 'description'})
    
    # Handle amount column
    if debit_cols and credit_cols:
        # Bank format with separate debit/credit columns
        df[debit_cols[0]] = pd.to_numeric(df[debit_cols[0]], errors='coerce').fillna(0)
        df[credit_cols[0]] = pd.to_numeric(df[credit_cols[0]], errors='coerce').fillna(0)
        df['amount'] = df[credit_cols[0]] - df[debit_cols[0]]
    elif amount_cols:
        df = df.rename(columns={amount_cols[0]: 'amount'})
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    else:
        # Use first numeric column as amount
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            df = df.rename(columns={numeric_cols[0]: 'amount'})
        else:
            raise HTTPException(status_code=400, detail="Could not find amount column in CSV")
    
    df = df.dropna(subset=['amount'])
    
    income = df[df['amount'] > 0]['amount'].sum()
    expenses = abs(df[df['amount'] < 0]['amount'].sum())
    net = income - expenses
    
    expense_ratio = (expenses / income * 100) if income > 0 else 100
    savings_rate = (net / income * 100) if income > 0 else 0
    
    if expense_ratio < 50 and savings_rate > 20:
        score = "A"
    elif expense_ratio < 70 and savings_rate > 10:
        score = "B"
    elif expense_ratio < 85:
        score = "C"
    elif expense_ratio < 100:
        score = "D"
    else:
        score = "F"
    
    concerns = []
    recommendations = []
    
    if expense_ratio > 80:
        concerns.append(f"High expense ratio: {expense_ratio:.1f}% of income spent")
        recommendations.append("Review fixed expenses - look for subscriptions to cancel")
    
    if savings_rate < 10:
        concerns.append(f"Low savings rate: only {savings_rate:.1f}% saved")
        recommendations.append("Aim to save at least 10-20% of income")
    
    if net < 0:
        concerns.append(f"Negative cash flow: spending ${abs(net):.2f} more than earning")
        recommendations.append("Urgent: reduce expenses or increase income")
    
    monthly_expenses = expenses / 3
    emergency_months = net / monthly_expenses if monthly_expenses > 0 else 0
    
    if emergency_months < 3:
        concerns.append(f"Low emergency fund: only {emergency_months:.1f} months covered")
        recommendations.append("Build 3-6 months emergency fund as priority")
    
    if not concerns:
        concerns.append("Financial health looks stable")
        recommendations.append("Continue current savings habits")
        recommendations.append("Consider investing surplus funds")
    
    # Get basic analysis
    basic_analysis = {
        "score": score,
        "concerns": concerns[:3],
        "recommendations": recommendations[:3]
    }
    
    # Try AI-enhanced insights
    ai_insights = get_ai_insights(income, expenses, df, basic_analysis)
    
    if ai_insights:
        analysis = {
            "score": score,
            "assessment": ai_insights.get("assessment", ""),
            "concerns": ai_insights.get("concerns", concerns[:3]),
            "recommendations": ai_insights.get("recommendations", recommendations[:3])
        }
    else:
        analysis = basic_analysis
    
    return {
        "transactions": int(len(df)),
        "income": float(round(income, 2)),
        "expenses": float(round(expenses, 2)),
        "analysis": analysis
    }


@app.post("/chat")
@track(name="financial_chat")
async def chat(req: ChatRequest):
    """AI-powered chat about finances"""
    
    # Build context from transaction summary if available
    context = ""
    if req.transactions_summary:
        context = f"""
        User's Financial Context:
            Transactions: {req.transactions_summary.get('transactions', 'N/A')}
            Income: ${req.transactions_summary.get('income', 0):,.2f}
            Expenses: ${req.transactions_summary.get('expenses', 0):,.2f}
            Risk Score: {req.transactions_summary.get('analysis', {}).get('score', 'N/A')}
            """
    
    system_prompt = """You are a financial literacy educator helping people understand their finances better.
            Guidelines:
            - Be educational, not prescriptive (use "consider" not "you should")
            - Explain WHY things matter, don't just tell people what to do
            - Provide context and benchmarks when relevant
            - Keep responses concise (2-3 paragraphs max)
            - Include specific, actionable steps when appropriate
            - Always add disclaimer that this is educational, not financial advice
            
            Look for Trends:
            - Is income increasing or decreasing over time
            - Are expenses growing faster than income
            - Are expenses changing
            - Are there any large one-time transactions that skew the data
            - Note if the situation appears to be improving/worsening over time

            Focus on:
            - Building emergency funds
            - Understanding spending patterns
            - Responsible debt management
            - Savings strategies
            - Financial literacy fundamentals

            Never recommend:
            - Specific investments or stocks
            - Cryptocurrency speculation
            - High-risk financial products
            - Tax evasion strategies""" 
    
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"{context}\n\nQuestion: {req.message}"}
            ]
        )
        
        return {"response": response.content[0].text}
        
    except Exception as e:
        print(f"Chat AI failed: {e}")
        # Fallback to basic tips
        tips = {
            "save": "Consider automating savings transfers - research shows people who automate save 2-3x more than those who don't. Start with even 5-10% of income.",
            "budget": "Track expenses for 1 month to understand patterns. The 50/30/20 rule (needs/wants/savings) is a common framework, but adjust based on your situation.",
            "emergency": "Financial experts generally recommend 3-6 months of expenses in accessible savings. Build this before focusing on other goals.",
            "debt": "The avalanche method (highest interest first) saves the most money. The snowball method (smallest balance first) provides psychological wins. Choose what motivates you.",
        }
        
        msg = req.message.lower()
        for key, tip in tips.items():
            if key in msg:
                return {"response": tip + "\n\nNote: This is educational information only, not financial advice."}
        
        return {"response": "I can help explain financial concepts like budgeting, saving, debt management, and emergency funds. What would you like to learn about?\n\nNote: This is educational information only, not financial advice."}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)