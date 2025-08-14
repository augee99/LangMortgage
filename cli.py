#!/usr/bin/env python3
"""
Command-line interface for mortgage validation agent
"""

import argparse
import json
from main import run_mortgage_validation

def main():
    parser = argparse.ArgumentParser(description='Mortgage Loan Validation Agent')
    
    # Add command line arguments
    parser.add_argument('--name', required=True, help='Applicant name')
    parser.add_argument('--credit-score', type=int, required=True, help='Credit score (300-850)')
    parser.add_argument('--income', type=float, required=True, help='Annual income in dollars')
    parser.add_argument('--employment-years', type=float, required=True, help='Years of employment')
    parser.add_argument('--loan-amount', type=float, required=True, help='Loan amount in dollars')
    parser.add_argument('--property-value', type=float, required=True, help='Property value in dollars')
    parser.add_argument('--down-payment', type=float, required=True, help='Down payment in dollars')
    parser.add_argument('--debt-ratio', type=float, required=True, help='Debt-to-income ratio (e.g., 0.35 for 35%)')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    # Create application data
    application = {
        'applicant_name': args.name,
        'credit_score': args.credit_score,
        'annual_income': args.income,
        'employment_years': args.employment_years,
        'loan_amount': args.loan_amount,
        'property_value': args.property_value,
        'down_payment': args.down_payment,
        'debt_to_income_ratio': args.debt_ratio
    }
    
    try:
        result = run_mortgage_validation(application)
        
        if args.json:
            # Output JSON format
            output = {
                'applicant': application,
                'decision': result['final_decision'],
                'reason': result['decision_reason'],
                'confidence': result['confidence_score'],
                'validation_results': {
                    'data_validation': result['data_validation_result']['status'],
                    'credit_grade': result['credit_assessment_result']['credit_grade'],
                    'credit_risk': result['credit_assessment_result']['risk_level'],
                    'income_adequacy': result['income_verification_result']['income_adequacy'],
                    'overall_risk': result['risk_analysis_result']['overall_risk'],
                    'requires_pmi': result['risk_analysis_result'].get('requires_pmi', False)
                }
            }
            print(json.dumps(output, indent=2))
        else:
            # Human-readable format
            print(f"DECISION: {result['final_decision']}")
            print(f"Confidence: {result['confidence_score']:.1f}%")
            print(f"Reason: {result['decision_reason']}")
            
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()