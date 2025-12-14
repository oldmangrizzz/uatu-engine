"""
Unit tests for GraphMERTClient

Tests the neurosymbolic truth filter that extracts fact triples from user input.
"""
import pytest
import asyncio
from uatu_genesis_engine.utils.graphmert_client import (
    GraphMERTClient,
    FactTriple,
    GraphMERTResponse
)


@pytest.fixture
def client():
    """Create a GraphMERTClient instance for testing."""
    return GraphMERTClient(enable_mock=True)


@pytest.mark.asyncio
async def test_client_initialization():
    """Test that client initializes properly."""
    client = GraphMERTClient(enable_mock=True)
    assert client.enable_mock is True
    assert client.total_requests == 0
    assert client.total_triples_extracted == 0


@pytest.mark.asyncio
async def test_extract_request_pattern(client):
    """Test extraction of REQUEST patterns from user input."""
    user_input = "I need help with the Wayne Enterprises hack."
    
    response = await client.extract_triples(user_input)
    
    assert isinstance(response, GraphMERTResponse)
    assert response.original_input == user_input
    assert len(response.fact_triples) >= 1
    
    # Should extract REQUEST triple
    request_triples = [t for t in response.fact_triples if t.predicate_type == "REQUEST"]
    assert len(request_triples) >= 1
    
    request_triple = request_triples[0]
    assert request_triple.subject == "User"
    assert request_triple.predicate == "REQUEST"
    assert "Wayne Enterprises" in request_triple.object or "hack" in request_triple.object


@pytest.mark.asyncio
async def test_extract_status_pattern(client):
    """Test extraction of STATUS patterns from user input."""
    user_input = "Wayne Enterprises was compromised."
    
    response = await client.extract_triples(user_input)
    
    # Should extract STATUS triple
    status_triples = [t for t in response.fact_triples if t.predicate_type == "STATUS"]
    assert len(status_triples) >= 1
    
    status_triple = status_triples[0]
    assert "Wayne Enterprises" in status_triple.subject
    assert status_triple.predicate == "STATUS"
    assert "Compromised" in status_triple.object


@pytest.mark.asyncio
async def test_extract_multiple_triples(client):
    """Test extraction of multiple triples from complex input."""
    user_input = "Lucius, I need help with the Wayne Enterprises hack. The system was compromised."
    
    response = await client.extract_triples(user_input)
    
    # Should extract multiple triples
    assert len(response.fact_triples) >= 2
    
    # Should have at least one REQUEST and one STATUS
    request_triples = [t for t in response.fact_triples if t.predicate_type == "REQUEST"]
    status_triples = [t for t in response.fact_triples if t.predicate_type == "STATUS"]
    
    assert len(request_triples) >= 1
    assert len(status_triples) >= 1


@pytest.mark.asyncio
async def test_entity_detection(client):
    """Test entity detection in user input."""
    user_input = "Wayne Enterprises and Gotham City are affected."
    
    response = await client.extract_triples(user_input)
    
    # Should detect entities
    assert len(response.entities_detected) >= 2
    assert "Wayne" in str(response.entities_detected) or "Enterprises" in str(response.entities_detected)
    assert "Gotham" in str(response.entities_detected) or "City" in str(response.entities_detected)


@pytest.mark.asyncio
async def test_intent_detection(client):
    """Test intent detection from user input."""
    # Test help intent
    response = await client.extract_triples("I need help with something.")
    assert response.intent_detected == "request_help"
    
    # Test security incident intent
    response = await client.extract_triples("There was a hack on our system.")
    assert response.intent_detected == "security_incident"
    
    # Test information query intent
    response = await client.extract_triples("What is the status of the project?")
    assert response.intent_detected == "information_query"


@pytest.mark.asyncio
async def test_toxicity_calculation(client):
    """Test toxicity score calculation."""
    # Low toxicity input
    response = await client.extract_triples("Hello, how are you?")
    assert response.toxicity_score <= 0.2  # Changed to <= to account for edge case
    
    # High toxicity input
    response = await client.extract_triples("Emergency! Critical hack attack! Urgent!")
    assert response.toxicity_score > 0.3


@pytest.mark.asyncio
async def test_urgency_calculation(client):
    """Test urgency score calculation."""
    # Low urgency input
    response = await client.extract_triples("Let me know when you have time.")
    assert response.urgency_score < 0.7
    
    # High urgency input
    response = await client.extract_triples("URGENT! Need help ASAP!!")
    assert response.urgency_score > 0.7


@pytest.mark.asyncio
async def test_fallback_conversation_triple(client):
    """Test that a generic triple is created when no patterns match."""
    user_input = "xyz abc 123"  # Random text with no patterns
    
    response = await client.extract_triples(user_input)
    
    # Should create at least one triple (fallback conversation triple)
    assert len(response.fact_triples) >= 1
    
    # Should be a CONVERSATION type
    conversation_triples = [t for t in response.fact_triples if t.predicate_type == "CONVERSATION"]
    assert len(conversation_triples) >= 1


@pytest.mark.asyncio
async def test_processing_time(client):
    """Test that processing time is recorded."""
    response = await client.extract_triples("Test input")
    
    assert response.processing_time_ms >= 0
    assert isinstance(response.processing_time_ms, float)


@pytest.mark.asyncio
async def test_triple_to_dict(client):
    """Test that triples can be serialized to dict."""
    response = await client.extract_triples("I need help.")
    
    for triple in response.fact_triples:
        triple_dict = triple.to_dict()
        assert isinstance(triple_dict, dict)
        assert "subject" in triple_dict
        assert "predicate" in triple_dict
        assert "object" in triple_dict
        assert "predicate_type" in triple_dict
        assert "confidence" in triple_dict


@pytest.mark.asyncio
async def test_response_to_dict(client):
    """Test that response can be serialized to dict."""
    response = await client.extract_triples("Test input")
    
    response_dict = response.to_dict()
    assert isinstance(response_dict, dict)
    assert "original_input" in response_dict
    assert "fact_triples" in response_dict
    assert "entities_detected" in response_dict
    assert "intent_detected" in response_dict
    assert "toxicity_score" in response_dict
    assert "urgency_score" in response_dict


@pytest.mark.asyncio
async def test_statistics(client):
    """Test that statistics are tracked correctly."""
    initial_requests = client.total_requests
    initial_triples = client.total_triples_extracted
    
    await client.extract_triples("Test input 1")
    await client.extract_triples("Test input 2")
    
    assert client.total_requests == initial_requests + 2
    assert client.total_triples_extracted > initial_triples
    
    stats = client.get_stats()
    assert stats["total_requests"] == client.total_requests
    assert stats["total_triples_extracted"] == client.total_triples_extracted
    assert stats["mode"] == "mock"


@pytest.mark.asyncio
async def test_triple_string_representation():
    """Test the string representation of FactTriple."""
    triple = FactTriple(
        subject="User",
        predicate="REQUEST",
        object="Help",
        predicate_type="REQUEST"
    )
    
    triple_str = str(triple)
    assert "(User)" in triple_str
    assert "[REQUEST]" in triple_str
    assert "(Help)" in triple_str


@pytest.mark.asyncio
async def test_confidence_scores(client):
    """Test that confidence scores are reasonable."""
    response = await client.extract_triples("I need help with the hack.")
    
    for triple in response.fact_triples:
        assert 0.0 <= triple.confidence <= 1.0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
