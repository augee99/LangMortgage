# LangMortgage - Mortgage Validation Agent

A LangGraph-based agent for validating and approving/rejecting mortgage loan applications using Google's Gemini 2.5 Flash model.

## Features

- **5-Node Validation Workflow**:
  1. **Data Validation** - Validates input application data
  2. **Credit Assessment** - Evaluates credit score and history  
  3. **Income Verification** - Verifies income and employment
  4. **Risk Analysis** - Analyzes loan-to-value ratio and overall risk
  5. **Final Decision** - Makes approve/reject/pending decision

- **Google LLM Integration** - Uses Gemini 2.5 Flash for intelligent analysis
- **Flexible Routing** - Sequential or conditional workflow options
- **Comprehensive Testing** - Multiple test scenarios included

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Google API key
```

3. Set your Google API key in `.env`:
```
GOOGLE_API_KEY=your_actual_google_api_key_here
```

## Usage

### Basic Usage

```python
from main import run_mortgage_validation

# Sample application data
application = {
    "applicant_name": "John Doe",
    "credit_score": 720,
    "annual_income": 85000.0,
    "employment_years": 3.5,
    "loan_amount": 320000.0,
    "property_value": 400000.0,
    "down_payment": 80000.0,
    "debt_to_income_ratio": 0.35
}

# Run validation
result = run_mortgage_validation(application)
print(f"Decision: {result['final_decision']}")
print(f"Reason: {result['decision_reason']}")
```

### Run Example

```bash
python main.py
```

### Run Tests

```bash
python test_agent.py
```

## Workflow Details

### Node 1: Data Validation
- Validates required fields are present
- Checks credit score range (300-850)
- Verifies positive income and loan amounts
- Ensures down payment doesn't exceed property value

### Node 2: Credit Assessment  
- Grades credit score (A/B/C/D/F)
- Evaluates employment stability
- Determines risk level based on credit history

### Node 3: Income Verification
- Calculates payment-to-income ratio
- Validates income adequacy (≤28% recommended)
- Checks employment history (≥2 years preferred)

### Node 4: Risk Analysis
- Calculates loan-to-value ratio
- Identifies risk factors
- Determines if PMI is required (LTV >80%)

### Node 5: Final Decision
- Makes final approval decision
- Provides confidence score
- Gives detailed reasoning

## Decision Criteria

- **APPROVED**: Good credit (B+ grade), adequate income, low-medium risk
- **REJECTED**: Poor credit (D/F grade), inadequate income, high risk
- **PENDING_REVIEW**: Borderline cases requiring manual review

## File Structure

```
LangMortgage/
├── __init__.py          # Package initialization
├── state.py             # State definition
├── nodes.py             # Node implementations  
├── graph.py             # Workflow graph
├── main.py              # Main execution
├── test_agent.py        # Test scenarios
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
└── README.md           # This file
```

## Requirements

- Python 3.8+
- LangGraph 0.2.0+
- langchain-google-genai 1.0.0+
- Google API key for Gemini access