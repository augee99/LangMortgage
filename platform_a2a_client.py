"""
Platform-specific A2A client for LangGraph SaaS
Handles inter-agent communication using LangGraph platform endpoints
"""

import os
import json
import requests
import uuid
from typing import Dict, Any, Optional
from .state import MortgageState

class LangGraphA2AClient:
    """A2A client for LangGraph platform communication"""
    
    def __init__(self):
        # Get platform configuration from environment
        self.platform_base_url = os.getenv('LANGGRAPH_PLATFORM_URL', 'https://api.langgraph.ai')
        self.api_key = os.getenv('LANGGRAPH_API_KEY')
        self.property_agent_id = os.getenv('PROPERTY_AGENT_ID')
        
        if not self.api_key:
            raise ValueError("LANGGRAPH_API_KEY environment variable required")
        if not self.property_agent_id:
            raise ValueError("PROPERTY_AGENT_ID environment variable required")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def request_property_valuation(self, property_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request property valuation from PropertyValue agent on LangGraph platform
        
        Args:
            property_info: Property information for valuation
            
        Returns:
            Valuation response from PropertyValue agent
        """
        
        request_id = str(uuid.uuid4())
        
        # Create platform-compatible request
        platform_request = {
            "input": {
                # Property data for valuation
                "property_address": property_info.get('property_address', ''),
                "property_type": property_info.get('property_type', 'single_family'),
                "square_footage": property_info.get('square_footage'),
                "bedrooms": property_info.get('bedrooms'),
                "bathrooms": property_info.get('bathrooms'),
                "year_built": property_info.get('year_built'),
                "lot_size": property_info.get('lot_size'),
                
                # A2A metadata
                "request_id": request_id,
                "requesting_agent": "MortgageApproval",
                "response_data": None,
                
                # Initialize empty state fields
                "comparable_properties": [],
                "market_trends": {},
                "neighborhood_data": {},
                "estimated_value": None,
                "confidence_level": None,
                "valuation_range": None,
                "comparable_analysis": {},
                "market_adjustment": {},
                "final_assessment": {},
                "current_step": "initialized",
                "errors": [],
                "warnings": []
            },
            "config": {
                "recursion_limit": 100,
                "configurable": {
                    "model": "gemini-2.5-flash",
                    "temperature": 0.1,
                    "enable_a2a_communication": True
                }
            }
        }
        
        try:
            # Make request to PropertyValue agent on platform
            endpoint = f"{self.platform_base_url}/agents/{self.property_agent_id}/invoke"
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=platform_request,
                timeout=120  # 2 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract valuation data from platform response
                output = result.get('output', {})
                
                if output.get('response_data'):
                    return {
                        "status": "SUCCESS",
                        "valuation_data": {
                            "property_valuation": output['response_data']
                        },
                        "raw_response": result
                    }
                else:
                    return {
                        "status": "ERROR",
                        "error_message": "No valuation data in response",
                        "valuation_data": None
                    }
            else:
                return {
                    "status": "ERROR",
                    "error_message": f"Platform request failed: {response.status_code} - {response.text}",
                    "valuation_data": None
                }
                
        except requests.exceptions.Timeout:
            return {
                "status": "ERROR",
                "error_message": "PropertyValue agent request timed out",
                "valuation_data": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "ERROR",
                "error_message": f"Network error: {str(e)}",
                "valuation_data": None
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error_message": f"Unexpected error: {str(e)}",
                "valuation_data": None
            }
    
    def extract_loan_to_value_info(self, valuation_response: Dict[str, Any], loan_amount: float) -> Dict[str, Any]:
        """Extract LTV analysis from valuation response"""
        
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

# Platform-compatible mortgage property valuation client
class PlatformMortgagePropertyValuationClient:
    """Platform-specific client for mortgage agent property valuation requests"""
    
    def __init__(self):
        self.a2a_client = LangGraphA2AClient()
    
    def request_property_valuation(self, property_info: Dict[str, Any]) -> Dict[str, Any]:
        """Request property valuation using platform A2A"""
        return self.a2a_client.request_property_valuation(property_info)
    
    def extract_loan_to_value_info(self, valuation_response: Dict[str, Any], loan_amount: float) -> Dict[str, Any]:
        """Extract LTV info using platform client"""
        return self.a2a_client.extract_loan_to_value_info(valuation_response, loan_amount)