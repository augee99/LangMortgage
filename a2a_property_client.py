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

try:
    from langgraph_sdk import get_client
    LangGraph_SDK_available = True
except ImportError:
    LangGraph_SDK_available = False
    get_client = None

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
                    "https://fnma-property-value-agent-a-847d714161b5593186939c2aaa3e7c33.us.langgraph.app",
                    "https://property-valuation-agent.langgraph.cloud",
                    "https://propvalue.langgraph.cloud", 
                    "https://property-value.langgraph.cloud"
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
        
        # Initialize platform client
        self.platform_mode = False
        self.client = None
        
        if not self.use_mock and self.property_agent_url:
            try:
                if LangGraph_SDK_available and get_client:
                    print(f"🔗 Attempting SDK connection to: {self.property_agent_url}")
                    self.client = get_client(url=self.property_agent_url)
                    self.platform_mode = True
                    print(f"✅ SDK connected to PropValue agent: {self.property_agent_url}")
                else:
                    print("⚠️  LangGraph SDK not available, will use HTTP requests")
                    self.platform_mode = True  # Use HTTP instead
                    print(f"🌐 HTTP mode enabled for: {self.property_agent_url}")
            except Exception as e:
                print(f"⚠️  SDK connection failed: {e}")
                print("🌐 Will attempt HTTP requests instead")
                self.platform_mode = True  # Still try HTTP
        
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
            
            if self.client and LangGraph_SDK_available:
                # Use LangGraph SDK - try multiple assistant IDs
                assistant_ids = [
                    "995669b4-14a3-4352-a6d4-2b269c9b74da", # User provided assistant ID
                    "fnma-property-value-agent-a",           # Based on deployment name
                    "property_value_agent",                  # Underscore format
                    "property-value-agent",                  # Dash format
                    "property_valuation_agent",              # Default
                    "propvalue",                             # Short name
                    "fnma-property-value-agent",             # Without suffix
                    None                                     # Default assistant
                ]
                
                for assistant_id in assistant_ids:
                    try:
                        print(f"🔍 Trying assistant_id: {assistant_id}")
                        
                        create_params = {
                            "thread_id": None,  # Let LangGraph create a new thread
                            "input": valuation_request,
                            "config": {"configurable": {"enable_a2a_communication": True}}
                        }
                        
                        if assistant_id:
                            create_params["assistant_id"] = assistant_id
                        
                        response = self.client.runs.create(**create_params)
                        print(f"✅ Run created with ID: {response.get('run_id')}")
                        
                        # Wait for completion and get result
                        final_response = self.client.runs.wait(response["run_id"])
                        print(f"📥 Final response status: {final_response.get('status')}")
                        
                        if final_response.get("status") == "success":
                            result_data = final_response.get("output", {})
                            
                            # Try different output formats
                            valuation_result = (
                                result_data.get("valuation_result") or
                                result_data.get("output") or
                                result_data
                            )
                            
                            print(f"🎯 Found valuation result: {bool(valuation_result)}")
                            
                            return {
                                "status": "SUCCESS",
                                "valuation_data": {
                                    "property_valuation": valuation_result
                                },
                                "raw_response": final_response
                            }
                        else:
                            print(f"⚠️  Assistant {assistant_id} failed: {final_response.get('error')}")
                            continue
                            
                    except Exception as e:
                        print(f"❌ Assistant {assistant_id} error: {str(e)}")
                        continue
                
                # If all assistant IDs failed
                return {
                    "status": "ERROR", 
                    "error_message": "All assistant ID attempts failed",
                    "valuation_data": None
                }
            else:
                # Use HTTP requests as fallback with proper LangGraph API format
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                # Try different API endpoints
                endpoints = [
                    f"{self.property_agent_url}/runs",
                    f"{self.property_agent_url}/invoke", 
                    f"{self.property_agent_url}/stream",
                    f"{self.property_agent_url}"
                ]
                
                for endpoint in endpoints:
                    try:
                        print(f"🔍 Trying HTTP endpoint: {endpoint}")
                        
                        # Try different payload formats
                        payloads = [
                            # Standard LangGraph format
                            {
                                "input": valuation_request,
                                "config": {"configurable": {"enable_a2a_communication": True}}
                            },
                            # Alternative format with assistant_id
                            {
                                "assistant_id": "property_valuation_agent",
                                "input": valuation_request,
                                "config": {"configurable": {"enable_a2a_communication": True}}
                            },
                            # Direct input format
                            valuation_request
                        ]
                        
                        for i, payload in enumerate(payloads):
                            print(f"   📤 Trying payload format {i+1}")
                            
                            response = requests.post(
                                endpoint,
                                json=payload,
                                headers=headers,
                                timeout=30
                            )
                            
                            print(f"   📥 HTTP {response.status_code}: {endpoint}")
                            
                            if response.status_code == 200:
                                try:
                                    result = response.json()
                                    
                                    # Try different output extraction methods
                                    output = (
                                        result.get("output", {}) or
                                        result.get("valuation_result", {}) or
                                        result
                                    )
                                    
                                    valuation_result = (
                                        output.get("valuation_result") or
                                        output.get("output") or
                                        output
                                    )
                                    
                                    if valuation_result and isinstance(valuation_result, dict):
                                        print(f"✅ HTTP success with endpoint {endpoint}")
                                        return {
                                            "status": "SUCCESS",
                                            "valuation_data": {
                                                "property_valuation": valuation_result
                                            },
                                            "raw_response": result
                                        }
                                        
                                except Exception as parse_error:
                                    print(f"   ❌ JSON parse error: {parse_error}")
                                    continue
                            
                            elif response.status_code in [404, 405]:
                                break  # Wrong endpoint, try next one
                                
                    except Exception as e:
                        print(f"❌ HTTP error for {endpoint}: {str(e)}")
                        continue
                
                return {
                    "status": "ERROR",
                    "error_message": "All HTTP endpoint attempts failed",
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