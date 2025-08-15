"""
Error handling utilities for MortgageApproval Agent
Provides robust error handling for LangGraph SaaS deployment
"""

import logging
import traceback
from typing import Dict, Any, Optional
from state import MortgageState

# Configure logging for SaaS platform
logger = logging.getLogger(__name__)

class MortgageApprovalError(Exception):
    """Custom exception for mortgage approval errors"""
    
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

def handle_node_error(state: MortgageState, node_name: str, error: Exception) -> MortgageState:
    """Handle errors that occur in workflow nodes"""
    
    error_message = f"Error in {node_name}: {str(error)}"
    logger.error(error_message, exc_info=True)
    
    # Add error to state
    if 'errors' not in state:
        state['errors'] = []
    state['errors'].append(error_message)
    
    # Set current step to indicate failure
    state['current_step'] = f"{node_name}_failed"
    
    # For critical errors that should result in rejection
    if isinstance(error, MortgageApprovalError):
        if error.error_code in ['INVALID_APPLICATION', 'PROPERTY_VALUATION_FAILED', 'SYSTEM_ERROR']:
            state['final_decision'] = 'REJECTED'
            state['decision_reason'] = f'Application rejected due to system error: {error.message}'
            state['confidence_score'] = 0
            state['current_step'] = 'final_decision_completed'
    
    return state

def handle_a2a_property_error(error: Exception, property_address: str) -> Dict[str, Any]:
    """Handle A2A property valuation errors"""
    
    error_details = {
        "status": "ERROR",
        "error_code": "PROPERTY_VALUATION_A2A_ERROR",
        "error_message": str(error),
        "property_address": property_address,
        "valuation_data": None
    }
    
    # Log the error
    logger.error(f"A2A Property Valuation Error for {property_address}: {str(error)}", exc_info=True)
    
    # Categorize error types
    if "timeout" in str(error).lower():
        error_details["error_code"] = "PROPERTY_VALUATION_TIMEOUT"
    elif "not found" in str(error).lower() or "unavailable" in str(error).lower():
        error_details["error_code"] = "PROPERTY_VALUATION_UNAVAILABLE"
    elif "authentication" in str(error).lower():
        error_details["error_code"] = "PROPERTY_VALUATION_AUTH_ERROR"
    
    return error_details

def validate_mortgage_environment() -> Dict[str, Any]:
    """Validate environment for mortgage approval SaaS deployment"""
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    import os
    
    # Check required environment variables
    required_vars = ['GOOGLE_API_KEY']
    for var in required_vars:
        if not os.getenv(var):
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing required environment variable: {var}")
    
    # Check optional environment variables
    optional_vars = {
        'LANGCHAIN_TRACING_V2': 'Tracing not enabled',
        'LANGCHAIN_API_KEY': 'LangSmith integration not available',
        'PROPERTY_VALUATION_ENDPOINT': 'Property valuation A2A endpoint not configured'
    }
    
    for var, warning in optional_vars.items():
        if not os.getenv(var):
            validation_result["warnings"].append(warning)
    
    return validation_result

def create_safe_mortgage_decision(state: MortgageState, error_context: str) -> MortgageState:
    """Create a safe mortgage decision when workflow fails"""
    
    # Default to rejection with explanation when system errors occur
    state['final_decision'] = 'REJECTED'
    state['decision_reason'] = f'Application rejected due to system error: {error_context}'
    state['confidence_score'] = 0
    state['current_step'] = 'final_decision_completed'
    
    # Ensure all required result fields are initialized
    result_fields = [
        'data_validation_result',
        'credit_assessment_result', 
        'income_verification_result',
        'property_valuation_result',
        'risk_analysis_result'
    ]
    
    for field in result_fields:
        if field not in state or not state[field]:
            state[field] = {
                "status": "NOT_COMPLETED",
                "error": "Workflow terminated due to system error"
            }
    
    return state

def should_continue_after_error(state: MortgageState, node_name: str) -> str:
    """Determine workflow continuation after error"""
    
    # Critical errors that should terminate workflow
    critical_nodes = ['data_validation', 'property_valuation']
    
    if node_name in critical_nodes:
        return 'decision'  # Skip to final decision
    
    # Non-critical errors can continue to next node
    node_flow = {
        'credit_assessment': 'income_verification',
        'income_verification': 'property_valuation',
        'risk_analysis': 'decision'
    }
    
    return node_flow.get(node_name, 'decision')