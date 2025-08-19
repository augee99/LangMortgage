#!/usr/bin/env python3
"""
Test complete LangMortgage workflow with property valuation
"""

import os
import sys
sys.path.append('.')

from main import run_mortgage_validation

def test_complete_mortgage_workflow():
    """Test complete mortgage workflow with real property data"""
    
    # Complete application data with property information
    application_data = {
        "applicant_name": "John Doe",
        "credit_score": 720,
        "annual_income": 85000,
        "loan_amount": 320000,
        "property_value": 400000,
        "property_address": "123 Main St, Austin, TX 78701",
        "property_type": "single_family",
        "square_footage": 2200,
        "bedrooms": 4,
        "bathrooms": 2.5,
        "year_built": 2015,
        "lot_size": 0.25,
        "loan_purpose": "purchase",
        "down_payment": 80000
    }
    
    print("🏠 Testing Complete LangMortgage Workflow")
    print("=" * 60)
    print(f"Property: {application_data['property_address']}")
    print(f"Loan Amount: ${application_data['loan_amount']:,}")
    print(f"Property Type: {application_data['property_type']}")
    print(f"Square Footage: {application_data['square_footage']:,}")
    print("=" * 60)
    
    # Run the complete workflow
    try:
        result = run_mortgage_validation(application_data)
        
        print("\n✅ WORKFLOW COMPLETED")
        print("=" * 60)
        print(f"Final Decision: {result.get('final_decision', 'Unknown')}")
        print(f"Confidence: {result.get('confidence_score', 0)}%")
        print(f"Decision Reason: {result.get('decision_reason', 'N/A')}")
        
        # Check if property valuation worked
        if 'property_valuation' in result:
            valuation = result['property_valuation']
            print(f"\n🏡 PROPERTY VALUATION:")
            print(f"   Estimated Value: ${valuation.get('estimated_value', 0):,.2f}")
            print(f"   Confidence Level: {valuation.get('confidence_level', 'Unknown')}")
            print(f"   LTV Ratio: {valuation.get('ltv_ratio', 0):.2%}")
        else:
            print(f"\n⚠️  Property valuation issue: {result.get('errors', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ WORKFLOW FAILED: {str(e)}")
        return None

if __name__ == "__main__":
    test_complete_mortgage_workflow()