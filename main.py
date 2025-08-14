"""
Main execution file for the LangMortgage agent
"""

import os
from dotenv import load_dotenv
from graph import create_mortgage_workflow
from state import MortgageState

# Load environment variables
load_dotenv()

def run_mortgage_validation(application_data: dict) -> dict:
    """
    Run mortgage validation workflow on application data
    
    Args:
        application_data: Dictionary containing loan application details
        
    Returns:
        Dictionary with validation results and decision
    """
    
    # Create the workflow
    workflow = create_mortgage_workflow()
    
    # Initialize state with application data
    initial_state = MortgageState(
        applicant_name=application_data.get("applicant_name", ""),
        credit_score=application_data.get("credit_score", 0),
        annual_income=application_data.get("annual_income", 0.0),
        employment_years=application_data.get("employment_years", 0.0),
        loan_amount=application_data.get("loan_amount", 0.0),
        property_value=application_data.get("property_value", 0.0),
        down_payment=application_data.get("down_payment", 0.0),
        debt_to_income_ratio=application_data.get("debt_to_income_ratio", 0.0),
        
        # Initialize empty results
        data_validation_result={},
        credit_assessment_result={},
        income_verification_result={},
        risk_analysis_result={},
        
        # Initialize decision fields
        final_decision="",
        decision_reason="",
        confidence_score=0.0,
        
        # Initialize status fields
        current_step="initializing",
        errors=[],
        warnings=[]
    )
    
    # Execute the workflow
    result = workflow.invoke(initial_state)
    
    return result

def main():
    """Example usage of the mortgage validation agent"""
    
    # Sample loan application
    sample_application = {
        "applicant_name": "John Doe",
        "credit_score": 720,
        "annual_income": 85000.0,
        "employment_years": 3.5,
        "loan_amount": 320000.0,
        "property_value": 400000.0,
        "down_payment": 80000.0,
        "debt_to_income_ratio": 0.35
    }
    
    print("=" * 60)
    print("MORTGAGE LOAN VALIDATION AGENT")
    print("=" * 60)
    print(f"Applicant: {sample_application['applicant_name']}")
    print(f"Credit Score: {sample_application['credit_score']}")
    print(f"Annual Income: ${sample_application['annual_income']:,.2f}")
    print(f"Loan Amount: ${sample_application['loan_amount']:,.2f}")
    print(f"Property Value: ${sample_application['property_value']:,.2f}")
    print("-" * 60)
    
    try:
        # Run the validation
        result = run_mortgage_validation(sample_application)
        
        print("\nVALIDATION RESULTS:")
        print("-" * 60)
        
        # Display results from each node
        print(f"1. Data Validation: {result['data_validation_result']['status']}")
        print(f"2. Credit Assessment: {result['credit_assessment_result']['credit_grade']} grade, {result['credit_assessment_result']['risk_level']} risk")
        print(f"3. Income Verification: {result['income_verification_result']['income_adequacy']}")
        print(f"4. Risk Analysis: {result['risk_analysis_result']['overall_risk']} risk")
        print(f"5. Final Decision: {result['final_decision']}")
        
        print("\nDETAILS:")
        print("-" * 60)
        print(f"Decision Reason: {result['decision_reason']}")
        print(f"Confidence Score: {result['confidence_score']:.1f}%")
        
        if result['risk_analysis_result'].get('requires_pmi'):
            print("⚠️  PMI Required (LTV > 80%)")
            
        if result.get('warnings'):
            print(f"\nWarnings: {', '.join(result['warnings'])}")
            
        if result.get('errors'):
            print(f"\nErrors: {', '.join(result['errors'])}")
    
    except Exception as e:
        print(f"Error running mortgage validation: {e}")

if __name__ == "__main__":
    main()