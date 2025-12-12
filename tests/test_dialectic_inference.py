"""
Unit tests for DialecticInference

Tests the dialectical reasoning engine implementing Zord Theory,
including thesis, antithesis, and synthesis generation.
"""
import pytest
from uatu_genesis_engine.agent_zero_integration.dialectic_inference import (
    DialecticInference,
    DialecticalThought,
    DialecticalChain,
    DialecticalStage,
    DialecticalPromptBuilder
)


@pytest.fixture
def sample_soul_anchor():
    """Sample soul anchor data for testing."""
    return {
        "primary_name": "Test Persona",
        "archetype": "technology",
        "core_constants": [
            "Innovation over tradition",
            "Ethical responsibility",
            "Pragmatic solutions"
        ],
        "core_drive": "Using technology to solve real-world problems"
    }


@pytest.fixture
def dialectic_engine(sample_soul_anchor):
    """Create a dialectic inference engine for testing."""
    return DialecticInference(soul_anchor_data=sample_soul_anchor)


class TestDialecticalThought:
    """Test the DialecticalThought dataclass."""
    
    def test_initialization(self):
        """Test dialectical thought initialization."""
        thought = DialecticalThought(
            stage=DialecticalStage.THESIS,
            content="Test content",
            reasoning="Test reasoning",
            confidence=0.9,
            bias_influence=0.0
        )
        
        assert thought.stage == DialecticalStage.THESIS
        assert thought.content == "Test content"
        assert thought.reasoning == "Test reasoning"
        assert thought.confidence == 0.9
        assert thought.bias_influence == 0.0
        assert thought.timestamp is not None


class TestDialecticalChain:
    """Test the DialecticalChain dataclass."""
    
    def test_initialization(self):
        """Test dialectical chain initialization."""
        thesis = DialecticalThought(
            stage=DialecticalStage.THESIS,
            content="Thesis content",
            confidence=0.9
        )
        antithesis = DialecticalThought(
            stage=DialecticalStage.ANTITHESIS,
            content="Antithesis content",
            confidence=0.8
        )
        synthesis = DialecticalThought(
            stage=DialecticalStage.SYNTHESIS,
            content="Synthesis content",
            confidence=0.95
        )
        
        chain = DialecticalChain(
            user_input="Test input",
            thesis=thesis,
            antithesis=antithesis,
            synthesis=synthesis,
            final_output="Final output"
        )
        
        assert chain.user_input == "Test input"
        assert chain.thesis.stage == DialecticalStage.THESIS
        assert chain.antithesis.stage == DialecticalStage.ANTITHESIS
        assert chain.synthesis.stage == DialecticalStage.SYNTHESIS
        assert chain.final_output == "Final output"
    
    def test_to_dict(self):
        """Test converting chain to dictionary."""
        thesis = DialecticalThought(
            stage=DialecticalStage.THESIS,
            content="Thesis",
            confidence=0.9
        )
        antithesis = DialecticalThought(
            stage=DialecticalStage.ANTITHESIS,
            content="Antithesis",
            confidence=0.8
        )
        synthesis = DialecticalThought(
            stage=DialecticalStage.SYNTHESIS,
            content="Synthesis",
            confidence=0.95
        )
        
        chain = DialecticalChain(
            user_input="Test",
            thesis=thesis,
            antithesis=antithesis,
            synthesis=synthesis,
            final_output="Output"
        )
        
        chain_dict = chain.to_dict()
        
        assert "user_input" in chain_dict
        assert "thesis" in chain_dict
        assert "antithesis" in chain_dict
        assert "synthesis" in chain_dict
        assert "final_output" in chain_dict
        assert chain_dict["thesis"]["stage"] == "thesis"
        assert chain_dict["antithesis"]["stage"] == "antithesis"
        assert chain_dict["synthesis"]["stage"] == "synthesis"


class TestDialecticInference:
    """Test the DialecticInference class."""
    
    def test_initialization(self, sample_soul_anchor):
        """Test engine initialization."""
        engine = DialecticInference(soul_anchor_data=sample_soul_anchor)
        
        assert engine.soul_anchor == sample_soul_anchor
        assert engine.archetype == "technology"
        assert len(engine.core_constants) == 3
        assert engine.core_drive == "Using technology to solve real-world problems"
    
    def test_initialization_empty_anchor(self):
        """Test initialization with no soul anchor."""
        engine = DialecticInference()
        
        assert engine.soul_anchor == {}
        assert engine.core_constants == []
        assert engine.core_drive == ""
    
    def test_generate_thesis(self, dialectic_engine):
        """Test thesis generation."""
        user_input = "What is the best approach to this problem?"
        
        thesis = dialectic_engine.generate_thesis(user_input)
        
        assert thesis.stage == DialecticalStage.THESIS
        assert thesis.content is not None
        assert thesis.bias_influence == 0.0  # Thesis should be unbiased
        assert thesis.confidence > 0
    
    def test_generate_antithesis(self, dialectic_engine):
        """Test antithesis generation."""
        user_input = "What is the best approach to this problem?"
        thesis = dialectic_engine.generate_thesis(user_input)
        
        antithesis = dialectic_engine.generate_antithesis(user_input, thesis)
        
        assert antithesis.stage == DialecticalStage.ANTITHESIS
        assert antithesis.content is not None
        assert antithesis.bias_influence == 1.0  # Antithesis should be fully biased
        assert antithesis.confidence > 0
    
    def test_generate_synthesis(self, dialectic_engine):
        """Test synthesis generation."""
        user_input = "What is the best approach to this problem?"
        thesis = dialectic_engine.generate_thesis(user_input)
        antithesis = dialectic_engine.generate_antithesis(user_input, thesis)
        
        synthesis = dialectic_engine.generate_synthesis(user_input, thesis, antithesis)
        
        assert synthesis.stage == DialecticalStage.SYNTHESIS
        assert synthesis.content is not None
        assert 0.0 < synthesis.bias_influence < 1.0  # Synthesis should be balanced
        assert synthesis.confidence > 0
    
    def test_generate_dialectical_thought(self, dialectic_engine):
        """Test complete dialectical thought generation."""
        user_input = "How should we approach this technical challenge?"
        
        chain = dialectic_engine.generate_dialectical_thought(user_input)
        
        assert isinstance(chain, DialecticalChain)
        assert chain.user_input == user_input
        assert chain.thesis.stage == DialecticalStage.THESIS
        assert chain.antithesis.stage == DialecticalStage.ANTITHESIS
        assert chain.synthesis.stage == DialecticalStage.SYNTHESIS
        assert chain.final_output is not None
    
    def test_dialectical_chain_logged(self, dialectic_engine):
        """Test that dialectical chains are logged to history."""
        user_input = "Test question"
        
        # Initially empty
        assert len(dialectic_engine.get_chain_history()) == 0
        
        # Generate a chain
        dialectic_engine.generate_dialectical_thought(user_input)
        
        # Should be logged
        assert len(dialectic_engine.get_chain_history()) == 1
    
    def test_get_latest_chain(self, dialectic_engine):
        """Test retrieving the latest chain."""
        # Initially None
        assert dialectic_engine.get_latest_chain() is None
        
        # Generate some chains
        dialectic_engine.generate_dialectical_thought("Question 1")
        dialectic_engine.generate_dialectical_thought("Question 2")
        
        latest = dialectic_engine.get_latest_chain()
        
        assert latest is not None
        assert latest.user_input == "Question 2"
    
    def test_clear_history(self, dialectic_engine):
        """Test clearing chain history."""
        # Generate some chains
        dialectic_engine.generate_dialectical_thought("Question 1")
        dialectic_engine.generate_dialectical_thought("Question 2")
        
        assert len(dialectic_engine.get_chain_history()) == 2
        
        # Clear history
        dialectic_engine.clear_history()
        
        assert len(dialectic_engine.get_chain_history()) == 0
    
    def test_export_chains_for_logging(self, dialectic_engine):
        """Test exporting chains for external logging."""
        # Generate some chains
        dialectic_engine.generate_dialectical_thought("Question 1")
        dialectic_engine.generate_dialectical_thought("Question 2")
        
        exported = dialectic_engine.export_chains_for_logging()
        
        assert len(exported) == 2
        assert all(isinstance(chain, dict) for chain in exported)
        assert all("user_input" in chain for chain in exported)
        assert all("thesis" in chain for chain in exported)
        assert all("antithesis" in chain for chain in exported)
        assert all("synthesis" in chain for chain in exported)
    
    def test_bias_triggers_extraction(self, dialectic_engine):
        """Test extracting bias triggers from soul anchor."""
        triggers = dialectic_engine._extract_bias_triggers()
        
        assert len(triggers) > 0
        assert "Innovation over tradition" in triggers
        assert "technology perspective" in triggers
    
    def test_bias_balance_calculation(self, dialectic_engine):
        """Test calculating bias balance."""
        thesis = DialecticalThought(
            stage=DialecticalStage.THESIS,
            content="Thesis",
            bias_influence=0.0
        )
        antithesis = DialecticalThought(
            stage=DialecticalStage.ANTITHESIS,
            content="Antithesis",
            bias_influence=1.0
        )
        
        balance = dialectic_engine._calculate_bias_balance(thesis, antithesis)
        
        # Should be between 0 and 1
        assert 0.0 <= balance <= 1.0
        # Should be closer to middle (balanced)
        assert 0.3 <= balance <= 0.7
    
    def test_logging_disabled(self, sample_soul_anchor):
        """Test that logging can be disabled."""
        engine = DialecticInference(
            soul_anchor_data=sample_soul_anchor,
            enable_logging=False
        )
        
        engine.generate_dialectical_thought("Test question")
        
        # Should not be logged
        assert len(engine.get_chain_history()) == 0


class TestDialecticalPromptBuilder:
    """Test the DialecticalPromptBuilder helper class."""
    
    def test_build_thesis_prompt(self):
        """Test building thesis prompt."""
        user_input = "What is the best approach?"
        
        prompt = DialecticalPromptBuilder.build_thesis_prompt(user_input)
        
        assert user_input in prompt
        assert "objective" in prompt.lower() or "helpful" in prompt.lower()
        assert "unbiased" in prompt.lower() or "factual" in prompt.lower()
    
    def test_build_antithesis_prompt(self, sample_soul_anchor):
        """Test building antithesis prompt."""
        user_input = "What is the best approach?"
        thesis = "You should do X, Y, and Z."
        
        prompt = DialecticalPromptBuilder.build_antithesis_prompt(
            user_input,
            thesis,
            sample_soul_anchor
        )
        
        assert user_input in prompt
        assert thesis in prompt
        assert "technology" in prompt  # archetype
        assert "Innovation over tradition" in prompt  # core constant
    
    def test_build_synthesis_prompt(self):
        """Test building synthesis prompt."""
        user_input = "What is the best approach?"
        thesis = "Objective response"
        antithesis = "Biased response"
        
        prompt = DialecticalPromptBuilder.build_synthesis_prompt(
            user_input,
            thesis,
            antithesis
        )
        
        assert user_input in prompt
        assert thesis in prompt
        assert antithesis in prompt
        assert "synthesize" in prompt.lower() or "reconcile" in prompt.lower()


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""
    
    def test_complete_reasoning_flow(self, dialectic_engine):
        """Test complete dialectical reasoning flow."""
        user_input = "Should we use cutting-edge technology or proven solutions?"
        
        # Generate complete chain
        chain = dialectic_engine.generate_dialectical_thought(user_input)
        
        # Verify chain structure
        assert chain.thesis.bias_influence == 0.0  # Objective
        assert chain.antithesis.bias_influence == 1.0  # Biased
        assert 0.0 < chain.synthesis.bias_influence < 1.0  # Balanced
        
        # Verify final output comes from synthesis
        assert chain.final_output == chain.synthesis.content
    
    def test_multiple_questions_chain_history(self, dialectic_engine):
        """Test handling multiple questions with chain history."""
        questions = [
            "What's the best programming language?",
            "How should we handle security?",
            "What about performance optimization?"
        ]
        
        for question in questions:
            dialectic_engine.generate_dialectical_thought(question)
        
        # Should have all three in history
        history = dialectic_engine.get_chain_history()
        assert len(history) == 3
        
        # Each should have complete chain
        for chain in history:
            assert chain.thesis is not None
            assert chain.antithesis is not None
            assert chain.synthesis is not None
    
    def test_bias_influence_progression(self, dialectic_engine):
        """Test that bias influence progresses correctly through stages."""
        chain = dialectic_engine.generate_dialectical_thought("Test question")
        
        # Thesis should have no bias
        assert chain.thesis.bias_influence == 0.0
        
        # Antithesis should have maximum bias
        assert chain.antithesis.bias_influence == 1.0
        
        # Synthesis should be somewhere in between
        assert chain.synthesis.bias_influence > chain.thesis.bias_influence
        assert chain.synthesis.bias_influence < chain.antithesis.bias_influence
    
    def test_export_and_reimport_chain(self, dialectic_engine):
        """Test exporting chain data for persistence."""
        # Generate a chain
        dialectic_engine.generate_dialectical_thought("Test question")
        
        # Export
        exported = dialectic_engine.export_chains_for_logging()
        
        # Verify structure is suitable for external storage
        assert isinstance(exported, list)
        assert len(exported) == 1
        
        chain_data = exported[0]
        assert "user_input" in chain_data
        assert "thesis" in chain_data
        assert "antithesis" in chain_data
        assert "synthesis" in chain_data
        assert "created_at" in chain_data
        
        # All nested data should be serializable
        import json
        json_str = json.dumps(chain_data)
        assert json_str is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
