# LangMortgage Platform Testing Guide

## Sample JSON Inputs for LangGraph Platform

### 1. Basic Test Input (`sample_langgraph_input.json`)
```json
{
  "applicant_name": "Sarah Johnson",
  "credit_score": 720,
  "annual_income": 85000,
  "employment_years": 3.5,
  "loan_amount": 320000,
  "property_value": 400000,
  "down_payment": 80000,
  "debt_to_income_ratio": 0.28,
  "property_address": "123 Main St, Austin, TX 78701",
  "property_type": "single_family",
  "square_footage": 2200,
  "bedrooms": 4,
  "bathrooms": 2.5,
  "year_built": 2015,
  "lot_size": 0.25,
  "loan_purpose": "purchase"
}
```

### 2. Test Scenarios

The `platform_test_samples.json` file contains 4 different scenarios:

- **strong_application**: High credit score, good income, low risk
- **marginal_application**: Moderate credit, higher DTI ratio
- **high_risk_application**: Low credit score, high risk factors
- **refinance_application**: Refinancing scenario

### 3. Expected Workflow

1. **Data Validation**: Validates all input fields
2. **Credit Assessment**: Analyzes credit score and assigns grade
3. **Income Verification**: Checks income sufficiency
4. **Property Valuation**: Calls PropValue agent via A2A integration
5. **Risk Analysis**: Combines all factors for risk assessment
6. **Final Decision**: APPROVED/REJECTED with confidence score

### 4. Property Valuation Integration

The workflow now successfully integrates with the PropValue agent:
- ✅ Real property valuations via A2A calls
- ✅ Streaming API integration
- ✅ Proper response formatting
- ✅ Error handling and fallback to mock data

### 5. Testing on LangGraph Platform

To test on the platform:

1. Deploy the LangMortgage agent
2. Use any of the JSON samples as input
3. Monitor the workflow execution
4. Verify property valuation calls to PropValue agent
5. Check final approval/rejection decision

### 6. Key Features Demonstrated

- **A2A Integration**: Real-time property valuation
- **Multi-step Workflow**: Complete mortgage underwriting process
- **Risk Assessment**: Comprehensive evaluation
- **Error Handling**: Graceful degradation when services unavailable
- **Structured Output**: Detailed decision reasoning

### 7. Environment Requirements

- `LANGGRAPH_API_KEY`: For A2A communication
- `ASSISTANT_ID`: PropValue agent assistant ID
- `PROPVALUE_AGENT_URL`: PropValue agent endpoint

All environment variables are properly configured in `.env` file.