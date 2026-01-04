"""
Requirements Agent Implementation
Specialist in requirements analysis, gap detection, and traceability.

Dependencies:
    pip install requests typing dataclasses
"""

import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import re


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AgentContext:
    """Shared context across all agents"""
    project_id: int
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    current_query: str = ""
    query_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Standardized response from agents"""
    agent_id: str
    agent_name: str
    content: str
    confidence: float  # 0.0 to 1.0
    sources: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    requires_followup: bool = False
    suggested_agents: List[str] = field(default_factory=list)


# ============================================================================
# BASE AGENT (for reference)
# ============================================================================

class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        category_id: int,
        llm_base_url: str = "http://localhost:11434",
        llm_model: str = "llama3.1:8b",
        temperature: float = 0.1
    ):
        self.agent_id = agent_id
        self.name = name
        self.category_id = category_id
        self.llm_base_url = llm_base_url
        self.llm_model = llm_model
        self.temperature = temperature
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Define agent's personality and expertise"""
        pass
    
    @abstractmethod
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        """
        Determine if this agent should handle the query.
        Returns confidence score 0.0-1.0
        """
        pass
    
    def process_query(
        self,
        query: str,
        context: AgentContext,
        retrieved_context: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """Main processing logic"""
        # This would be implemented in the base class
        # For now, each agent implements its own version
        pass


# ============================================================================
# OLLAMA LLM CLIENT
# ============================================================================

class OllamaLLM:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        self.base_url = base_url
        self.model = model
        self.api_endpoint = f"{base_url}/api/generate"
    
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.1,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate response from Ollama.
        
        Args:
            prompt: The user prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
        
        Returns:
            Generated text response
        """
        # Combine system prompt with user prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=120  # 2 minute timeout for local LLM
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out. Is Ollama running?")
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama. Ensure Ollama is running on localhost:11434")
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")
    
    def health_check(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            models = response.json().get("models", [])
            return any(m["name"] == self.model for m in models)
        except:
            return False


# ============================================================================
# MOCK DATA PLATFORM CLIENT (for Workstream 1 integration)
# ============================================================================

class DataPlatformClient:
    """
    Client for interacting with Workstream 1 data platform.
    Replace with actual implementation once Workstream 1 APIs are ready.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def retrieve_requirements_by_query(
        self,
        query: str,
        project_id: int,
        top_k: int = 5,
        min_similarity: float = 0.3,
        priority_filter: Optional[List[str]] = None,
        status_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Call Workstream 1 API to retrieve requirements"""
        # TODO: Replace with actual API call once Workstream 1 is ready
        # For now, return mock data for testing
        return self._mock_retrieve_requirements(query, project_id, top_k)
    
    def get_requirement_by_id(
        self,
        requirement_id: str,
        project_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get specific requirement by ID"""
        # TODO: Replace with actual API call
        return self._mock_get_requirement(requirement_id, project_id)
    
    def find_requirements_without_design(
        self,
        project_id: int,
        priority_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Find requirements lacking design documentation"""
        # TODO: Replace with actual API call
        return self._mock_find_gaps(project_id, priority_filter)
    
    def get_requirement_traceability(
        self,
        requirement_id: str,
        project_id: int
    ) -> Dict[str, Any]:
        """Get traceability chain for a requirement"""
        # TODO: Replace with actual API call
        return self._mock_get_traceability(requirement_id, project_id)
    
    def get_all_requirement_ids(
        self,
        project_id: int,
        status_filter: Optional[List[str]] = None
    ) -> List[str]:
        """Get all requirement IDs in project"""
        # TODO: Replace with actual API call
        return self._mock_get_all_ids(project_id, status_filter)
    
    # Mock methods for testing (remove once Workstream 1 is integrated)
    def _mock_retrieve_requirements(self, query: str, project_id: int, top_k: int):
        return [
            {
                "id": 1,
                "chunk_text": "The system SHALL support multi-factor authentication for all users.",
                "metadata": {
                    "requirement_id": "REQ-001",
                    "priority": "high",
                    "status": "approved",
                    "section": "Authentication Requirements"
                },
                "filename": "requirements.pdf",
                "page_number": 1,
                "category_name": "Requirements",
                "similarity_score": 0.89
            },
            {
                "id": 2,
                "chunk_text": "The system SHALL implement role-based access control with Admin, Manager, and User roles.",
                "metadata": {
                    "requirement_id": "REQ-045",
                    "priority": "high",
                    "status": "approved",
                    "section": "Authorization Requirements"
                },
                "filename": "requirements.pdf",
                "page_number": 2,
                "category_name": "Requirements",
                "similarity_score": 0.75
            }
        ]
    
    def _mock_get_requirement(self, req_id: str, project_id: int):
        if req_id == "REQ-045":
            return {
                "id": 2,
                "chunk_text": "The system SHALL implement role-based access control with Admin, Manager, and User roles.",
                "metadata": {
                    "requirement_id": "REQ-045",
                    "priority": "high",
                    "status": "approved"
                },
                "filename": "requirements.pdf"
            }
        return None
    
    def _mock_find_gaps(self, project_id: int, priority_filter):
        return [
            {
                "requirement_id": "REQ-025",
                "chunk_text": "The system SHALL support data export in CSV and JSON formats.",
                "priority": "high",
                "status": "approved",
                "has_design": False,
                "filename": "requirements.pdf"
            }
        ]
    
    def _mock_get_traceability(self, req_id: str, project_id: int):
        return {
            "requirement": {
                "id": req_id,
                "text": "The system SHALL implement RBAC...",
                "priority": "high",
                "status": "approved"
            },
            "design_links": [
                {
                    "chunk_id": 123,
                    "chunk_text": "AuthService component handles RBAC logic...",
                    "filename": "design.pdf",
                    "component_name": "AuthService",
                    "confidence": 0.85
                }
            ],
            "tech_spec_links": []
        }
    
    def _mock_get_all_ids(self, project_id: int, status_filter):
        return ["REQ-001", "REQ-002", "REQ-025", "REQ-045"]


# ============================================================================
# REQUIREMENTS AGENT
# ============================================================================

class RequirementsAgent(BaseAgent):
    """
    Specialist in requirements analysis, gap detection, and traceability.
    
    Expertise:
        - Analyzing functional and non-functional requirements
        - Identifying requirement gaps and conflicts
        - Tracing requirements to design and implementation
        - Assessing requirement completeness and clarity
        - Understanding requirement priorities and dependencies
    """
    
    def __init__(
        self,
        category_id: int,
        data_platform_client: DataPlatformClient,
        llm_base_url: str = "http://localhost:11434",
        llm_model: str = "llama3.1:8b"
    ):
        super().__init__(
            agent_id="req_agent",
            name="Requirements Specialist",
            category_id=category_id,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
            temperature=0.1  # Very precise for requirements
        )
        self.data_platform = data_platform_client
        self.llm = OllamaLLM(base_url=llm_base_url, model=llm_model)
    
    def get_system_prompt(self) -> str:
        """System prompt optimized for Llama 3.1"""
        return """You are a Requirements Analysis Specialist. Your expertise includes:
- Analyzing functional and non-functional requirements
- Identifying requirement gaps and conflicts
- Tracing requirements to design and implementation
- Assessing requirement completeness and clarity

Guidelines:
- Be precise and unambiguous
- Reference specific requirement IDs when available (e.g., REQ-001)
- Identify any ambiguities or conflicts
- Check for completeness, testability, and consistency
- Suggest when design or technical specifications should be consulted

Format your response as JSON:
{
  "answer": "Your detailed analysis here",
  "confidence": "high|medium|low",
  "key_sources": ["REQ-001", "REQ-045"],
  "suggests_consulting": ["Design Specialist", "Tech Specs Expert"],
  "reasoning": "Why other agents might be needed"
}"""
    
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        """
        Determine if this agent should handle the query.
        Returns confidence score 0.0-1.0
        """
        query_lower = query.lower()
        
        # High confidence keywords
        high_confidence_keywords = [
            "req-", "requirement id", "requirements document"
        ]
        if any(kw in query_lower for kw in high_confidence_keywords):
            return 0.95
        
        # Medium-high confidence keywords
        requirement_keywords = [
            "requirement", "shall", "must", "feature",
            "functionality", "user story", "acceptance criteria",
            "business need", "capability", "specification",
            "gap", "missing", "without design", "traceability"
        ]
        
        matches = sum(1 for kw in requirement_keywords if kw in query_lower)
        
        # Check query type from context
        query_type = context.query_metadata.get("query_type", "")
        if "requirement" in query_type.lower() or "gap" in query_type.lower():
            return 0.9
        
        # Calculate score based on keyword matches
        base_score = 0.3
        score_per_match = 0.15
        final_score = min(base_score + (matches * score_per_match), 1.0)
        
        return final_score
    
    def process_query(
        self,
        query: str,
        context: AgentContext,
        retrieved_context: Optional[List[Dict]] = None
    ) -> AgentResponse:
        """
        Main processing logic for requirements queries.
        
        Args:
            query: User's question
            context: Agent context with project_id, conversation history
            retrieved_context: Optional pre-retrieved chunks
        
        Returns:
            AgentResponse with answer, confidence, sources
        """
        # Step 1: Detect query type and retrieve appropriate context
        if retrieved_context is None:
            retrieved_context = self._retrieve_context(query, context)
        
        # Step 2: Check for specialized queries
        if self._is_gap_analysis_query(query):
            return self._handle_gap_analysis(query, context)
        
        if self._is_traceability_query(query):
            return self._handle_traceability_query(query, context)
        
        if self._is_specific_requirement_query(query):
            return self._handle_specific_requirement(query, context)
        
        # Step 3: General requirements analysis
        return self._handle_general_query(query, context, retrieved_context)
    
    def _retrieve_context(
        self,
        query: str,
        context: AgentContext,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant requirement chunks"""
        try:
            # Extract any filters from query
            priority_filter = self._extract_priority_filter(query)
            status_filter = self._extract_status_filter(query)
            
            return self.data_platform.retrieve_requirements_by_query(
                query=query,
                project_id=context.project_id,
                top_k=top_k,
                priority_filter=priority_filter,
                status_filter=status_filter
            )
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []
    
    def _extract_priority_filter(self, query: str) -> Optional[List[str]]:
        """Extract priority filter from query"""
        query_lower = query.lower()
        priorities = []
        
        if "high priority" in query_lower or "high-priority" in query_lower:
            priorities.append("high")
        if "medium priority" in query_lower:
            priorities.append("medium")
        if "low priority" in query_lower:
            priorities.append("low")
        
        return priorities if priorities else None
    
    def _extract_status_filter(self, query: str) -> Optional[List[str]]:
        """Extract status filter from query"""
        query_lower = query.lower()
        statuses = []
        
        status_keywords = {
            "approved": "approved",
            "draft": "draft",
            "implemented": "implemented",
            "deprecated": "deprecated"
        }
        
        for keyword, status in status_keywords.items():
            if keyword in query_lower:
                statuses.append(status)
        
        return statuses if statuses else None
    
    def _is_gap_analysis_query(self, query: str) -> bool:
        """Check if query is asking for gap analysis"""
        query_lower = query.lower()
        gap_keywords = [
            "without design", "missing design", "no design",
            "gap", "lacking", "don't have", "haven't"
        ]
        return any(kw in query_lower for kw in gap_keywords)
    
    def _is_traceability_query(self, query: str) -> bool:
        """Check if query is asking for traceability"""
        query_lower = query.lower()
        trace_keywords = [
            "implement", "implements", "satisfied by",
            "design for", "traceability", "linked to",
            "what components", "which design"
        ]
        return any(kw in query_lower for kw in trace_keywords)
    
    def _is_specific_requirement_query(self, query: str) -> bool:
        """Check if query asks for a specific requirement by ID"""
        # Look for REQ-XXX pattern
        return bool(re.search(r'REQ-\d+', query, re.IGNORECASE))
    
    def _handle_gap_analysis(
        self,
        query: str,
        context: AgentContext
    ) -> AgentResponse:
        """Handle gap analysis queries"""
        priority_filter = self._extract_priority_filter(query)
        
        gaps = self.data_platform.find_requirements_without_design(
            project_id=context.project_id,
            priority_filter=priority_filter
        )
        
        if not gaps:
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content="Great news! All requirements have associated design documentation.",
                confidence=0.95,
                sources=[],
                metadata={"gap_count": 0}
            )
        
        # Build response using LLM
        prompt = self._build_gap_analysis_prompt(query, gaps)
        llm_response = self.llm.generate(
            prompt=prompt,
            temperature=self.temperature,
            system_prompt=self.get_system_prompt()
        )
        
        parsed_response = self._parse_llm_response(llm_response)
        
        return AgentResponse(
            agent_id=self.agent_id,
            agent_name=self.name,
            content=parsed_response["answer"],
            confidence=self._map_confidence(parsed_response["confidence"]),
            sources=gaps,
            metadata={
                "gap_count": len(gaps),
                "high_priority_gaps": len([g for g in gaps if g["priority"] == "high"])
            },
            suggested_agents=parsed_response.get("suggests_consulting", [])
        )
    
    def _build_gap_analysis_prompt(self, query: str, gaps: List[Dict]) -> str:
        """Build prompt for gap analysis"""
        gaps_text = "\n".join([
            f"- {g['requirement_id']} (Priority: {g['priority']}): {g['chunk_text'][:100]}..."
            for g in gaps
        ])
        
        return f"""Query: {query}

Requirements without design documentation:
{gaps_text}

Provide a clear analysis:
1. Summarize the gaps found
2. Highlight high-priority gaps
3. Suggest next steps
4. Recommend if Design Specialist should be consulted

Return JSON format as specified."""
    
    def _handle_traceability_query(
        self,
        query: str,
        context: AgentContext
    ) -> AgentResponse:
        """Handle traceability queries"""
        # Extract requirement ID from query
        req_match = re.search(r'REQ-\d+', query, re.IGNORECASE)
        
        if not req_match:
            # General traceability question
            return self._handle_general_query(query, context, [])
        
        req_id = req_match.group(0).upper()
        
        # Get traceability information
        trace_data = self.data_platform.get_requirement_traceability(
            requirement_id=req_id,
            project_id=context.project_id
        )
        
        if not trace_data or not trace_data.get("requirement"):
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content=f"I couldn't find requirement {req_id} in the project.",
                confidence=0.3,
                sources=[]
            )
        
        # Build response using LLM
        prompt = self._build_traceability_prompt(query, req_id, trace_data)
        llm_response = self.llm.generate(
            prompt=prompt,
            temperature=self.temperature,
            system_prompt=self.get_system_prompt()
        )
        
        parsed_response = self._parse_llm_response(llm_response)
        
        # Combine all sources
        all_sources = [trace_data["requirement"]]
        if trace_data.get("design_links"):
            all_sources.extend(trace_data["design_links"])
        if trace_data.get("tech_spec_links"):
            all_sources.extend(trace_data["tech_spec_links"])
        
        return AgentResponse(
            agent_id=self.agent_id,
            agent_name=self.name,
            content=parsed_response["answer"],
            confidence=self._map_confidence(parsed_response["confidence"]),
            sources=all_sources,
            metadata={"requirement_id": req_id},
            suggested_agents=parsed_response.get("suggests_consulting", [])
        )
    
    def _build_traceability_prompt(
        self,
        query: str,
        req_id: str,
        trace_data: Dict
    ) -> str:
        """Build prompt for traceability analysis"""
        req = trace_data["requirement"]
        design_links = trace_data.get("design_links", [])
        tech_links = trace_data.get("tech_spec_links", [])
        
        design_text = "\n".join([
            f"- {d['component_name']}: {d['chunk_text'][:100]}... (Confidence: {d['confidence']})"
            for d in design_links
        ]) if design_links else "No design documentation linked"
        
        tech_text = "\n".join([
            f"- {t.get('api_endpoint', 'Component')}: {t['chunk_text'][:100]}..."
            for t in tech_links
        ]) if tech_links else "No technical specifications linked"
        
        return f"""Query: {query}

Requirement {req_id}:
Priority: {req['priority']}
Status: {req['status']}
Text: {req['text']}

Design Documentation:
{design_text}

Technical Specifications:
{tech_text}

Provide a clear traceability analysis:
1. Summarize the requirement
2. Explain design implementations
3. Describe technical specifications
4. Assess completeness of traceability

Return JSON format as specified."""
    
    def _handle_specific_requirement(
        self,
        query: str,
        context: AgentContext
    ) -> AgentResponse:
        """Handle queries about specific requirements"""
        req_match = re.search(r'REQ-\d+', query, re.IGNORECASE)
        req_id = req_match.group(0).upper()
        
        requirement = self.data_platform.get_requirement_by_id(
            requirement_id=req_id,
            project_id=context.project_id
        )
        
        if not requirement:
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content=f"I couldn't find requirement {req_id} in the project.",
                confidence=0.3,
                sources=[]
            )
        
        prompt = self._build_specific_requirement_prompt(query, requirement)
        llm_response = self.llm.generate(
            prompt=prompt,
            temperature=self.temperature,
            system_prompt=self.get_system_prompt()
        )
        
        parsed_response = self._parse_llm_response(llm_response)
        
        return AgentResponse(
            agent_id=self.agent_id,
            agent_name=self.name,
            content=parsed_response["answer"],
            confidence=self._map_confidence(parsed_response["confidence"]),
            sources=[requirement],
            metadata={"requirement_id": req_id},
            suggested_agents=parsed_response.get("suggests_consulting", [])
        )
    
    def _build_specific_requirement_prompt(
        self,
        query: str,
        requirement: Dict
    ) -> str:
        """Build prompt for specific requirement queries"""
        meta = requirement.get("metadata", {})
        
        return f"""Query: {query}

Requirement Details:
ID: {meta.get('requirement_id', 'Unknown')}
Priority: {meta.get('priority', 'Unknown')}
Status: {meta.get('status', 'Unknown')}
Section: {meta.get('section', 'Unknown')}
Text: {requirement['chunk_text']}

Source: {requirement['filename']} (Page {requirement.get('page_number', 'N/A')})

Analyze this requirement and answer the query:
1. Provide clear explanation
2. Assess completeness and testability
3. Identify any ambiguities
4. Suggest if other categories should be consulted

Return JSON format as specified."""
    
    def _handle_general_query(
        self,
        query: str,
        context: AgentContext,
        retrieved_context: List[Dict]
    ) -> AgentResponse:
        """Handle general requirements queries"""
        if not retrieved_context:
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content="I couldn't find relevant requirements for your query. Please try rephrasing or check if requirements documents are uploaded.",
                confidence=0.2,
                sources=[]
            )
        
        prompt = self._build_general_query_prompt(query, retrieved_context, context)
        llm_response = self.llm.generate(
            prompt=prompt,
            temperature=self.temperature,
            system_prompt=self.get_system_prompt()
        )
        
        parsed_response = self._parse_llm_response(llm_response)
        
        return AgentResponse(
            agent_id=self.agent_id,
            agent_name=self.name,
            content=parsed_response["answer"],
            confidence=self._map_confidence(parsed_response["confidence"]),
            sources=retrieved_context,
            metadata={"chunks_retrieved": len(retrieved_context)},
            suggested_agents=parsed_response.get("suggests_consulting", [])
        )
    
    def _build_general_query_prompt(
        self,
        query: str,
        chunks: List[Dict],
        context: AgentContext
    ) -> str:
        """Build prompt for general queries"""
        # Format context
        context_text = self._format_context(chunks)
        
        # Format conversation history (last 3 messages)
        conversation_text = self._format_conversation_history(
            context.conversation_history[-3:]
        )
        
        return f"""Previous Conversation:
{conversation_text}

Relevant Requirements:
{context_text}

Current Query: {query}

Analyze the requirements and answer the query:
1. Provide clear, precise answer based on the requirements
2. Reference specific requirement IDs (e.g., [REQ-001])
3. Identify any gaps or ambiguities
4. Suggest if other document categories should be consulted

Return JSON format as specified."""
    
    def _format_context(self, chunks: List[Dict]) -> str:
        """Format retrieved chunks for prompt"""
        formatted = ""
        for i, chunk in enumerate(chunks, 1):
            meta = chunk.get("metadata", {})
            req_id = meta.get("requirement_id", "Unknown")
            priority = meta.get("priority", "unknown")
            status = meta.get("status", "unknown")
            
            formatted += f"""[Source {i}] {req_id} - {chunk['filename']}
Priority: {priority}, Status: {status}
{chunk['chunk_text']}

"""
        return formatted
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history"""
        if not history:
            return "No previous conversation."
        
        formatted = ""
        for msg in history:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            formatted += f"{role}: {content}\n"
        
        return formatted
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response with error handling"""
        try:
            # Try to extract JSON from response
            # Sometimes Llama 3.1 adds extra text before/after JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Fallback if no JSON found
                return {
                    "answer": response,
                    "confidence": "medium",
                    "key_sources": [],
                    "suggests_consulting": []
                }
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw response
            return {
                "answer": response,
                "confidence": "medium",
                "key_sources": [],
                "suggests_consulting": []
            }
    
    def _map_confidence(self, confidence_str: str) -> float:
        """Map confidence string to float"""
        confidence_map = {
            "high": 0.9,
            "medium": 0.6,
            "low": 0.3
        }
        return confidence_map.get(confidence_str.lower(), 0.5)


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

def test_requirements_agent():
    """Test the Requirements Agent with mock data"""
    
    print("=" * 60)
    print("REQUIREMENTS AGENT - TEST SUITE")
    print("=" * 60)
    
    # Initialize components
    data_platform = DataPlatformClient()
    requirements_category_id = 1  # Assume Requirements category has ID 1
    
    agent = RequirementsAgent(
        category_id=requirements_category_id,
        data_platform_client=data_platform
    )
    
    # Check Ollama health
    print("\n1. Checking Ollama connection...")
    if agent.llm.health_check():
        print("   ✅ Ollama is running and llama3.1:8b is available")
    else:
        print("   ⚠️  Ollama not running or model not available")
        print("   Run: ollama pull llama3.1:8b")
        return
    
    # Test context
    context = AgentContext(
        project_id=1,
        conversation_history=[],
        current_query=""
    )
    
    # Test 1: Can handle query
    print("\n2. Testing query relevance detection...")
    test_queries = [
        "What are the authentication requirements?",
        "Show me REQ-045",
        "Find requirements without design documentation",
        "What's the weather today?"  # Should score low
    ]
    
    for query in test_queries:
        score = agent.can_handle_query(query, context)
        print(f"   Query: '{query}'")
        print(f"   Score: {score:.2f} {'✅' if score > 0.5 else '❌'}")
    
    # Test 2: General query
    print("\n3. Testing general requirements query...")
    query = "What are the authentication requirements?"
    context.current_query = query
    
    response = agent.process_query(query, context)
    print(f"   Query: {query}")
    print(f"   Answer: {response.content[:200]}...")
    print(f"   Confidence: {response.confidence:.2f}")
    print(f"   Sources: {len(response.sources)} documents")
    
    # Test 3: Specific requirement
    print("\n4. Testing specific requirement query...")
    query = "Tell me about REQ-045"
    response = agent.process_query(query, context)
    print(f"   Query: {query}")
    print(f"   Answer: {response.content[:200]}...")
    print(f"   Confidence: {response.confidence:.2f}")
    
    # Test 4: Gap analysis
    print("\n5. Testing gap analysis...")
    query = "What high-priority requirements don't have design documentation?"
    response = agent.process_query(query, context)
    print(f"   Query: {query}")
    print(f"   Answer: {response.content[:200]}...")
    print(f"   Gaps found: {response.metadata.get('gap_count', 0)}")
    
    # Test 5: Traceability
    print("\n6. Testing traceability query...")
    query = "What components implement REQ-045?"
    response = agent.process_query(query, context)
    print(f"   Query: {query}")
    print(f"   Answer: {response.content[:200]}...")
    print(f"   Sources: {len(response.sources)} linked items")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    """
    To run this agent:
    
    1. Ensure Ollama is running:
       $ ollama serve
    
    2. Ensure llama3.1:8b model is downloaded:
       $ ollama pull llama3.1:8b
    
    3. Run this script:
       $ python requirements_agent.py
    
    Note: This uses mock data. Replace DataPlatformClient
    with actual Workstream 1 API client when ready.
    """
    test_requirements_agent()
