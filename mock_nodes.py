"""
Mock version of mortgage nodes that doesn't require LLM API calls
Used for testing and demonstration purposes
"""

from typing import Dict, Any

# Import with fallback for platform deployment
try:
    from .state import MortgageState
    from .a2a_property_client import MortgagePropertyValuationClient
except ImportError:
    from state import MortgageState
    from a2a_property_client import MortgagePropertyValuationClient

def mock_data_validation_node(state: MortgageState) -> MortgageState:
    """Mock Node 1: Validate input loan application data"""
    
    validation_result = {
        "status": "PASS",
        "issues": [],
        "warnings": []
    }
    
    # Basic validation logic
    if state['credit_score'] < 300 or state['credit_score'] > 850:
        validation_result["issues"].append("Invalid credit score")
        validation_result["status"] = "FAIL"
    if state['annual_income'] <= 0:
        validation_result["issues"].append("Invalid annual income")
        validation_result["status"] = "FAIL"
    if state['loan_amount'] <= 0:
        validation_result["issues"].append("Invalid loan amount")
        validation_result["status"] = "FAIL"
    if state['down_payment'] > state['property_value']:
        validation_result["issues"].append("Down payment exceeds property value")
        validation_result["status"] = "FAIL"
    if state['debt_to_income_ratio'] > 0.5:
        validation_result["warnings"].append("High debt-to-income ratio")
    
    state['data_validation_result'] = validation_result
    state['current_step'] = "data_validation_completed"
    
    return state

def mock_credit_assessment_node(state: MortgageState) -> MortgageState:
    """Mock Node 2: Evaluate credit score and creditworthiness"""
    
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

def mock_income_verification_node(state: MortgageState) -> MortgageState:
    """Mock Node 3: Verify income and employment details"""
    
    monthly_income = state['annual_income'] / 12
    monthly_payment = state['loan_amount'] * 0.005  # Rough estimate at 6% for 30 years
    income_ratio = monthly_payment / monthly_income
    
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

def mock_property_valuation_node(state: MortgageState) -> MortgageState:
    """Mock Node: Get property valuation via A2A communication with PropertyValuation agent"""
    
    # Extract property information from mortgage application
    property_info = {
        "property_address": state.get('property_address', 'Address not provided'),
        "property_type": state.get('property_type', 'single_family'),
        "square_footage": state.get('square_footage'),
        "bedrooms": state.get('bedrooms'),
        "bathrooms": state.get('bathrooms'),
        "year_built": state.get('year_built'),
        "lot_size": state.get('lot_size')
    }
    
    # Initialize A2A client and request valuation (will use mock data)
    prop_val_client = MortgagePropertyValuationClient()
    valuation_response = prop_val_client.request_property_valuation(property_info)
    
    if valuation_response['status'] == 'SUCCESS':
        # Extract LTV information
        ltv_analysis = prop_val_client.extract_loan_to_value_info(
            valuation_response, 
            state['loan_amount']
        )
        
        valuation_result = {
            "status": "SUCCESS",
            "appraised_value": valuation_response['valuation_data']['property_valuation']['estimated_value'],
            "confidence_level": valuation_response['valuation_data']['property_valuation']['confidence_level'],
            "confidence_score": valuation_response['valuation_data']['property_valuation']['confidence_score'],
            "valuation_range": valuation_response['valuation_data']['property_valuation']['valuation_range'],
            "ltv_analysis": ltv_analysis,
            "valuation_flags": valuation_response['valuation_data']['valuation_flags']
        }
        
        # Compare appraised value vs stated value
        appraised_value = valuation_result['appraised_value']
        stated_value = state['property_value']
        value_variance = abs(appraised_value - stated_value) / stated_value
        
        if value_variance > 0.10:  # More than 10% difference
            state['warnings'].append(f"Significant variance between stated (${stated_value:,.0f}) and appraised (${appraised_value:,.0f}) values")
        
        # Update property value with appraised value for downstream calculations
        state['property_value'] = appraised_value
        
    else:
        valuation_result = {
            "status": "ERROR",
            "error_message": valuation_response.get('error_message', 'Property valuation failed'),
            "appraised_value": state['property_value'],  # Fall back to stated value
            "confidence_level": "LOW",
            "ltv_analysis": {"ltv_available": False}
        }
        
        state['errors'].append(f"Property valuation failed: {valuation_result['error_message']}")
    
    state['property_valuation_result'] = valuation_result
    state['current_step'] = "property_valuation_completed"
    
    return state

def mock_risk_analysis_node(state: MortgageState) -> MortgageState:
    """Mock Node 4: Analyze loan-to-value ratio and overall risk"""
    
    loan_to_value = state['loan_amount'] / state['property_value']
    down_payment_percent = state['down_payment'] / state['property_value']
    
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

def mock_final_decision_node(state: MortgageState) -> MortgageState:
    """Mock Node 5: Make final approve/reject decision"""
    
    # Collect all assessment results
    data_valid = state['data_validation_result']['status'] == "PASS"
    credit_grade = state['credit_assessment_result']['credit_grade']
    income_adequate = state['income_verification_result']['income_adequacy'] == "SUFFICIENT"
    risk_level = state['risk_analysis_result']['overall_risk']
    
    # Check property valuation
    property_val_success = state.get('property_valuation_result', {}).get('status') == 'SUCCESS'
    
    # Decision logic
    if not data_valid:
        decision = "REJECTED"
        reason = "Failed data validation"
        confidence = 95
    elif not property_val_success and state.get('property_valuation_result', {}).get('status') == 'ERROR':
        decision = "REJECTED"
        reason = "Property valuation failed"
        confidence = 90
    elif credit_grade in ['A', 'B'] and income_adequate and risk_level in ['LOW', 'MEDIUM']:
        decision = "APPROVED"
        reason = f"Strong application: {credit_grade} credit grade, adequate income, {risk_level.lower()} risk"
        confidence = 85 if risk_level == 'LOW' else 75
        
        # Adjust confidence based on property valuation
        if property_val_success:
            prop_confidence = state['property_valuation_result']['confidence_level']
            if prop_confidence == 'HIGH':
                confidence += 5
            elif prop_confidence == 'LOW':
                confidence -= 10
                
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