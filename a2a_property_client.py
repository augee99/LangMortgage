"""
A2A Client for integrating with Property Valuation Agent
Used by Mortgage Approval Agent to request property valuations
Platform-compatible version using LangGraph SDK
"""

import json
from typing import Dict, Any, Optional
try:
    from langgraph_sdk import get_client
    LangGraph_SDK_available = True
except ImportError:
    LangGraph_SDK_available = False

class MortgagePropertyValuationClient:
    """Client for mortgage agent to communicate with property valuation agent"""
    
    def __init__(self, use_mock=True, property_agent_url=None):
        self.use_mock = use_mock
        self.property_agent_url = property_agent_url
        
        # Initialize LangGraph SDK client for platform deployment
        if not use_mock and LangGraph_SDK_available and property_agent_url:
            try:
                self.client = get_client(url=property_agent_url)
                self.platform_mode = True
            except Exception as e:
                print(f"Warning: Could not connect to property valuation agent: {e}")
                self.client = None
                self.platform_mode = False
        else:
            self.client = None
            self.platform_mode = False
        
    def request_property_valuation(self, property_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request property valuation from PropertyValuation agent
        
        Args:
            property_info: Property information from mortgage application
            
        Returns:
            Valuation response formatted for mortgage processing
        """
        
        if self.use_mock or not self.platform_mode:
            return self._mock_property_valuation(property_info)
        
        try:
            # Create standardized A2A request for platform deployment
            valuation_request = {
                "property_address": property_info.get("property_address", ""),
                "property_type": property_info.get("property_type", "Single Family"),
                "purchase_price": property_info.get("purchase_price", 0),
                "loan_amount": property_info.get("loan_amount", 0),
                "request_id": f"mortgage_{property_info.get('application_id', 'unknown')}",
                "requesting_agent": "MortgageApproval"
            }
            
            # Send request to PropertyValuation agent via LangGraph platform
            response = self.client.runs.create(
                assistant_id="property_valuation_agent",
                input=valuation_request,
                config={"configurable": {"enable_a2a_communication": True}}
            )
            
            # Wait for completion and get result
            final_response = self.client.runs.wait(response["run_id"])
            
            if final_response.get("status") == "success":
                result_data = final_response.get("output", {})
                
                return {
                    "status": "SUCCESS",
                    "valuation_data": {
                        "property_valuation": result_data.get("valuation_result", {})
                    },
                    "raw_response": final_response
                }
            else:
                return {
                    "status": "ERROR",
                    "error_message": final_response.get("error", "Property valuation failed"),
                    "valuation_data": None
                }
                
        except Exception as e:
            return {
                "status": "ERROR",
                "error_message": f"A2A communication error: {str(e)}",
                "valuation_data": None
            }
    
    def _mock_property_valuation(self, property_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock property valuation when PropValue agent is not available
        
        Args:
            property_info: Property information
            
        Returns:
            Mock valuation response
        """
        
        # Simple mock valuation based on property type and size
        base_value = 400000  # Default base value
        
        if property_info.get('square_footage'):
            base_value = property_info['square_footage'] * 200  # $200 per sq ft
        
        # Adjust for property type
        property_type = property_info.get('property_type', 'single_family')
        if property_type == 'condo':
            base_value *= 0.9
        elif property_type == 'townhouse':
            base_value *= 0.95
        elif property_type == 'multi_family':
            base_value *= 1.1
        
        mock_valuation = {
            "property_valuation": {
                "estimated_value": base_value,
                "confidence_level": "MEDIUM",
                "confidence_score": 75,
                "valuation_range": {
                    "min_value": base_value * 0.9,
                    "max_value": base_value * 1.1
                },
                "appraisal_date": "2024-12-15",
                "appraiser_notes": "Mock valuation - PropValue agent not available"
            },
            "loan_to_value_calculation": {
                "estimated_value": base_value,
                "ltv_ready": True
            },
            "valuation_flags": {
                "high_confidence": False,  # Mock data always medium confidence
                "market_stable": True,
                "comparable_data_sufficient": True
            }
        }
        
        return {
            "status": "SUCCESS",
            "valuation_data": mock_valuation,
            "raw_response": {"note": "Mock data - PropValue agent not available"}
        }
    
    def extract_loan_to_value_info(self, valuation_response: Dict[str, Any], loan_amount: float) -> Dict[str, Any]:
        """
        Extract loan-to-value calculation from valuation response
        
        Args:
            valuation_response: Response from property valuation
            loan_amount: Requested loan amount
            
        Returns:
            LTV analysis for mortgage decision
        """
        
        if valuation_response.get('status') != 'SUCCESS':
            return {
                "ltv_available": False,
                "error": "Property valuation failed"
            }
        
        valuation_data = valuation_response['valuation_data']['property_valuation']
        estimated_value = valuation_data['estimated_value']
        
        ltv_ratio = loan_amount / estimated_value
        
        return {
            "ltv_available": True,
            "estimated_property_value": estimated_value,
            "loan_amount": loan_amount,
            "ltv_ratio": ltv_ratio,
            "ltv_percentage": ltv_ratio * 100,
            "confidence_level": valuation_data['confidence_level'],
            "confidence_score": valuation_data['confidence_score'],
            "valuation_range": valuation_data['valuation_range'],
            "ltv_risk_assessment": self._assess_ltv_risk(ltv_ratio, valuation_data['confidence_level'])
        }
    
    def _assess_ltv_risk(self, ltv_ratio: float, confidence_level: str) -> Dict[str, Any]:
        """Assess LTV risk for mortgage decision"""
        
        risk_factors = []
        risk_level = "LOW"
        
        if ltv_ratio > 0.95:
            risk_factors.append("Very high LTV (>95%)")
            risk_level = "HIGH"
        elif ltv_ratio > 0.80:
            risk_factors.append("High LTV (>80%)")
            risk_level = "MEDIUM" if confidence_level == "HIGH" else "HIGH"
        elif ltv_ratio > 0.70:
            if confidence_level == "LOW":
                risk_factors.append("Medium LTV with low confidence valuation")
                risk_level = "MEDIUM"
        
        if confidence_level == "LOW":
            risk_factors.append("Low confidence property valuation")
            if risk_level == "LOW":
                risk_level = "MEDIUM"
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "requires_pmi": ltv_ratio > 0.80,
            "recommended_action": self._get_ltv_recommendation(risk_level, ltv_ratio)
        }
    
    def _get_ltv_recommendation(self, risk_level: str, ltv_ratio: float) -> str:
        """Get recommendation based on LTV risk assessment"""
        
        if risk_level == "HIGH":
            return "REJECT" if ltv_ratio > 0.95 else "REQUIRE_ADDITIONAL_REVIEW"
        elif risk_level == "MEDIUM":
            return "REQUIRE_PMI" if ltv_ratio > 0.80 else "APPROVE_WITH_CONDITIONS"
        else:
            return "APPROVE"

# Example usage for testing
if __name__ == "__main__":
    client = MortgagePropertyValuationClient()
    
    test_property = {
        "property_address": "123 Test St, Sample City, TX 75001",
        "property_type": "single_family",
        "square_footage": 2200,
        "bedrooms": 4,
        "bathrooms": 2.5,
        "year_built": 2010,
        "lot_size": 0.25
    }
    
    print("Testing A2A Property Valuation...")
    response = client.request_property_valuation(test_property)
    print(f"Status: {response['status']}")
    
    if response['status'] == 'SUCCESS':
        ltv_info = client.extract_loan_to_value_info(response, 350000)
        print(f"LTV Analysis: {json.dumps(ltv_info, indent=2)}")
    else:
        print(f"Error: {response['error_message']}")