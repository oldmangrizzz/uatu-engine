"""
Unit tests for ConvexSeeder

Tests the seeding of GraphMERT data to Convex database.
"""
import pytest
import json
from pathlib import Path
from uatu_genesis_engine.utils.convex_seeder import (
    ConvexSeeder,
    get_convex_graphmert_schema
)
from uatu_genesis_engine.graphmert.compiler import (
    GraphMERTData,
    FactTriple
)


@pytest.fixture
def sample_graphmert_data():
    """Create sample GraphMERT data for testing."""
    triples = [
        FactTriple(
            subject="Lucius Fox",
            predicate="CORE_TRAIT",
            object="Brilliant applied scientist",
            predicate_type="PROPERTY",
            confidence=1.0,
            metadata={"immutable": True}
        ),
        FactTriple(
            subject="Lucius Fox",
            predicate="HAS_SKILL_EXPERT",
            object="defense systems",
            predicate_type="SKILL",
            confidence=1.0
        ),
        FactTriple(
            subject="Lucius Fox",
            predicate="ACQUIRED_2025",
            object="Wayne Enterprises",
            predicate_type="EVENT",
            confidence=0.9
        )
    ]
    
    return GraphMERTData(
        person_name="Lucius Fox",
        root_invariants=["Brilliant applied scientist", "Ethical innovator"],
        fact_triples=triples,
        node_count=5,
        edge_count=3,
        metadata={"test": "data"}
    )


class TestConvexSeeder:
    """Test the ConvexSeeder class."""
    
    def test_initialization_mock_mode(self):
        """Test initialization in mock mode."""
        seeder = ConvexSeeder(mock_mode=True)
        
        assert seeder.mock_mode is True
        assert seeder.convex_url is None
    
    def test_initialization_real_mode(self):
        """Test initialization with Convex URL."""
        seeder = ConvexSeeder(
            convex_url="https://api.convex.dev/test",
            api_key="test_key",
            mock_mode=False
        )
        
        assert seeder.mock_mode is False
        assert seeder.convex_url == "https://api.convex.dev/test"
        assert seeder.api_key == "test_key"
    
    @pytest.mark.asyncio
    async def test_seed_mind_mock_mode(self, sample_graphmert_data, tmp_path):
        """Test seeding in mock mode."""
        seeder = ConvexSeeder(mock_mode=True)
        
        result = await seeder.seed_mind(sample_graphmert_data)
        
        assert result["person_name"] == "Lucius Fox"
        assert result["nodes_seeded"] == 5
        assert result["facts_seeded"] == 3
        assert result["root_invariants_count"] == 2
        assert result["mock_mode"] is True
        assert "backup_file" in result
    
    @pytest.mark.asyncio
    async def test_seed_mind_validates_invariants(self, sample_graphmert_data):
        """Test that seeding validates root invariants."""
        seeder = ConvexSeeder(mock_mode=True)
        
        # Should not raise exception
        result = await seeder.seed_mind(sample_graphmert_data, validate_invariants=True)
        
        assert result is not None
    
    def test_validate_root_invariants(self, sample_graphmert_data):
        """Test root invariant validation."""
        seeder = ConvexSeeder(mock_mode=True)
        
        # Should not raise exception for valid data
        seeder._validate_root_invariants(sample_graphmert_data)
    
    def test_prepare_payload(self, sample_graphmert_data):
        """Test payload preparation."""
        seeder = ConvexSeeder(mock_mode=True)
        
        payload = seeder._prepare_payload(sample_graphmert_data)
        
        assert "person_name" in payload
        assert "root_invariants" in payload
        assert "fact_triples" in payload
        assert "node_count" in payload
        assert "edge_count" in payload
        assert "seeded_at" in payload
        
        assert payload["person_name"] == "Lucius Fox"
        assert len(payload["root_invariants"]) == 2
        assert len(payload["fact_triples"]) == 3
    
    @pytest.mark.asyncio
    async def test_mock_seed_creates_backup(self, sample_graphmert_data):
        """Test that mock seed creates local backup file."""
        seeder = ConvexSeeder(mock_mode=True)
        payload = seeder._prepare_payload(sample_graphmert_data)
        
        result = await seeder._mock_seed(payload)
        
        assert "backup_file" in result
        backup_file = Path(result["backup_file"])
        assert backup_file.exists()
        
        # Verify backup content
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        assert backup_data["person_name"] == "Lucius Fox"
        assert len(backup_data["fact_triples"]) == 3


class TestConvexSchema:
    """Test Convex schema utilities."""
    
    def test_schema_export(self):
        """Test exporting Convex schema."""
        schema_json = get_convex_graphmert_schema()
        
        assert schema_json is not None
        
        # Should be valid JSON
        schema = json.loads(schema_json)
        
        # Should contain expected tables
        assert "minds" in schema
        assert "fact_triples" in schema
        
        # Verify minds table structure
        assert "fields" in schema["minds"]
        assert "person_name" in schema["minds"]["fields"]
        assert "root_invariants" in schema["minds"]["fields"]
        
        # Verify fact_triples table structure
        assert "fields" in schema["fact_triples"]
        assert "subject" in schema["fact_triples"]["fields"]
        assert "predicate" in schema["fact_triples"]["fields"]
        assert "object" in schema["fact_triples"]["fields"]


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_seeding_workflow(self, sample_graphmert_data):
        """Test complete seeding workflow."""
        seeder = ConvexSeeder(mock_mode=True)
        
        result = await seeder.seed_mind(sample_graphmert_data)
        
        # Verify all expected fields
        assert result["person_name"] == "Lucius Fox"
        assert result["nodes_seeded"] == 5
        assert result["facts_seeded"] == 3
        assert result["root_invariants_count"] == 2
        
        # Verify backup was created
        assert Path(result["backup_file"]).exists()
    
    @pytest.mark.asyncio
    async def test_verify_seed_mock_mode(self):
        """Test verification in mock mode."""
        seeder = ConvexSeeder(mock_mode=True)
        
        result = await seeder.verify_seed("Test Person")
        
        assert result["verified"] is False
        assert result["mock_mode"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
