"""
Configuration schema for MortgageApproval Agent
Defines configurable parameters for LangGraph SaaS deployment
"""

from typing import Optional
from typing_extensions import Annotated, TypedDict
from langchain_core.runnables import ConfigurableField


class MortgageApprovalConfiguration(TypedDict):
    """Configuration for Mortgage Approval Agent"""
    
    # LLM Configuration
    model: Annotated[str, ConfigurableField(
        id="model",
        name="LLM Model",
        description="The language model to use for mortgage analysis",
        default="gemini-2.5-flash"
    )]
    
    temperature: Annotated[float, ConfigurableField(
        id="temperature",
        name="Temperature",
        description="Controls randomness in LLM responses (0.0-1.0)",
        default=0.1
    )]
    
    # Credit Assessment Parameters
    minimum_credit_score: Annotated[int, ConfigurableField(
        id="minimum_credit_score",
        name="Minimum Credit Score",
        description="Minimum credit score for loan consideration",
        default=580
    )]
    
    excellent_credit_threshold: Annotated[int, ConfigurableField(
        id="excellent_credit_threshold",
        name="Excellent Credit Threshold",
        description="Credit score threshold for excellent rating",
        default=750
    )]
    
    # Income and DTI Parameters
    max_debt_to_income_ratio: Annotated[float, ConfigurableField(
        id="max_debt_to_income_ratio",
        name="Maximum Debt-to-Income Ratio",
        description="Maximum acceptable debt-to-income ratio",
        default=0.43
    )]
    
    max_payment_to_income_ratio: Annotated[float, ConfigurableField(
        id="max_payment_to_income_ratio",
        name="Maximum Payment-to-Income Ratio",
        description="Maximum acceptable payment-to-income ratio",
        default=0.28
    )]
    
    # LTV and Property Parameters
    max_loan_to_value_ratio: Annotated[float, ConfigurableField(
        id="max_loan_to_value_ratio",
        name="Maximum Loan-to-Value Ratio",
        description="Maximum acceptable loan-to-value ratio",
        default=0.95
    )]
    
    pmi_threshold: Annotated[float, ConfigurableField(
        id="pmi_threshold",
        name="PMI Threshold",
        description="LTV ratio above which PMI is required",
        default=0.80
    )]
    
    # A2A Property Valuation Settings
    enable_property_valuation: Annotated[bool, ConfigurableField(
        id="enable_property_valuation",
        name="Enable Property Valuation",
        description="Enable A2A property valuation requests",
        default=True
    )]
    
    property_valuation_required: Annotated[bool, ConfigurableField(
        id="property_valuation_required",
        name="Property Valuation Required",
        description="Require property valuation for all loans",
        default=True
    )]
    
    min_property_confidence: Annotated[str, ConfigurableField(
        id="min_property_confidence",
        name="Minimum Property Valuation Confidence",
        description="Minimum confidence level required from property valuation",
        default="MEDIUM"
    )]