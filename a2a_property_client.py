"""
A2A Client for integrating with Property Valuation Agent
Used by Mortgage Approval Agent to request property valuations
Platform-compatible version using LangGraph SDK
"""

import json
import os
import requests
from typing import Dict, Any, Optional

# Platform detection
def is_langgraph_platform():
    """Detect if running on LangGraph platform"""
    # Check various environment indicators
    checks = [
        ('LANGGRAPH_CLOUD', os.getenv('LANGGRAPH_CLOUD') == 'true'),
        ('LANGGRAPH_PLATFORM', os.getenv('LANGGRAPH_PLATFORM') == 'true'),
        ('HOSTNAME contains langgraph.cloud', 'langgraph.cloud' in os.getenv('HOSTNAME', '')),
        ('PATH_INFO contains /api/', '/api/' in os.getenv('PATH_INFO', '')),
        ('SERVER_SOFTWARE contains langgraph-api', 'langgraph-api' in str(os.getenv('SERVER_SOFTWARE', ''))),
        ('Has LANGGRAPH_* env vars', any(key.startswith('LANGGRAPH_') for key in os.environ.keys())),
        ('Running in container', os.path.exists('/.dockerenv') or os.getenv('KUBERNETES_SERVICE_HOST')),
    ]
    
    is_platform = any(check[1] for check in checks)
    
    # Debug output
    print("🔍 Platform Detection Results:")
    for name, result in checks:
        print(f"   {name}: {result}")
    print(f"   🎯 Platform detected: {is_platform}")
    
    return is_platform

# SDK not used - using direct HTTP calls for better platform compatibility

class MortgagePropertyValuationClient:
    """Client for mortgage agent to communicate with property valuation agent"""
    
    def __init__(self, use_mock=None, property_agent_url=None):
        print("🚀 Initializing MortgagePropertyValuationClient...")
        
        # Auto-detect platform and configuration
        self.is_platform = is_langgraph_platform()
        
        # Debug environment variables
        print("🔍 Environment Variables Check:")
        env_vars = ['PROPVALUE_AGENT_URL', 'PROPERTY_VALUATION_AGENT_URL', 'LANGGRAPH_CLOUD', 'LANGGRAPH_PLATFORM']
        for var in env_vars:
            value = os.getenv(var)
            print(f"   {var}: {value if value else 'Not set'}")
        
        # Get PropValue agent URL from environment or parameter
        self.property_agent_url = (
            property_agent_url or 
            os.getenv('PROPVALUE_AGENT_URL') or
            os.getenv('PROPERTY_VALUATION_AGENT_URL')
        )
        
        print(f"🌐 Final PropValue URL: {self.property_agent_url}")
        
        # Determine if we should use mock mode
        if use_mock is None:
            # Auto-decide: use real A2A if on platform and URL available
            self.use_mock = not (self.is_platform and self.property_agent_url)
            
            # PLATFORM OVERRIDE: If on platform but no URL, try to construct one
            if self.is_platform and not self.property_agent_url:
                print("🔧 Platform detected but no PropValue URL - attempting to use default")
                # Try common PropValue deployment names
                possible_urls = [
                    "https://fnma-property-value-agent-a-847d714161b5593186939c2aaa3e7c33.us.langgraph.app"
                ]
                
                for url in possible_urls:
                    print(f"   Trying: {url}")
                    self.property_agent_url = url
                    break
                
                # Force A2A attempt even without explicit URL
                self.use_mock = False
                print(f"🚀 Forcing A2A attempt with: {self.property_agent_url}")
            
            # TEMPORARY: Force A2A if URL is available (for testing)
            if self.property_agent_url and not self.use_mock:
                print("🔧 A2A mode enabled (URL available)")
                self.use_mock = False
        else:
            self.use_mock = use_mock
        
        print(f"🎭 Final mock mode decision: {self.use_mock}")
        print(f"🌐 Using PropValue URL: {self.property_agent_url}")
        
        # Always use HTTP mode - SDK causes issues on platform
        self.platform_mode = True
        self.client = None
        
        if not self.use_mock and self.property_agent_url:
            print(f"🌐 HTTP mode enabled for: {self.property_agent_url}")
            print("🔧 Using direct HTTP calls to avoid SDK complexity")
        
    def request_property_valuation(self, property_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request property valuation from PropertyValuation agent
        
        Args:
            property_info: Property information from mortgage application
            
        Returns:
            Valuation response formatted for mortgage processing
        """
        
        if self.use_mock:
            print("🎭 Using MOCK mode - not calling real PropValue agent")
            return self._mock_property_valuation(property_info)
        
        if not self.property_agent_url:
            print("⚠️  No PropValue URL available, falling back to mock")
            return self._mock_property_valuation(property_info)
        
        print(f"🚀 ATTEMPTING REAL A2A CALL to PropValue agent")
        
        try:
            # Create standardized A2A request for platform deployment
            valuation_request = {
                "property_address": property_info.get("property_address", ""),
                "property_type": property_info.get("property_type", "single_family"),
                "square_footage": property_info.get("square_footage", 0),
                "bedrooms": property_info.get("bedrooms", 0),
                "bathrooms": property_info.get("bathrooms", 0),
                "year_built": property_info.get("year_built", 0),
                "lot_size": property_info.get("lot_size", 0),
                "purchase_price": property_info.get("purchase_price", property_info.get("loan_amount", 0) * 1.25),
                "request_id": f"mortgage_{property_info.get('application_id', 'unknown')}",
                "requesting_agent": "MortgageApproval"
            }
            
            print(f"📤 Sending A2A request to PropValue: {self.property_agent_url}")
            
            # Skip SDK and go directly to HTTP since async SDK calls are problematic
            print("🌐 Using HTTP requests instead of SDK to avoid async issues")
            
            # Use HTTP requests with the working pattern from curl test
            headers = {
                "Content-Type": "application/json",
                "x-api-key": os.getenv('LANGGRAPH_API_KEY')
            }
            
            # Get PropValue assistant ID - use specific env var to avoid conflicts
            assistant_id = (
                os.getenv('PROPVALUE_ASSISTANT_ID') or      # Platform-specific
                os.getenv('PROPERTY_VALUATION_ASSISTANT_ID') or  # Alternative name  
                os.getenv('ASSISTANT_ID') or                # Fallback to generic
                "128e123f-7772-47de-9032-23d882e2b7bc"     # Local testing fallback
            )
            
            print(f"🎯 PropValue Assistant ID: {assistant_id}")
            
            # Platform diagnostic info
            if self.is_platform:
                current_assistant = os.getenv('ASSISTANT_ID')
                if current_assistant and current_assistant != assistant_id:
                    print(f"ℹ️  Current LangMortgage Assistant: {current_assistant}")
                    print(f"🎯 Target PropValue Assistant: {assistant_id}")
            
            if not headers["x-api-key"]:
                print("❌ No API key found - HTTP A2A requests will fail")
                return {
                    "status": "ERROR",
                    "error_message": "LANGGRAPH_API_KEY not found in environment",
                    "valuation_data": None
                }
            
            # Use streaming endpoint directly like our successful curl test
            stream_url = f"{self.property_agent_url}/runs/stream"
            
            # Build payload exactly like successful curl request with stream_mode
            payload = {
                "assistant_id": assistant_id,
                "input": {
                    "name": valuation_request.get("requesting_agent", "Single Family Home"),
                    "property_address": valuation_request["property_address"],
                    "property_type": valuation_request["property_type"],
                    "square_footage": valuation_request["square_footage"],
                    "bedrooms": valuation_request["bedrooms"],
                    "bathrooms": valuation_request["bathrooms"],
                    "year_built": valuation_request["year_built"],
                    "lot_size": valuation_request["lot_size"]
                },
                "config": {
                    "recursion_limit": 25
                },
                "stream_mode": ["values"]
            }
            
            try:
                print(f"🚀 Streaming request to: {stream_url}")
                print(f"🔑 Using assistant ID: {assistant_id}")
                
                # Make single streaming request (like successful curl test)
                response = requests.post(
                    stream_url,
                    json=payload,
                    headers=headers,
                    stream=True,
                    timeout=60
                )
                
                if response.status_code != 200:
                    print(f"❌ HTTP {response.status_code}: {response.text}")
                    return {
                        "status": "ERROR",
                        "error_message": f"HTTP {response.status_code}: {response.text}",
                        "valuation_data": None
                    }
                
                # Parse streaming response to get final result
                final_result = None
                run_id = None
                
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])  # Remove 'data: ' prefix
                            
                            # Extract run_id from metadata
                            if "run_id" in data:
                                run_id = data["run_id"]
                            
                            # Look for final result with valuation data
                            if "estimated_value" in data and "confidence_level" in data:
                                final_result = data
                                print(f"✅ Found valuation result: ${data.get('estimated_value', 0):,.2f}")
                                
                        except json.JSONDecodeError:
                            continue
                
                if final_result:
                    # Transform the result to match expected format
                    property_valuation = {
                        "estimated_value": final_result.get("estimated_value"),
                        "confidence_level": final_result.get("confidence_level"),
                        "confidence_score": final_result.get("confidence_score", 85),
                        "valuation_range": final_result.get("valuation_range", {}),
                        "valuation_date": final_result.get("response_data", {}).get("valuation_date"),
                        "appraiser_notes": final_result.get("response_data", {}).get("appraiser_notes"),
                        "comparable_analysis": final_result.get("comparable_analysis", {}),
                        "market_adjustment": final_result.get("market_adjustment", {}),
                        "neighborhood_data": final_result.get("neighborhood_data", {})
                    }
                    
                    return {
                        "status": "SUCCESS",
                        "valuation_data": {
                            "property_valuation": property_valuation,
                            "loan_to_value_calculation": {
                                "estimated_value": final_result.get("estimated_value"),
                                "ltv_ready": True
                            },
                            "valuation_flags": {
                                "high_confidence": final_result.get("confidence_level") == "HIGH",
                                "market_stable": final_result.get("market_trends", {}).get("market_direction") == "STABLE",
                                "comparable_data_sufficient": len(final_result.get("comparable_properties", [])) >= 3
                            }
                        },
                        "raw_response": final_result,
                        "run_id": run_id
                    }
                else:
                    return {
                        "status": "ERROR",
                        "error_message": "No valuation result found in stream response",
                        "valuation_data": None
                    }
                    
            except Exception as e:
                print(f"❌ HTTP request error: {str(e)}")
                return {
                    "status": "ERROR",
                    "error_message": f"Request failed: {str(e)}",
                    "valuation_data": None
                }
                
        except Exception as e:
            print(f"❌ A2A communication failed: {str(e)}")
            print("🔄 Falling back to mock valuation")
            return self._mock_property_valuation(property_info)
    
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