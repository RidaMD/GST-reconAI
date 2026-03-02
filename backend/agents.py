import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

load_dotenv()

def generate_fallback_audit(data: dict) -> str:
    """
    Generated a structured, rule-based audit report when AI is unavailable.
    """
    invoice_id = data.get("invoice_id", "N/A")
    risk_level = data.get("risk_level", "UNKNOWN")
    risk_score = data.get("risk_score", 0)
    root_causes = data.get("root_cause", "N/A").split(" | ")
    amount = data.get("amount_invoice", 0)
    
    # Analyze root causes for structural/behavioral/financial
    structural = [c for c in root_causes if c in ["NO IRN", "MISSING 2B", "SUPPLIER NON FILED"]]
    behavioral = [c for c in root_causes if c in ["LATE FILING", "CHRONIC LATE", "MISSED FILING", "BROKEN UPSTREAM"]]
    
    report = f"""# GST Audit Report (Rule-Based Fallback)
**Invoice ID:** {invoice_id}
**Risk Level:** {risk_level} (Score: {risk_score})

> [!NOTE]
> This report was generated using rule-based analysis as the AI engine is currently offline or in high demand.

### Risk Analysis (3 Levels)
- **Level 1: Structural Break:** {", ".join(structural) if structural else "No major structural breaks detected."}
- **Level 2: Vendor Behavior:** {", ".join(behavioral) if behavioral else "Vendor behavior appears standard based on available graph nodes."}
- **Level 3: Financial Exposure:** This invoice carries a taxable value of Rs. {amount:,.2f}. The risk multiplier was adjusted based on its relative size to your total procurement pool.

### Appreciable Action to be Taken
{"**STRICT ACTION REQUIRED:** Immediate hold on ITC claim for this invoice. Contact supplier for reconciliation." if risk_score > 100 else "**CAUTION:** Verify GSTR-2B reflection before next filing cycle." if risk_score > 50 else "Monitor following period for status update."}
"""
    return report

def generate_audit_report(invoice_data: dict) -> str:
    """
    Takes an invoice risk dictionary and uses LangChain + OpenAI to generate
    an easy-to-understand plain language Audit Report.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return "Error: OPENAI_API_KEY is not set in the environment."

    try:
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2, openai_api_key=openai_api_key)
        
        prompt_template = """
        You are an elite GST (Goods and Services Tax) Compliance Auditor AI.
        
        I will provide you with the data for an invoice that has been run through our multi-hop Knowledge Graph Engine, identifying a mismatch based on its relationships and nodes.
        Your job is to read the data, risk score, and root cause, and produce a highly professional "Audit Non-Compliance Report".
        
        You MUST explicitly analyze the risk based on the following 3 levels:
        1. Structural Break (Missing IRN, Not in Returns, Broken upstream chains)
        2. Vendor Behavior (Late filing, missed periods)
        3. Financial Exposure (Value of invoice relative to total exposure)
        
        Finally, you MUST provide an appreciable action to be taken based on this analysis.
        Keep it concise, actionable, and formatted nicely in Markdown. Don't use code blocks, just regular markdown text, headers, and bullet points.
        
        Data:
        {data}
        
        Format desired:
        # GST Audit Report
        **Invoice ID:** [id]
        **Risk Level:** [level] (Score: [score])
        
        ### Risk Analysis (3 Levels)
        - **Level 1: Structural Break:** [Explanation]
        - **Level 2: Vendor Behavior:** [Explanation]
        - **Level 3: Financial Exposure:** [Explanation]
        
        ### Appreciable Action to be Taken
        [Clear, decisive recommendation for the buyer]
        """
        
        prompt = PromptTemplate(input_variables=["data"], template=prompt_template)
        chain = prompt | llm
        
        response = chain.invoke({"data": json.dumps(invoice_data, indent=2)})
        
        return response.content
        
    except Exception as e:
        # If OpenAI fails (Quota, Timeout, etc.), use the localized fallback generator
        print(f"LLM Error: {str(e)}. Triggering Rule-Based Fallback.")
        return generate_fallback_audit(invoice_data)
