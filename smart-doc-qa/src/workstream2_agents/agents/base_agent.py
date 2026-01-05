"""
Base agent class that all specialized agents inherit from
"""
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.data_models import (
    AgentContext, AgentResponse, ConfidenceLevel, Source
)
from utils.ollama_client import ollama_client, OllamaException
from config.settings import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        category_id: int,
        llm_model: str = None,
        temperature: float = 0.1
    ):
        self.agent_id = agent_id
        self.name = name
        self.category_id = category_id
        self.llm_model = llm_model or settings.OLLAMA_MODEL
        self.temperature = temperature
        
        # Use global Ollama client
        self.llm_client = ollama_client
        
        logger.info(f"Initialized {self.name} (ID: {self.agent_id})")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Define agent's personality and expertise
        Must be implemented by each specialized agent
        """
        pass
    
    @abstractmethod
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        """
        Determine if this agent should handle the query
        
        Args:
            query: User query
            context: Agent context
            
        Returns:
            Confidence score 0.0-1.0
        """
        pass
    
    def retrieve_context(
        self,
        query: str,
        context: AgentContext,
        top_k: int = 5
    ) -> List[Source]:
        """
        Retrieve relevant documents from this agent's category
        
        NOTE: This is a placeholder. Will be integrated with Workstream 1
        retrieval system later.
        
        Args:
            query: User query
            context: Agent context
            top_k: Number of results to retrieve
            
        Returns:
            List of Source objects
        """
        # TODO: Integrate with actual retrieval system from Workstream 1
        logger.warning(f"{self.name}: Using mock retrieval (integration pending)")
        
        # Mock sources for now
        return [
            Source(
                chunk_id=1,
                document_id=1,
                filename=f"mock_doc_{self.category_id}.pdf",
                category_name=self.name,
                chunk_text=f"Mock content related to: {query}",
                page_number=1,
                metadata={},
                similarity_score=0.85
            )
        ]
    
    def process_query(
        self,
        query: str,
        context: AgentContext,
        retrieved_context: Optional[List[Source]] = None
    ) -> AgentResponse:
        """
        Main processing logic for the agent
        
        Args:
            query: User query
            context: Agent context
            retrieved_context: Pre-retrieved context (optional)
            
        Returns:
            AgentResponse with answer and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Retrieve context if not provided
            if retrieved_context is None:
                logger.info(f"{self.name}: Retrieving context for query")
                retrieved_context = self.retrieve_context(query, context)
            
            # Step 2: Build prompt
            prompt = self._build_prompt(query, retrieved_context, context)
            
            # Step 3: Generate response
            logger.info(f"{self.name}: Generating response")
            response_text = self._call_llm(prompt, context)
            
            # Step 4: Parse and structure response
            response = self._parse_response(response_text, retrieved_context)
            
            # Add processing time
            response.processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"{self.name}: Response generated ({response.processing_time_ms}ms)")
            
            return response
            
        except Exception as e:
            logger.error(f"{self.name}: Error processing query: {e}")
            # Return error response
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content=f"Error: {str(e)}",
                confidence=ConfidenceLevel.LOW,
                sources=[],
                metadata={"error": str(e)},
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def _build_prompt(
        self,
        query: str,
        retrieved_context: List[Source],
        context: AgentContext
    ) -> str:
        """Build the prompt for LLM"""
        system_prompt = self.get_system_prompt()
        context_text = self._format_context(retrieved_context)
        conversation_text = self._format_conversation_history(
            context.conversation_history
        )
        
        prompt = f"""{system_prompt}

CONVERSATION HISTORY:
{conversation_text}

RELEVANT CONTEXT FROM {self.name.upper()}:
{context_text}

CURRENT QUERY: {query}

Please provide a response that:
1. Answers the query using the context provided
2. Cites specific sources with [Source N] notation
3. Indicates your confidence level (high/medium/low)
4. Suggests if other document categories should be consulted
5. Returns response in JSON format:
{{
    "answer": "your detailed answer with [Source N] citations",
    "confidence": "high|medium|low",
    "key_sources": ["brief description of key sources"],
    "suggests_consulting": ["agent_name1", "agent_name2"],
    "reasoning": "why you're suggesting other agents if any"
}}

IMPORTANT: Return ONLY valid JSON, no other text.

RESPONSE:"""
        
        return prompt
    
    def _format_context(self, sources: List[Source]) -> str:
        """Format retrieved sources for prompt"""
        if not sources:
            return "No relevant context found."
        
        formatted = ""
        for i, source in enumerate(sources, 1):
            formatted += f"""
[Source {i}] - {source.filename} (Page {source.page_number or 'N/A'})
{source.chunk_text}
Metadata: {json.dumps(source.metadata, indent=2) if source.metadata else 'None'}
---
"""
        return formatted
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history"""
        if not history:
            return "No previous conversation."
        
        formatted = ""
        # Only last 5 messages to keep prompt size manageable
        for msg in history[-5:]:
            role = msg.get('role', 'user').upper()
            content = msg.get('content', '')
            formatted += f"{role}: {content}\n"
        
        return formatted
    
    def _call_llm(self, prompt: str, context: AgentContext) -> str:
        """
        Call LLM with prompt
        
        Args:
            prompt: Full prompt
            context: Agent context
            
        Returns:
            Generated text
        """
        try:
            response = self.llm_client.generate(
                prompt=prompt,
                temperature=self.temperature
            )
            return response
        except OllamaException as e:
            logger.error(f"{self.name}: LLM call failed: {e}")
            raise
    
    def _parse_response(
        self,
        llm_response: str,
        retrieved_context: List[Source]
    ) -> AgentResponse:
        """Parse LLM response into structured format"""
        try:
            # Clean response (remove markdown code blocks if present)
            cleaned = llm_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            
            # Map confidence string to enum
            confidence_str = parsed.get("confidence", "medium").lower()
            confidence_map = {
                "high": ConfidenceLevel.HIGH,
                "medium": ConfidenceLevel.MEDIUM,
                "low": ConfidenceLevel.LOW
            }
            confidence = confidence_map.get(confidence_str, ConfidenceLevel.MEDIUM)
            
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content=parsed.get("answer", ""),
                confidence=confidence,
                sources=retrieved_context,
                metadata={
                    "key_sources": parsed.get("key_sources", []),
                    "reasoning": parsed.get("reasoning", "")
                },
                suggested_agents=parsed.get("suggests_consulting", [])
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"{self.name}: Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {llm_response[:200]}")
            
            # Fallback: return raw response
            return AgentResponse(
                agent_id=self.agent_id,
                agent_name=self.name,
                content=llm_response,
                confidence=ConfidenceLevel.LOW,
                sources=retrieved_context,
                metadata={"parse_error": str(e)}
            )
    
    def _calculate_keyword_score(self, query: str, keywords: List[str]) -> float:
        """
        Helper method to calculate relevance score based on keywords
        
        Args:
            query: User query
            keywords: List of keywords to check
            
        Returns:
            Score between 0.0 and 1.0
        """
        query_lower = query.lower()
        matches = sum(1 for kw in keywords if kw.lower() in query_lower)
        
        if matches == 0:
            return 0.0
        
        # Score increases with matches but caps at 1.0
        return min(0.3 + (matches * 0.15), 1.0)
    