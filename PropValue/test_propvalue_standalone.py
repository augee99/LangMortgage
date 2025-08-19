"""
Standalone test for PropValue agent A2A communication
Run this to test the PropValue agent independently
"""

import sys
import os
sys.path.append('/home/sagemaker-user/langgraph/PropValue')

from a2a_client import A2APropertyValuationClient, example_mortgage_to_property_valuation
import json

def test_propvalue_agent():
    """Test PropValue agent directly"""
    
    print("🏠 TESTING PROPVALUE AGENT STANDALONE")
    print("=" * 50)
    
    # Test cases for different property types
    test_properties = [
        {
            "name": "Single Family Home",
            "property_address": "123 Main St, Austin, TX 78701",
            "property_type": "single_family",
            "square_footage": 2200,
            "bedrooms": 4,
            "bathrooms": 2.5,
            "year_built": 2015,
            "lot_size": 0.25
        },
        {
            "name": "Luxury Property",
            "property_address": "456 Oak Ave, Beverly Hills, CA 90210", 
            "property_type": "single_family",
            "square_footage": 4500,
            "bedrooms": 6,
            "bathrooms": 5.5,
            "year_built": 2020,
            "lot_size": 1.0
        },
        {
            "name": "Urban Condo",
            "property_address": "789 City Center #25, Seattle, WA 98101",
            "property_type": "condo",
            "square_footage": 1200,
            "bedrooms": 2,
            "bathrooms": 2,
            "year_built": 2018,
            "lot_size": 0
        }
    ]
    
    # Initialize PropValue client
    client = A2APropertyValuationClient(use_mock=True)  # Use mock for reliable testing
    
    for i, property_data in enumerate(test_properties, 1):
        print(f"\n{i}. Testing {property_data['name']}")
        print("-" * 30)
        
        try:
            # Send valuation request
            response = client.process_valuation_request(property_data, "MortgageApproval")
            
            print(f"Property: {property_data['property_address']}")
            print(f"Type: {property_data['property_type']}")
            print(f"Size: {property_data['square_footage']} sq ft")
            
            if response['status'] == 'SUCCESS':
                data = response['data']
                print(f"\n✅ Valuation Results:")
                print(f"  Estimated Value: ${data['estimated_value']:,.0f}")
                print(f"  Confidence: {data['confidence_level']} ({data.get('confidence_score', 'N/A')}%)")
                
                if 'valuation_range' in data:
                    val_range = data['valuation_range']
                    print(f"  Value Range: ${val_range.get('min_value', 0):,.0f} - ${val_range.get('max_value', 0):,.0f}")
                    
                print(f"  Appraisal Date: {data.get('valuation_date', 'N/A')}")
                print(f"  Notes: {data.get('appraiser_notes', 'N/A')}")
                
                # Format for mortgage agent
                formatted = client.format_response_for_mortgage_agent(data)
                print(f"\n📋 Formatted for Mortgage Agent:")
                print(f"  LTV Ready: {formatted['loan_to_value_calculation']['ltv_ready']}")
                print(f"  High Confidence: {formatted['valuation_flags']['high_confidence']}")
                print(f"  Market Stable: {formatted['valuation_flags']['market_stable']}")
                
            else:
                print(f"❌ Valuation failed: {response.get('error_message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test error: {e}")

def test_propvalue_example():
    """Run the built-in example function"""
    
    print(f"\n🧪 RUNNING BUILT-IN EXAMPLE")
    print("=" * 40)
    
    try:
        result = example_mortgage_to_property_valuation()
        
        if result:
            print(f"✅ Built-in example successful")
            print(f"Result keys: {list(result.keys())}")
        else:
            print(f"❌ Built-in example failed")
            
    except Exception as e:
        print(f"❌ Example error: {e}")

if __name__ == "__main__":
    test_propvalue_agent()
    test_propvalue_example()
    
    print(f"\n" + "=" * 50)
    print(f"🏁 PROPVALUE STANDALONE TESTING COMPLETE")
    print(f"=" * 50)