from typing import Dict, Any, List
from typing_extensions import TypedDict

class MortgageState(TypedDict):
    """State for mortgage loan validation workflow"""
    
    # Input application data
    applicant_name: str
    credit_score: int
    annual_income: float
    employment_years: float
    loan_amount: float
    property_value: float
    down_payment: float
    debt_to_income_ratio: float
    
    # Validation results from each node
    data_validation_result: Dict[str, Any]
    credit_assessment_result: Dict[str, Any]
    income_verification_result: Dict[str, Any]
    risk_analysis_result: Dict[str, Any]
    
    # Final decision
    final_decision: str  # "APPROVED", "REJECTED", "PENDING_REVIEW"
    decision_reason: str
    confidence_score: float
    
    # Processing status
    current_step: str
    errors: List[str]
    warnings: List[str]