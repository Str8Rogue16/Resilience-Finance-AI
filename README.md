# Resilience Finance AI

**AI-powered financial health assistant built for the Encode.io Hackathon - Financial Health Track**

Resilience Finance AI helps users understand their cash flow, identify financial risk, and build stability without overwhelm. It analyzes income, expenses, and savings to surface exposure areas, estimate emergency readiness, and generate clear, achievable next steps—enabling users to make responsible spending and saving decisions with confidence.

The system applies a **risk and resilience framework** to personal finance, prioritizing clarity, explainability, and practical action over complex dashboards or speculative advice.

---

## 🎯 Problem Statement

**63% of Americans can't cover a $500 emergency.** Most people don't understand where their money actually goes or what financial vulnerabilities they face. Traditional budgeting apps focus on tracking, but don't explain the *why* behind financial health or provide educational guidance.

## ✨ Solution

Upload your bank transaction CSV and receive instant AI-powered financial analysis with:
- **Financial Health Score (A-F)** based on expense ratios, savings rates, and emergency fund coverage
- **Specific risk factors** with educational context explaining why each matters
- **Actionable recommendations** prioritized by impact
- **Plain-language explanations** without jargon or complex dashboards

---

## 🚀 Key Capabilities

### Cash-Flow Analysis
Clear visibility into where money goes and which expenses create risk. The system calculates:
- Total income vs expenses
- Expense ratio (% of income spent)
- Savings rate
- Emergency fund months of coverage

### Financial Exposure Scoring
An explainable, non-speculative risk score (A-F) based on:
- Income stability
- Fixed cost burden
- Emergency fund coverage
- Cash flow patterns

### Actionable Stability Plans
AI-generated steps that break financial goals into manageable actions:
- Build emergency fund milestones
- Identify expense reduction opportunities
- Understand spending patterns
- Educational resources and frameworks (50/30/20 rule, etc.)

### Plain-Language Explanations
Financial concepts explained without jargon or assumptions of prior knowledge. Uses "consider" instead of "you should" to maintain educational (not prescriptive) guidance.

---

## 🏗️ Tech Stack

**Backend:**
- FastAPI (Python)
- Claude Sonnet 4 (Anthropic AI)
- Pandas (data processing)
- Opik (LLM observability)

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Responsive design with modern indigo theme

**Key Technologies:**
```
fastapi - Web framework
anthropic - Claude AI integration
pandas - Transaction data processing
opik - LLM call tracking and monitoring
```

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.9+
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Opik API key ([Get one here](https://www.comet.com/opik)) - Optional for observability

### Quick Start

```bash
# Clone repository
git clone https://github.com/Str8Rogue16/resilience-finance-ai.git
cd resilience-finance-ai

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add:
# ANTHROPIC_API_KEY=your_key_here
# OPIK_API_KEY=your_key_here (optional)

# Run server
python main.py
```

Server starts at `http://localhost:8000`

### Frontend

Open `frontend/index.html` in your browser, or:

```bash
cd frontend
python -m http.server 8080
```

Visit `http://localhost:8080`

---

## 📊 Demo & Usage

### Sample Data

Five realistic financial scenarios included for testing:

1. **thriving_finances.csv** - Grade A: $8k income, 20% savings, excellent health
2. **struggling_finances.csv** - Grade D: 50% to rent, no emergency fund, high risk
3. **recovering_finances.csv** - Grade C: Improving trend, building savings
4. **volatile_finances.csv** - Grade C: Freelance income, inconsistent cash flow
5. **myfinances.csv** - Grade F: Negative Cashflow, expense ratio of 101%

Generate samples:
```bash
cd backend
python generate_enhanced_samples.py
```

### CSV Format

Your CSV should include:
- **Date** (e.g., "Date", "Transaction Date", "Posted Date")
- **Amount** (single column OR separate "Debit"/"Credit")
- **Description** (optional but helpful)

Example:
```csv
Date,Description,Amount
2026-01-15,Salary,3000
2026-01-16,Rent,-1200
2026-01-17,Groceries,-150
```

**Privacy Note:** Remove personal information (names, account numbers) before upload.

---

## 🎓 How It Works

### Financial Health Scoring

**Grade A:** <50% expenses, >20% savings, 6+ months emergency fund  
**Grade B:** 50-70% expenses, 10-20% savings, 3-6 months fund  
**Grade C:** 70-85% expenses, <10% savings, 1-3 months fund  
**Grade D:** 85-100% expenses, minimal savings, <1 month fund  
**Grade F:** >100% expenses, negative cash flow, financial crisis

### AI Analysis Pipeline

1. **Upload** → Parse CSV, auto-detect format
2. **Calculate** → Compute ratios, savings rate, emergency coverage
3. **Score** → Assign A-F grade
4. **AI Enhance** → Claude analyzes and generates personalized insights
5. **Display** → Show results with educational context

### Observability with Opik

Every AI call is tracked:
- Input prompts and financial data
- Claude's responses
- Token usage and latency
- Success/failure status

View dashboard: https://www.comet.com/opik

---

## ⚠️ Known Limitations

### 1. Historical Averaging
**Issue:** Averages all months equally. A pay raise in recent months won't be detected if analyzing 12+ months.

**Workaround:** Upload only 3-6 months of **recent** data.

**Future Fix:** Month-over-month trend detection.

### 2. Context Blindness
**Issue:** Cannot know about:
- Utilities bundled in rent
- One-time expenses (moving, medical)
- Debt payoff transactions
- Life circumstances

**Workaround:** Disclaimer added; users interpret with context.

**Future Fix:** Optional context field for user notes.

### 3. Limited Categorization
**Issue:** Without category columns, cannot break down spending types.

**Future Fix:** ML-based merchant categorization.

---

## 🎯 Design Principles

✅ **Financial health over financial hype** - Emergency funds, not crypto speculation  
✅ **Explainable AI, not black-box predictions** - Clear scoring criteria  
✅ **Responsible guidance aligned with real-world constraints** - Educational, not prescriptive  
✅ **Minimal user input, maximum clarity** - Upload CSV, get instant insights  

---

## 🏆 Hackathon Alignment

### Functionality ✅
- Fully working upload, analysis, display
- Handles multiple CSV formats
- Fallback if AI fails

### Real-World Relevance ✅
- Solves financial literacy gap
- Tested with real personal data
- Practical daily application

### LLM/Agent Usage ✅
- Claude Sonnet 4 for analysis
- Structured reasoning chain
- Context-aware recommendations

### Evaluation & Observability ✅
- Opik tracks all AI calls
- Quality metrics logged
- Production-ready monitoring

### Goal Alignment ✅
- Builds emergency funds
- Educational, not speculative
- Responsible spending guidance

---

## 📈 Future Enhancements

**Short Term:**
- Multi-file upload (checking + savings + credit combined)
- Monthly trend detection
- PDF export of analysis

**Medium Term:**
- Transaction categorization with ML
- Spending breakdown visualizations
- Goal tracking (emergency fund progress)

**Long Term:**
- Budget recommendations
- Financial literacy modules
- Multi-user authentication

---

## 🔐 Privacy & Security

- **No Data Storage** - Transactions processed in-memory only
- **User Responsibility** - Remove personal info before upload
- **API Keys** - Environment variables, never committed
- **Educational Only** - Not financial advice

---

## 📄 License

This project is licensed under the Apache License, Version 2.0. See the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built for **Encode.io Hackathon - Financial Health Track**
- Powered by **Anthropic Claude AI**
- Observability by **Comet Opik**
- Financial principles from **CFPB** guidelines

---

## 👤 About

**Solo developer submission**  
Built as a learning project exploring:
- FastAPI and AI integration
- LLM observability best practices
- Real-world financial data analysis
- Production-ready fallback patterns

---

## Disclaimer

Resilience Finance AI is provided for educational and informational purposes only. It does not constitute financial, investment, tax, or legal advice. For personalized guidance, consult a qualified financial professional.

---

*"Understanding your financial health is the first step toward financial resilience."*
