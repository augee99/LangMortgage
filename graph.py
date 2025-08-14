from langgraph.graph import StateGraph, END
from state import MortgageState
from nodes import (
    data_validation_node,
    credit_assessment_node,
    income_verification_node,
    risk_analysis_node,
    final_decision_node
)

def create_mortgage_workflow():
    """Create the 5-node mortgage validation workflow"""
    
    # Create the state graph
    workflow = StateGraph(MortgageState)
    
    # Add nodes
    workflow.add_node("data_validation", data_validation_node)
    workflow.add_node("credit_assessment", credit_assessment_node)
    workflow.add_node("income_verification", income_verification_node)
    workflow.add_node("risk_analysis", risk_analysis_node)
    workflow.add_node("decision", final_decision_node)
    
    # Define the flow
    workflow.set_entry_point("data_validation")
    
    # Sequential flow through all nodes
    workflow.add_edge("data_validation", "credit_assessment")
    workflow.add_edge("credit_assessment", "income_verification")
    workflow.add_edge("income_verification", "risk_analysis")
    workflow.add_edge("risk_analysis", "decision")
    workflow.add_edge("decision", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app

# Alternative conditional flow (optional enhancement)
def create_conditional_mortgage_workflow():
    """Create mortgage workflow with conditional routing based on validation results"""
    
    def should_continue_after_validation(state: MortgageState):
        """Route based on data validation results"""
        if state['data_validation_result']['status'] == "FAIL":
            return "decision"  # Skip to rejection if data validation fails
        return "credit_assessment"
    
    def should_continue_after_credit(state: MortgageState):
        """Route based on credit assessment"""
        if state['credit_assessment_result']['credit_grade'] == 'F':
            return "decision"  # Skip to rejection for very poor credit
        return "income_verification"
    
    workflow = StateGraph(MortgageState)
    
    # Add nodes
    workflow.add_node("data_validation", data_validation_node)
    workflow.add_node("credit_assessment", credit_assessment_node)
    workflow.add_node("income_verification", income_verification_node)
    workflow.add_node("risk_analysis", risk_analysis_node)
    workflow.add_node("decision", final_decision_node)
    
    # Define conditional flow
    workflow.set_entry_point("data_validation")
    
    workflow.add_conditional_edges(
        "data_validation",
        should_continue_after_validation,
        {
            "credit_assessment": "credit_assessment",
            "decision": "decision"
        }
    )
    
    workflow.add_conditional_edges(
        "credit_assessment",
        should_continue_after_credit,
        {
            "income_verification": "income_verification",
            "decision": "decision"
        }
    )
    
    workflow.add_edge("income_verification", "risk_analysis")
    workflow.add_edge("risk_analysis", "decision")
    workflow.add_edge("decision", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app