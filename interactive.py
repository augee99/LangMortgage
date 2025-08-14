"""
Interactive mortgage validation agent
"""

from main import run_mortgage_validation

def get_user_input():
    """Get mortgage application data from user input"""
    
    print("=" * 60)
    print("MORTGAGE LOAN VALIDATION - INTERACTIVE MODE")
    print("=" * 60)
    
    try:
        application = {}
        
        application['applicant_name'] = input("Applicant Name: ").strip()
        application['credit_score'] = int(input("Credit Score (300-850): "))
        application['annual_income'] = float(input("Annual Income ($): "))
        application['employment_years'] = float(input("Employment Years: "))
        application['loan_amount'] = float(input("Loan Amount ($): "))
        application['property_value'] = float(input("Property Value ($): "))
        application['down_payment'] = float(input("Down Payment ($): "))
        application['debt_to_income_ratio'] = float(input("Debt-to-Income Ratio (0.35 = 35%): "))
        
        return application
        
    except ValueError as e:
        print(f"Invalid input: {e}")
        return None

def main():
    """Interactive main function"""
    
    while True:
        application = get_user_input()
        
        if application is None:
            print("Invalid input. Please try again.")
            continue
            
        print("\n" + "=" * 60)
        print("PROCESSING APPLICATION...")
        print("=" * 60)
        
        try:
            result = run_mortgage_validation(application)
            
            print(f"\nAPPLICANT: {application['applicant_name']}")
            print("-" * 60)
            print(f"Credit Score: {application['credit_score']}")
            print(f"Annual Income: ${application['annual_income']:,.2f}")
            print(f"Loan Amount: ${application['loan_amount']:,.2f}")
            print(f"Property Value: ${application['property_value']:,.2f}")
            print(f"Down Payment: ${application['down_payment']:,.2f}")
            print(f"DTI Ratio: {application['debt_to_income_ratio']:.2%}")
            
            print("\nVALIDATION RESULTS:")
            print("-" * 60)
            print(f"1. Data Validation: {result['data_validation_result']['status']}")
            print(f"2. Credit Assessment: {result['credit_assessment_result']['credit_grade']} grade, {result['credit_assessment_result']['risk_level']} risk")
            print(f"3. Income Verification: {result['income_verification_result']['income_adequacy']}")
            print(f"4. Risk Analysis: {result['risk_analysis_result']['overall_risk']} risk")
            print(f"5. Final Decision: {result['final_decision']}")
            
            print(f"\nDECISION: {result['final_decision']}")
            print(f"Reason: {result['decision_reason']}")
            print(f"Confidence: {result['confidence_score']:.1f}%")
            
            if result['risk_analysis_result'].get('requires_pmi'):
                print("⚠️  PMI Required (LTV > 80%)")
                
        except Exception as e:
            print(f"Error processing application: {e}")
        
        # Ask if user wants to continue
        print("\n" + "=" * 60)
        continue_choice = input("Process another application? (y/n): ").lower().strip()
        if continue_choice not in ['y', 'yes']:
            break
    
    print("Thank you for using the Mortgage Validation Agent!")

if __name__ == "__main__":
    main()