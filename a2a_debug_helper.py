#!/usr/bin/env python3
"""
A2A Debug Helper - Find the correct PropValue agent configuration
"""

def get_propvalue_config_guide():
    """Generate a guide for finding PropValue agent configuration"""
    
    print("🔍 A2A CONFIGURATION GUIDE")
    print("=" * 50)
    
    print("\n📋 **Step 1: Find Your PropValue Agent Details**")
    print("In your LangGraph platform:")
    print("1. Go to your PropValue agent deployment")
    print("2. Copy the deployment URL (e.g., https://your-deployment.langgraph.cloud)")
    print("3. Note the assistant ID (usually shown in deployment settings)")
    
    print("\n🌐 **Step 2: Set Environment Variables in LangMortgage**")
    print("Set these in your LangMortgage deployment:")
    print("```")
    print("PROPVALUE_AGENT_URL=https://your-propvalue-deployment.langgraph.cloud")
    print("PROPVALUE_ASSISTANT_ID=your-actual-assistant-id")
    print("```")
    
    print("\n🔧 **Step 3: Common Assistant ID Patterns**")
    print("Try these patterns if you're not sure:")
    print("- If your deployment is named 'PropValue': assistant_id might be 'propvalue'")
    print("- If your deployment is named 'property-value': assistant_id might be 'property-value'")
    print("- Check the LangGraph platform deployment details for the exact ID")
    
    print("\n⚠️  **Current Error Analysis**")
    print("Error: 'All assistant ID attempts failed'")
    print("✅ GOOD: A2A communication is working (no more LLM calls)")
    print("❌ ISSUE: Wrong assistant_id or URL")
    
    print("\n📊 **Quick Test Configuration**")
    print("For immediate testing, you can modify nodes.py temporarily:")
    print("```python")
    print("# In nodes.py around line 325, add:")
    print("propvalue_url = 'https://your-actual-propvalue-url.langgraph.cloud'")
    print("assistant_id = 'your-actual-assistant-id'")
    print("```")

if __name__ == "__main__":
    get_propvalue_config_guide()