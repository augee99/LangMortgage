"""
Custom test script - modify the application data below and run
"""

from main import run_mortgage_validation

def test_custom_application():
    """Test with custom application data"""
    
    # MODIFY THESE VALUES FOR YOUR TEST:
    custom_application = {
        "applicant_name": "Alice Smith",
        "credit_score": 300,                    # 300-850
        "annual_income": 90000.0,               # Annual income in dollars
        "employment_years": 4.0,                # Years of employment
        "loan_amount": 300000.0,                # Loan amount in dollars
        "property_value": 380000.0,             # Property value in dollars
        "down_payment": 80000.0,                # Down payment in dollars
        "debt_to_income_ratio": 0.32            # 0.32 = 32%
    }
    
    print("=" * 60)
    print("CUSTOM MORTGAGE VALIDATION TEST")
    print("=" * 60)
    print(f"Applicant: {custom_application['applicant_name']}")
    print(f"Credit Score: {custom_application['credit_score']}")
    print(f"Annual Income: ${custom_application['annual_income']:,.2f}")
    print(f"Loan Amount: ${custom_application['loan_amount']:,.2f}")
    print(f"Property Value: ${custom_application['property_value']:,.2f}")
    print(f"Down Payment: ${custom_application['down_payment']:,.2f}")
    print(f"DTI Ratio: {custom_application['debt_to_income_ratio']:.2%}")
    print("-" * 60)
    
    try:
        result = run_mortgage_validation(custom_application)
        
        print("\nVALIDATION RESULTS:")
        print("-" * 60)
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
            
        # Calculate some additional metrics
        ltv = result['risk_analysis_result']['loan_to_value_ratio']
        monthly_income = result['income_verification_result']['monthly_income']
        monthly_payment = result['income_verification_result']['estimated_monthly_payment']
        
        print(f"\nADDITIONAL METRICS:")
        print("-" * 60)
        print(f"Loan-to-Value Ratio: {ltv:.2%}")
        print(f"Monthly Income: ${monthly_income:,.2f}")
        print(f"Estimated Monthly Payment: ${monthly_payment:,.2f}")
        
    except Exception as e:
        print(f"Error processing application: {e}")

if __name__ == "__main__":
    test_custom_application()