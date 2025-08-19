"""
Test A2A integration between LoanMortgage and PropValue agents
"""

import sys
import os
sys.path.append('/home/sagemaker-user/langgraph/LangMortgage')
sys.path.append('/home/sagemaker-user/langgraph/PropValue')

from a2a_property_client import MortgagePropertyValuationClient
import json

def test_a2a_integration_mock():
    """Test A2A integration using mock PropValue responses"""
    
    print("🧪 TESTING A2A INTEGRATION (Mock Mode)")
    print("=" * 60)
    
    # Initialize client in mock mode
    client = MortgagePropertyValuationClient(use_mock=True)
    
    # Test property data that would come from mortgage application
    test_properties = [
        {
            "name": "High Value Property",
            "data": {
                "property_address": "123 Luxury Lane, Beverly Hills, CA 90210",
                "property_type": "single_family",
                "square_footage": 3500,
                "bedrooms": 5,
                "bathrooms": 4.5,
                "year_built": 2015,
                "lot_size": 0.75,
                "loan_amount": 800000
            }
        },
        {
            "name": "Standard Property",
            "data": {
                "property_address": "456 Main St, Anytown, TX 75001",
                "property_type": "single_family", 
                "square_footage": 2200,
                "bedrooms": 4,
                "bathrooms": 2.5,
                "year_built": 2010,
                "lot_size": 0.25,
                "loan_amount": 350000
            }
        },
        {
            "name": "Condo Property",
            "data": {
                "property_address": "789 Urban Ave #15, Seattle, WA 98101",
                "property_type": "condo",
                "square_footage": 1200,
                "bedrooms": 2,
                "bathrooms": 2,
                "year_built": 2020,
                "lot_size": 0,
                "loan_amount": 220000
            }
        }
    ]
    
    for i, test_case in enumerate(test_properties, 1):
        print(f"\n{i}. Testing {test_case['name']}")
        print("-" * 40)
        
        try:
            # Request property valuation
            response = client.request_property_valuation(test_case['data'])
            
            print(f"Property: {test_case['data']['property_address']}")
            print(f"Type: {test_case['data']['property_type']}")
            print(f"Size: {test_case['data']['square_footage']} sq ft")
            print(f"Loan Amount: ${test_case['data']['loan_amount']:,.0f}")
            print()
            
            if response['status'] == 'SUCCESS':
                valuation = response['valuation_data']['property_valuation']
                print(f"✅ Valuation Status: {response['status']}")
                print(f"Estimated Value: ${valuation['estimated_value']:,.0f}")
                print(f"Confidence: {valuation['confidence_level']} ({valuation['confidence_score']}%)")
                print(f"Value Range: ${valuation['valuation_range']['min_value']:,.0f} - ${valuation['valuation_range']['max_value']:,.0f}")
                
                # Calculate LTV analysis
                ltv_info = client.extract_loan_to_value_info(response, test_case['data']['loan_amount'])
                
                if ltv_info['ltv_available']:
                    print(f"\nLTV Analysis:")
                    print(f"  LTV Ratio: {ltv_info['ltv_percentage']:.1f}%")
                    print(f"  Risk Level: {ltv_info['ltv_risk_assessment']['risk_level']}")
                    print(f"  Requires PMI: {ltv_info['ltv_risk_assessment']['requires_pmi']}")
                    print(f"  Recommendation: {ltv_info['ltv_risk_assessment']['recommended_action']}")
                else:
                    print(f"❌ LTV calculation failed: {ltv_info['error']}")
                    
            else:
                print(f"❌ Valuation failed: {response.get('error_message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test error: {e}")

def test_a2a_integration_real():
    """Test A2A integration with real PropValue agent (if available)"""
    
    print("\n🌐 TESTING A2A INTEGRATION (Real Agent Mode)")
    print("=" * 60)
    
    # Initialize client for real A2A communication
    client = MortgagePropertyValuationClient(use_mock=False)
    
    # Simple test property
    test_property = {
        "property_address": "123 Test Street, Sample City, TX 75001",
        "property_type": "single_family",
        "square_footage": 2000,
        "bedrooms": 3,
        "bathrooms": 2,
        "year_built": 2015,
        "lot_size": 0.20,
        "loan_amount": 400000,
        "application_id": "TEST_001"
    }
    
    print(f"Testing real A2A communication...")
    print(f"Property: {test_property['property_address']}")
    print(f"Loan Amount: ${test_property['loan_amount']:,.0f}")
    
    try:
        response = client.request_property_valuation(test_property)
        
        if response['status'] == 'SUCCESS':
            print(f"✅ Real A2A communication successful!")
            valuation = response['valuation_data']['property_valuation']
            print(f"Estimated Value: ${valuation['estimated_value']:,.0f}")
            print(f"Confidence: {valuation['confidence_level']}")
            
            # LTV analysis
            ltv_info = client.extract_loan_to_value_info(response, test_property['loan_amount'])
            print(f"LTV Ratio: {ltv_info['ltv_percentage']:.1f}%")
            print(f"Risk Assessment: {ltv_info['ltv_risk_assessment']['risk_level']}")
            
        else:
            print(f"⚠️  Real A2A failed: {response.get('error_message')}")
            print(f"   This is expected if PropValue agent is not deployed")
            
    except Exception as e:
        print(f"⚠️  Real A2A error: {e}")
        print(f"   This is expected if PropValue agent is not deployed")

def test_mortgage_workflow_with_property_valuation():
    """Test complete mortgage workflow including property valuation"""
    
    print("\n🏠 TESTING COMPLETE MORTGAGE WORKFLOW WITH PROPERTY VALUATION")
    print("=" * 70)
    
    # This would integrate with the main mortgage workflow
    # For now, we'll simulate the property valuation step
    
    mortgage_application = {
        "applicant_name": "John Doe",
        "credit_score": 720,
        "annual_income": 85000.0,
        "employment_years": 3.5,
        "loan_amount": 320000.0,
        "property_value": None,  # This should be populated by PropValue agent
        "down_payment": 80000.0,
        "debt_to_income_ratio": 0.35,
        
        # Property details for valuation
        "property_address": "456 Elm Street, Austin, TX 78701",
        "property_type": "single_family",
        "square_footage": 1800,
        "bedrooms": 3,
        "bathrooms": 2,
        "year_built": 2012,
        "lot_size": 0.18
    }
    
    print(f"Mortgage Application for: {mortgage_application['applicant_name']}")
    print(f"Property: {mortgage_application['property_address']}")
    print(f"Requested Loan: ${mortgage_application['loan_amount']:,.0f}")
    
    # Step 1: Get property valuation via A2A
    print(f"\n1. Requesting property valuation from PropValue agent...")
    
    client = MortgagePropertyValuationClient(use_mock=True)  # Use mock for reliable testing
    
    property_info = {
        "property_address": mortgage_application["property_address"],
        "property_type": mortgage_application["property_type"],
        "square_footage": mortgage_application["square_footage"],
        "bedrooms": mortgage_application["bedrooms"],
        "bathrooms": mortgage_application["bathrooms"],
        "year_built": mortgage_application["year_built"],
        "lot_size": mortgage_application["lot_size"],
        "loan_amount": mortgage_application["loan_amount"]
    }
    
    valuation_response = client.request_property_valuation(property_info)
    
    if valuation_response['status'] == 'SUCCESS':
        valuation = valuation_response['valuation_data']['property_valuation']
        mortgage_application['property_value'] = valuation['estimated_value']
        
        print(f"✅ Property valuation received:")
        print(f"   Estimated Value: ${valuation['estimated_value']:,.0f}")
        print(f"   Confidence: {valuation['confidence_level']}")
        
        # Step 2: Calculate LTV for mortgage decision
        ltv_info = client.extract_loan_to_value_info(valuation_response, mortgage_application['loan_amount'])
        
        print(f"\n2. LTV Analysis:")
        print(f"   LTV Ratio: {ltv_info['ltv_percentage']:.1f}%")
        print(f"   Risk Level: {ltv_info['ltv_risk_assessment']['risk_level']}")
        print(f"   Recommendation: {ltv_info['ltv_risk_assessment']['recommended_action']}")
        
        # Step 3: Update mortgage application with valuation data
        mortgage_application['ltv_ratio'] = ltv_info['ltv_ratio']
        mortgage_application['property_confidence'] = valuation['confidence_level']
        
        print(f"\n3. Updated Mortgage Application:")
        print(f"   Property Value: ${mortgage_application['property_value']:,.0f}")
        print(f"   LTV Ratio: {mortgage_application['ltv_ratio']:.1%}")
        print(f"   Down Payment: ${mortgage_application['down_payment']:,.0f}")
        
        # Step 4: Simulate mortgage decision based on enhanced data
        print(f"\n4. Mortgage Decision Factors:")
        print(f"   Credit Score: {mortgage_application['credit_score']} (Good: ≥700)")
        print(f"   LTV Ratio: {mortgage_application['ltv_ratio']:.1%} (Good: ≤80%)")
        print(f"   DTI Ratio: {mortgage_application['debt_to_income_ratio']:.1%} (Good: ≤36%)")
        print(f"   Property Confidence: {mortgage_application['property_confidence']}")
        
        # Simple decision logic
        decision_factors = []
        if mortgage_application['credit_score'] >= 700:
            decision_factors.append("✅ Good credit score")
        else:
            decision_factors.append("⚠️ Credit score below 700")
            
        if mortgage_application['ltv_ratio'] <= 0.80:
            decision_factors.append("✅ LTV ratio acceptable")
        else:
            decision_factors.append("⚠️ High LTV ratio")
            
        if mortgage_application['debt_to_income_ratio'] <= 0.36:
            decision_factors.append("✅ DTI ratio acceptable")
        else:
            decision_factors.append("⚠️ High DTI ratio")
            
        if valuation['confidence_level'] in ['HIGH', 'MEDIUM']:
            decision_factors.append("✅ Property valuation confident")
        else:
            decision_factors.append("⚠️ Low property valuation confidence")
        
        print(f"\n   Decision Factors:")
        for factor in decision_factors:
            print(f"     {factor}")
        
        # Final recommendation
        warning_count = sum(1 for factor in decision_factors if "⚠️" in factor)
        
        if warning_count == 0:
            final_decision = "APPROVED"
        elif warning_count <= 1:
            final_decision = "APPROVED_WITH_CONDITIONS"
        else:
            final_decision = "REQUIRES_MANUAL_REVIEW"
            
        print(f"\n🎯 FINAL RECOMMENDATION: {final_decision}")
        
    else:
        print(f"❌ Property valuation failed: {valuation_response.get('error_message')}")
        print(f"   Mortgage application cannot proceed without property valuation")

if __name__ == "__main__":
    # Run all tests
    test_a2a_integration_mock()
    test_a2a_integration_real()
    test_mortgage_workflow_with_property_valuation()
    
    print(f"\n" + "=" * 70)
    print(f"🏁 A2A INTEGRATION TESTING COMPLETE")
    print(f"=" * 70)
    print(f"✅ Mock A2A: Tests communication flow and data formats")
    print(f"🌐 Real A2A: Tests actual agent communication (if deployed)")
    print(f"🏠 Workflow: Tests complete mortgage process with property valuation")