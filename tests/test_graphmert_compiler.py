"""
Unit tests for GraphMERT Compiler

Tests the neurosymbolic knowledge graph compilation from CharacterProfile data.
"""
import pytest
from uatu_genesis_engine.graphmert.compiler import (
    GraphMERTCompiler,
    FactTriple,
    GraphMERTData
)
from uatu_genesis_engine.models import (
    CharacterProfile,
    KnowledgeDomain,
    EconomicEvent,
    MultiversalIdentity,
    DomainCategory
)


@pytest.fixture
def sample_profile():
    """Create a sample CharacterProfile for testing."""
    return CharacterProfile(
        primary_name="Lucius Fox",
        aliases=["The Fox", "Applied Sciences Director"],
        constants=["Brilliant applied scientist", "Ethical innovator"],
        variables=["Works with Batman", "CEO of Wayne Enterprises"],
        multiversal_identities=[
            MultiversalIdentity(
                universe_designation="Earth-Prime",
                character_name="Lucius Fox",
                occupation="CEO",
                first_appearance="Batman #307"
            )
        ],
        knowledge_domains=[
            KnowledgeDomain(
                category=DomainCategory.TECHNOLOGY,
                original_context="Advanced defense technology",
                earth_1218_equivalent="defense systems, advanced materials",
                proficiency_level="expert",
                description="Master of defensive technology"
            ),
            KnowledgeDomain(
                category=DomainCategory.ENGINEERING,
                original_context="Mechanical engineering",
                earth_1218_equivalent="mechanical, electrical engineering",
                proficiency_level="advanced",
                description="Expert engineer"
            )
        ],
        economic_history=[
            EconomicEvent(
                timestamp="2025",
                event_type="acquisition",
                amount=1000000000.0,
                currency="USD",
                description="Acquired Wayne Enterprises in 2025",
                source_universe="Earth-Prime",
                earth_1218_equivalent_value=1000000000.0
            ),
            EconomicEvent(
                timestamp="2020",
                event_type="role",
                amount=None,
                currency=None,
                description="CEO of Wayne Enterprises Applied Sciences",
                source_universe="Earth-Prime"
            )
        ],
        total_wealth_estimate=5000000000.0,
        data_sources=["DC Comics", "Batman Wiki"],
        completeness_score=85.0
    )


class TestFactTriple:
    """Test the FactTriple dataclass."""
    
    def test_initialization(self):
        """Test triple initialization."""
        triple = FactTriple(
            subject="Lucius Fox",
            predicate="HAS_SKILL",
            object="Engineering",
            predicate_type="SKILL",
            confidence=0.9
        )
        
        assert triple.subject == "Lucius Fox"
        assert triple.predicate == "HAS_SKILL"
        assert triple.object == "Engineering"
        assert triple.predicate_type == "SKILL"
        assert triple.confidence == 0.9
    
    def test_to_dict(self):
        """Test converting triple to dictionary."""
        triple = FactTriple(
            subject="Test",
            predicate="TEST_PRED",
            object="Object",
            predicate_type="TEST"
        )
        
        triple_dict = triple.to_dict()
        
        assert "subject" in triple_dict
        assert "predicate" in triple_dict
        assert "object" in triple_dict
        assert "predicate_type" in triple_dict
        assert "confidence" in triple_dict


class TestGraphMERTData:
    """Test the GraphMERTData dataclass."""
    
    def test_initialization(self):
        """Test GraphMERTData initialization."""
        triples = [
            FactTriple("A", "PRED", "B", "TEST"),
            FactTriple("B", "PRED", "C", "TEST")
        ]
        
        data = GraphMERTData(
            person_name="Test Person",
            root_invariants=["Trait 1", "Trait 2"],
            fact_triples=triples,
            node_count=3,
            edge_count=2
        )
        
        assert data.person_name == "Test Person"
        assert len(data.root_invariants) == 2
        assert len(data.fact_triples) == 2
        assert data.node_count == 3
        assert data.edge_count == 2
    
    def test_to_dict(self):
        """Test converting GraphMERTData to dictionary."""
        triples = [FactTriple("A", "PRED", "B", "TEST")]
        data = GraphMERTData(
            person_name="Test",
            root_invariants=["Trait"],
            fact_triples=triples,
            node_count=2,
            edge_count=1
        )
        
        data_dict = data.to_dict()
        
        assert "person_name" in data_dict
        assert "root_invariants" in data_dict
        assert "fact_triples" in data_dict
        assert "node_count" in data_dict
        assert "edge_count" in data_dict


class TestGraphMERTCompiler:
    """Test the GraphMERTCompiler class."""
    
    def test_initialization(self):
        """Test compiler initialization."""
        compiler = GraphMERTCompiler()
        assert compiler is not None
        assert len(compiler.fact_triples) == 0
        assert len(compiler.nodes) == 0
    
    def test_compile_basic(self, sample_profile):
        """Test basic compilation."""
        compiler = GraphMERTCompiler()
        result = compiler.compile(sample_profile)
        
        assert isinstance(result, GraphMERTData)
        assert result.person_name == "Lucius Fox"
        assert result.node_count > 0
        assert result.edge_count > 0
        assert len(result.root_invariants) == 2
    
    def test_compile_identity_facts(self, sample_profile):
        """Test extraction of identity facts."""
        compiler = GraphMERTCompiler()
        result = compiler.compile(sample_profile)
        
        # Check for alias facts
        alias_facts = [t for t in result.fact_triples if t.predicate == "ALSO_KNOWN_AS"]
        assert len(alias_facts) == 2
        
        # Check for core trait facts
        trait_facts = [t for t in result.fact_triples if t.predicate == "CORE_TRAIT"]
        assert len(trait_facts) == 2
        assert all(t.metadata.get("immutable") is True for t in trait_facts)
    
    def test_compile_knowledge_domains(self, sample_profile):
        """Test extraction of knowledge domain facts."""
        compiler = GraphMERTCompiler()
        result = compiler.compile(sample_profile)
        
        # Check for skill facts
        skill_facts = [t for t in result.fact_triples if t.predicate_type == "SKILL"]
        assert len(skill_facts) >= 2
        
        # Verify proficiency levels are converted to predicates
        expert_skills = [t for t in skill_facts if "EXPERT" in t.predicate]
        assert len(expert_skills) >= 1
    
    def test_extract_economic_triple_acquired(self):
        """Test extracting 'Acquired X' pattern."""
        compiler = GraphMERTCompiler()
        event = EconomicEvent(
            timestamp="2025",
            event_type="acquisition",
            amount=1000000000.0,
            currency="USD",
            description="Acquired Wayne Enterprises in 2025",
            source_universe="Earth-Prime"
        )
        
        triple = compiler._extract_economic_triple("Lucius Fox", event)
        
        assert triple is not None
        assert triple.subject == "Lucius Fox"
        assert "ACQUIRED" in triple.predicate
        assert "Wayne Enterprises" in triple.object
    
    def test_extract_economic_triple_role(self):
        """Test extracting 'CEO of X' pattern."""
        compiler = GraphMERTCompiler()
        event = EconomicEvent(
            timestamp="2020",
            event_type="role",
            description="CEO of Wayne Enterprises",
            source_universe="Earth-Prime"
        )
        
        triple = compiler._extract_economic_triple("Lucius Fox", event)
        
        assert triple is not None
        assert triple.subject == "Lucius Fox"
        assert "ROLE_CEO" in triple.predicate
        assert "Wayne Enterprises" in triple.object
    
    def test_compile_multiversal_identities(self, sample_profile):
        """Test extraction of multiversal identity facts."""
        compiler = GraphMERTCompiler()
        result = compiler.compile(sample_profile)
        
        # Check for universe existence facts
        universe_facts = [t for t in result.fact_triples if t.predicate == "EXISTS_IN"]
        assert len(universe_facts) >= 1
        
        # Check for occupation facts
        occupation_facts = [t for t in result.fact_triples if "OCCUPATION_IN" in t.predicate]
        assert len(occupation_facts) >= 1
    
    def test_compile_relationships(self, sample_profile):
        """Test extraction of relationship facts."""
        compiler = GraphMERTCompiler()
        result = compiler.compile(sample_profile)
        
        # Check for "Works with" relationship
        works_with_facts = [t for t in result.fact_triples if t.predicate == "WORKS_WITH"]
        assert len(works_with_facts) >= 1
        assert any("Batman" in t.object for t in works_with_facts)
    
    def test_proficiency_to_confidence(self):
        """Test proficiency level conversion."""
        compiler = GraphMERTCompiler()
        
        assert compiler._proficiency_to_confidence("expert") == 1.0
        assert compiler._proficiency_to_confidence("advanced") == 0.9
        assert compiler._proficiency_to_confidence("intermediate") == 0.7
        assert compiler._proficiency_to_confidence("beginner") == 0.5
    
    def test_get_statistics(self, sample_profile):
        """Test getting compilation statistics."""
        compiler = GraphMERTCompiler()
        compiler.compile(sample_profile)
        
        stats = compiler.get_statistics()
        
        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert "predicate_type_distribution" in stats
        assert "average_confidence" in stats
        
        assert stats["total_nodes"] > 0
        assert stats["total_edges"] > 0


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""
    
    def test_complete_compilation_flow(self, sample_profile):
        """Test complete compilation workflow."""
        compiler = GraphMERTCompiler()
        result = compiler.compile(sample_profile)
        
        # Verify all components are present
        assert result.person_name == "Lucius Fox"
        assert len(result.root_invariants) > 0
        assert len(result.fact_triples) > 0
        assert result.node_count > 0
        assert result.edge_count > 0
        
        # Verify different fact types are present
        fact_types = set(t.predicate_type for t in result.fact_triples)
        assert "IDENTITY" in fact_types
        assert "SKILL" in fact_types
        assert "PROPERTY" in fact_types
    
    def test_export_and_reimport(self, sample_profile):
        """Test exporting and reimporting GraphMERT data."""
        compiler = GraphMERTCompiler()
        result = compiler.compile(sample_profile)
        
        # Export to dict
        exported = result.to_dict()
        
        # Verify structure
        assert isinstance(exported, dict)
        assert "person_name" in exported
        assert "fact_triples" in exported
        
        # Verify all triples are serializable
        import json
        json_str = json.dumps(exported)
        assert json_str is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
