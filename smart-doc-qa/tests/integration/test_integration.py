# tests/test_integration.py

import sys
from pathlib import Path

# Add project root to Python path if not already present
# This allows imports to work regardless of where the script is run from
_project_root = Path(__file__).parent.parent.parent
print(f"Project root: {_project_root}")
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.data_platform.api.client import DataPlatformClient
from src.workstream2_agents.agents.requirements_agent import RequirementsAgent
from src.workstream2_agents.agents.base_agent import AgentContext
from src.data_platform.retrieval.search_similarity import search_pgvector
from src.data_platform.storage.document_repo import getdocument_by_id

def test_requirements_agent_integration():
    # Below logic is not yet implemented in the data platform client
    # Initialize client
    client = DataPlatformClient()

    # Test retrieval
    chunks = client.retrieve_requirements_by_query(
        query="What are the authentication requirements?",
        project_id=1,
        top_k=5
    )

    print(f"Found {len(chunks)} chunks")
    for chunk in chunks:
        print(f"- {chunk['metadata'].get('requirement_id')}: {chunk['chunk_text'][:100]}...")

    search_query = "What is Retrieval Augmented Generation?"

    # search query is used to retrieve the chunks from the PGVector database
    # this method is working fine and returns the chunks with similarity score
    print("++++++++++++++++++++✅ Search 2 started.++++++++++++++++++++")
    print(f"Searching for: {search_query}")
    hits = search_pgvector(search_query, top_k=5, min_similarity=0.5)
    for row in hits:
        document = getdocument_by_id(row['document_id'])
        print(f"[{row['similarity']:.4f}] \n Document: {document['filename']}\nchunk: {row['chunk_text']}\n")
        print("---------------**********************************************************************---------------")
    print("++++++++++++++++++++✅ Search 2 completed.++++++++++++++++++++")

    # Test with agent
    agent = RequirementsAgent(category_id=1)
    context = AgentContext(
        project_id=1,
        conversation_history=[],
        current_query=search_query
    )

    response = agent.process_query(
        query=search_query,
        context=context
    )

    print(f"\nAgent Response:")
    print(f"Confidence: {response.confidence}")
    print(f"Answer: {response.content[:200]}...")
    print(f"Sources: {len(response.sources)} documents")
#    print(f"Sources: {response.sources}")
    print(f"Metadata: {response.metadata}")
    print(f"Requires Followup: {response.requires_followup}")
    print(f"Suggested Agents: {response.suggested_agents}")
#    print(f"Processing Time: {response.processing_time_ms} ms")

if __name__ == "__main__":
    test_requirements_agent_integration()
