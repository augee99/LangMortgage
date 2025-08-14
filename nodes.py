from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from state import MortgageState

# Initialize Google LLM - will be created in each function to avoid auth issues
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1
    )

def data_validation_node(state: MortgageState) -> MortgageState:
    """Node 1: Validate input loan application data"""
    
    prompt = f"""
    You are a mortgage loan data validator. Review the following loan application data and identify any issues:
    
    Applicant: {state['applicant_name']}
    Credit Score: {state['credit_score']}
    Annual Income: ${state['annual_income']:,.2f}
    Employment Years: {state['employment_years']}
    Loan Amount: ${state['loan_amount']:,.2f}
    Property Value: ${state['property_value']:,.2f}
    Down Payment: ${state['down_payment']:,.2f}
    Debt-to-Income Ratio: {state['debt_to_income_ratio']:.2%}
    
    Validate:
    1. All required fields are present and reasonable
    2. Credit score is within valid range (300-850)
    3. Income and loan amounts are positive
    4. Down payment doesn't exceed property value
    5. Debt-to-income ratio is reasonable
    
    Return your assessment as JSON with 'status' (PASS/FAIL), 'issues' (list), and 'warnings' (list).
    """
    
    llm = get_llm()
    response = llm.invoke(prompt)
    
    # Parse response and update state
    validation_result = {
        "status": "PASS" if state['credit_score'] >= 300 and state['annual_income'] > 0 else "FAIL",
        "issues": [],
        "warnings": []
    }
    
    # Basic validation logic
    if state['credit_score'] < 300 or state['credit_score'] > 850:
        validation_result["issues"].append("Invalid credit score")
    if state['annual_income'] <= 0:
        validation_result["issues"].append("Invalid annual income")
    if state['loan_amount'] <= 0:
        validation_result["issues"].append("Invalid loan amount")
    if state['down_payment'] > state['property_value']:
        validation_result["issues"].append("Down payment exceeds property value")
    if state['debt_to_income_ratio'] > 0.5:
        validation_result["warnings"].append("High debt-to-income ratio")
    
    state['data_validation_result'] = validation_result
    state['current_step'] = "data_validation_completed"
    
    return state

def credit_assessment_node(state: MortgageState) -> MortgageState:
    """Node 2: Evaluate credit score and creditworthiness"""
    
    prompt = f"""
    You are a mortgage credit assessment specialist. Evaluate the creditworthiness based on:
    
    Credit Score: {state['credit_score']}
    Employment Years: {state['employment_years']}
    
    Credit Score Guidelines:
    - 750+: Excellent (lowest risk)
    - 700-749: Good 
    - 650-699: Fair
    - 600-649: Poor
    - Below 600: Very Poor (high risk)
    
    Employment Stability:
    - 2+ years: Stable
    - 1-2 years: Moderate
    - <1 year: Unstable
    
    Provide assessment with 'credit_grade' (A/B/C/D/F), 'risk_level' (LOW/MEDIUM/HIGH), and 'recommendation'.
    """
    
    llm = get_llm()
    response = llm.invoke(prompt)
    
    # Determine credit assessment
    if state['credit_score'] >= 750:
        credit_grade = "A"
        risk_level = "LOW"
    elif state['credit_score'] >= 700:
        credit_grade = "B"
        risk_level = "LOW"
    elif state['credit_score'] >= 650:
        credit_grade = "C"
        risk_level = "MEDIUM"
    elif state['credit_score'] >= 600:
        credit_grade = "D"
        risk_level = "HIGH"
    else:
        credit_grade = "F"
        risk_level = "HIGH"
    
    assessment_result = {
        "credit_grade": credit_grade,
        "risk_level": risk_level,
        "credit_score": state['credit_score'],
        "employment_stability": "STABLE" if state['employment_years'] >= 2 else "MODERATE" if state['employment_years'] >= 1 else "UNSTABLE"
    }
    
    state['credit_assessment_result'] = assessment_result
    state['current_step'] = "credit_assessment_completed"
    
    return state

def income_verification_node(state: MortgageState) -> MortgageState:
    """Node 3: Verify income and employment details"""
    
    monthly_income = state['annual_income'] / 12
    monthly_payment = state['loan_amount'] * 0.005  # Rough estimate at 6% for 30 years
    income_ratio = monthly_payment / monthly_income
    
    prompt = f"""
    You are an income verification specialist. Analyze the income details:
    
    Annual Income: ${state['annual_income']:,.2f}
    Monthly Income: ${monthly_income:,.2f}
    Employment Years: {state['employment_years']}
    Estimated Monthly Payment: ${monthly_payment:,.2f}
    Payment-to-Income Ratio: {income_ratio:.2%}
    
    Standard guidelines:
    - Payment-to-income ratio should be ≤ 28%
    - Employment should be ≥ 2 years for stability
    
    Provide 'income_adequacy' (SUFFICIENT/INSUFFICIENT), 'employment_stability' (STABLE/UNSTABLE), and 'concerns'.
    """
    
    llm = get_llm()
    response = llm.invoke(prompt)
    
    verification_result = {
        "monthly_income": monthly_income,
        "estimated_monthly_payment": monthly_payment,
        "payment_to_income_ratio": income_ratio,
        "income_adequacy": "SUFFICIENT" if income_ratio <= 0.28 else "INSUFFICIENT",
        "employment_stability": "STABLE" if state['employment_years'] >= 2 else "UNSTABLE",
        "concerns": []
    }
    
    if income_ratio > 0.28:
        verification_result["concerns"].append("Payment-to-income ratio exceeds 28%")
    if state['employment_years'] < 2:
        verification_result["concerns"].append("Employment history less than 2 years")
    
    state['income_verification_result'] = verification_result
    state['current_step'] = "income_verification_completed"
    
    return state

def risk_analysis_node(state: MortgageState) -> MortgageState:
    """Node 4: Analyze loan-to-value ratio and overall risk"""
    
    loan_to_value = state['loan_amount'] / state['property_value']
    down_payment_percent = state['down_payment'] / state['property_value']
    
    prompt = f"""
    You are a mortgage risk analyst. Evaluate the overall risk profile:
    
    Loan-to-Value Ratio: {loan_to_value:.2%}
    Down Payment: {down_payment_percent:.2%}
    Credit Score: {state['credit_score']}
    Debt-to-Income Ratio: {state['debt_to_income_ratio']:.2%}
    
    Risk Guidelines:
    - LTV > 80%: Higher risk (may require PMI)
    - DTI > 43%: Higher risk
    - Credit Score < 620: Higher risk
    
    Provide 'overall_risk' (LOW/MEDIUM/HIGH), 'risk_factors', and 'mitigation_suggestions'.
    """
    
    llm = get_llm()
    response = llm.invoke(prompt)
    
    risk_factors = []
    if loan_to_value > 0.8:
        risk_factors.append("High loan-to-value ratio (>80%)")
    if state['debt_to_income_ratio'] > 0.43:
        risk_factors.append("High debt-to-income ratio (>43%)")
    if state['credit_score'] < 620:
        risk_factors.append("Low credit score (<620)")
    
    # Determine overall risk
    if len(risk_factors) == 0:
        overall_risk = "LOW"
    elif len(risk_factors) <= 1:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "HIGH"
    
    risk_result = {
        "loan_to_value_ratio": loan_to_value,
        "down_payment_percent": down_payment_percent,
        "overall_risk": overall_risk,
        "risk_factors": risk_factors,
        "requires_pmi": loan_to_value > 0.8
    }
    
    state['risk_analysis_result'] = risk_result
    state['current_step'] = "risk_analysis_completed"
    
    return state

def final_decision_node(state: MortgageState) -> MortgageState:
    """Node 5: Make final approve/reject decision"""
    
    # Collect all assessment results
    data_valid = state['data_validation_result']['status'] == "PASS"
    credit_grade = state['credit_assessment_result']['credit_grade']
    income_adequate = state['income_verification_result']['income_adequacy'] == "SUFFICIENT"
    risk_level = state['risk_analysis_result']['overall_risk']
    
    prompt = f"""
    You are the final decision maker for mortgage loan approval. Based on all assessments:
    
    Data Validation: {state['data_validation_result']['status']}
    Credit Grade: {credit_grade}
    Income Adequacy: {state['income_verification_result']['income_adequacy']}
    Overall Risk: {risk_level}
    
    Previous Assessments:
    - Credit Score: {state['credit_score']}
    - Payment-to-Income: {state['income_verification_result']['payment_to_income_ratio']:.2%}
    - Loan-to-Value: {state['risk_analysis_result']['loan_to_value_ratio']:.2%}
    
    Decision Criteria:
    - APPROVED: All validations pass, good credit (B+ grade), adequate income, low-medium risk
    - REJECTED: Failed validations, poor credit (D/F grade), inadequate income, high risk
    - PENDING_REVIEW: Borderline cases requiring manual review
    
    Provide final decision (APPROVED/REJECTED/PENDING_REVIEW) with confidence score (0-100) and detailed reason.
    """
    
    llm = get_llm()
    response = llm.invoke(prompt)
    
    # Decision logic
    if not data_valid:
        decision = "REJECTED"
        reason = "Failed data validation"
        confidence = 95
    elif credit_grade in ['A', 'B'] and income_adequate and risk_level in ['LOW', 'MEDIUM']:
        decision = "APPROVED"
        reason = f"Strong application: {credit_grade} credit grade, adequate income, {risk_level.lower()} risk"
        confidence = 85 if risk_level == 'LOW' else 75
    elif credit_grade in ['D', 'F'] or not income_adequate or risk_level == 'HIGH':
        decision = "REJECTED"
        reason = f"High risk factors: {credit_grade} credit grade, income adequacy: {income_adequate}, {risk_level.lower()} risk"
        confidence = 80
    else:
        decision = "PENDING_REVIEW"
        reason = f"Borderline case requiring manual review: {credit_grade} credit, {risk_level.lower()} risk"
        confidence = 60
    
    state['final_decision'] = decision
    state['decision_reason'] = reason
    state['confidence_score'] = confidence
    state['current_step'] = "final_decision_completed"
    
    return state