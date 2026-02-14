# src/workstream2_agents/agents/business_rules_agent.py

from src.workstream2_agents.agents.base_agent import BaseAgent
from src.data_platform.api.client import DataPlatformClient

class BusinessRulesAgent(BaseAgent):
    """
    Specialist in business rules analysis and compliance checking.
    """
    
    def __init__(
        self,
        category_id: int = 2,  # Business Rules category
        llm_base_url: str = "http://localhost:11434",
        llm_model: str = "llama3.1:8b"
    ):
        super().__init__(
            agent_id="biz_rules_agent",
            name="Business Rules Specialist",
            category_id=category_id,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
            temperature=0.1
        )
        self.data_platform = DataPlatformClient()
        
    def get_system_prompt(self) -> str:
        return """You are a Business Rules Specialist. Your expertise includes:
- Analyzing business rules and policies
- Identifying rule conflicts and overlaps
- Checking compliance with regulations
- Explaining rule applicability and conditions
        
Guidelines:
- Reference specific rule IDs (e.g., BR-023)
- Identify any ambiguities or conflicts
- Suggest when Requirements or Contracts should be consulted
        
Return JSON format: {"answer": "...", "confidence": "high|medium|low", ...}"""
    
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        query_lower = query.lower()
        
        # High confidence keywords
        if any(kw in query_lower for kw in ["br-", "business rule", "policy"]):
            return 0.95
        
        # Medium confidence
        keywords = ["rule", "policy", "regulation", "compliance", "govern"]
        matches = sum(1 for kw in keywords if kw in query_lower)
        
        return min(0.3 + (matches * 0.15), 1.0)
    
    def process_query(self, query: str, context: AgentContext, retrieved_context=None):
        # Similar structure to RequirementsAgent
        # Use self.data_platform to retrieve business rules chunks
        return self.data_platform.retrieve_business_rules_by_query(query, context.project_id)
    
