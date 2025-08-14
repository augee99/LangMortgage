"""
Test script for the mortgage validation agent
"""

from main import run_mortgage_validation

def test_mortgage_scenarios():
    """Test various mortgage application scenarios"""
    
    scenarios = [
        {
            "name": "Strong Application",
            "data": {
                "applicant_name": "Alice Johnson",
                "credit_score": 780,
                "annual_income": 95000.0,
                "employment_years": 5.0,
                "loan_amount": 300000.0,
                "property_value": 400000.0,
                "down_payment": 100000.0,
                "debt_to_income_ratio": 0.25
            },
            "expected": "APPROVED"
        },
        {
            "name": "Weak Application",
            "data": {
                "applicant_name": "Bob Smith",
                "credit_score": 580,
                "annual_income": 45000.0,
                "employment_years": 0.5,
                "loan_amount": 250000.0,
                "property_value": 280000.0,
                "down_payment": 30000.0,
                "debt_to_income_ratio": 0.45
            },
            "expected": "REJECTED"
        },
        {
            "name": "Borderline Application",
            "data": {
                "applicant_name": "Carol Davis",
                "credit_score": 660,
                "annual_income": 65000.0,
                "employment_years": 1.8,
                "loan_amount": 280000.0,
                "property_value": 320000.0,
                "down_payment": 40000.0,
                "debt_to_income_ratio": 0.38
            },
            "expected": "PENDING_REVIEW"
        }
    ]
    
    print("MORTGAGE VALIDATION AGENT - TEST SCENARIOS")
    print("=" * 80)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print("-" * 40)
        
        try:
            result = run_mortgage_validation(scenario['data'])
            
            print(f"Applicant: {scenario['data']['applicant_name']}")
            print(f"Credit Score: {scenario['data']['credit_score']}")
            print(f"Annual Income: ${scenario['data']['annual_income']:,.2f}")
            print(f"Loan Amount: ${scenario['data']['loan_amount']:,.2f}")
            print()
            print(f"Decision: {result['final_decision']}")
            print(f"Reason: {result['decision_reason']}")
            print(f"Confidence: {result['confidence_score']:.1f}%")
            
            # Check if result matches expectation
            if result['final_decision'] == scenario['expected']:
                print("✅ Result matches expectation")
            else:
                print(f"❌ Expected {scenario['expected']}, got {result['final_decision']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mortgage_scenarios()