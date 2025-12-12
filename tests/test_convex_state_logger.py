"""
Unit tests for ConvexStateLogger

Tests the asynchronous black box recorder for logging internal states
to Convex backend.
"""
import pytest
import asyncio
import json
from pathlib import Path
from uatu_genesis_engine.agent_zero_integration.convex_state_logger import (
    ConvexStateLogger,
    ConvexStateLoggerContext,
    StateLogEntry,
    LogLevel,
    get_convex_schema_export
)


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary directory for log backups."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return str(log_dir)


@pytest.fixture
def logger_instance(temp_log_dir):
    """Create a logger instance for testing (mock mode)."""
    return ConvexStateLogger(
        convex_url=None,  # Mock mode
        batch_size=3,
        flush_interval=0.5,
        enable_local_backup=True,
        local_backup_path=temp_log_dir
    )


class TestStateLogEntry:
    """Test the StateLogEntry dataclass."""
    
    def test_initialization(self):
        """Test entry initialization."""
        entry = StateLogEntry(
            entry_type="test",
            data={"key": "value"},
            metadata={"meta": "data"},
            level=LogLevel.INFO
        )
        
        assert entry.entry_type == "test"
        assert entry.data == {"key": "value"}
        assert entry.metadata == {"meta": "data"}
        assert entry.level == LogLevel.INFO
        assert entry.timestamp is not None
    
    def test_to_dict(self):
        """Test converting entry to dictionary."""
        entry = StateLogEntry(
            entry_type="test",
            data={"key": "value"}
        )
        
        entry_dict = entry.to_dict()
        
        assert "entry_type" in entry_dict
        assert "timestamp" in entry_dict
        assert "data" in entry_dict
        assert "metadata" in entry_dict
        assert "level" in entry_dict
        assert entry_dict["entry_type"] == "test"


class TestConvexStateLogger:
    """Test the ConvexStateLogger class."""
    
    def test_initialization_mock_mode(self, temp_log_dir):
        """Test initialization in mock mode."""
        logger_obj = ConvexStateLogger(
            convex_url=None,
            local_backup_path=temp_log_dir
        )
        
        assert logger_obj.mock_mode is True
        assert logger_obj.is_running is False
        assert logger_obj.total_logged == 0
    
    def test_initialization_real_mode(self):
        """Test initialization with Convex URL."""
        logger_obj = ConvexStateLogger(
            convex_url="https://api.convex.dev/test",
            api_key="test_key"
        )
        
        assert logger_obj.mock_mode is False
        assert logger_obj.convex_url == "https://api.convex.dev/test"
        assert logger_obj.api_key == "test_key"
    
    @pytest.mark.asyncio
    async def test_start_stop(self, logger_instance):
        """Test starting and stopping the logger."""
        assert logger_instance.is_running is False
        
        await logger_instance.start()
        assert logger_instance.is_running is True
        
        await logger_instance.stop()
        assert logger_instance.is_running is False
    
    @pytest.mark.asyncio
    async def test_log_neurotransmitter_state(self, logger_instance):
        """Test logging neurotransmitter state."""
        state = {
            "dopamine": 0.7,
            "serotonin": 0.6,
            "cortisol": 0.3
        }
        
        await logger_instance.log_neurotransmitter_state(state)
        
        assert logger_instance.total_logged == 1
        assert len(logger_instance.log_buffer) == 1
        assert logger_instance.log_buffer[0].entry_type == "neurotransmitter"
    
    @pytest.mark.asyncio
    async def test_log_dialectical_chain(self, logger_instance):
        """Test logging dialectical chain."""
        chain = {
            "user_input": "Test question",
            "thesis": {"content": "Thesis"},
            "antithesis": {"content": "Antithesis"},
            "synthesis": {"content": "Synthesis"}
        }
        
        await logger_instance.log_dialectical_chain(chain)
        
        assert logger_instance.total_logged == 1
        assert logger_instance.log_buffer[0].entry_type == "dialectical_chain"
    
    @pytest.mark.asyncio
    async def test_log_interaction(self, logger_instance):
        """Test logging user-agent interaction."""
        await logger_instance.log_interaction(
            user_input="Hello",
            agent_output="Hi there!",
            metadata={"latency_ms": 150}
        )
        
        assert logger_instance.total_logged == 1
        assert logger_instance.log_buffer[0].entry_type == "interaction"
        assert logger_instance.log_buffer[0].data["user_input"] == "Hello"
        assert logger_instance.log_buffer[0].data["agent_output"] == "Hi there!"
    
    @pytest.mark.asyncio
    async def test_log_emotional_event(self, logger_instance):
        """Test logging emotional event."""
        await logger_instance.log_emotional_event(
            event_type="positive_feedback",
            description="User praised the response",
            emotional_impact={
                "dopamine": 0.15,
                "serotonin": 0.1,
                "cortisol": -0.1
            }
        )
        
        assert logger_instance.total_logged == 1
        assert logger_instance.log_buffer[0].entry_type == "emotional_event"
    
    @pytest.mark.asyncio
    async def test_log_security_event(self, logger_instance):
        """Test logging security event."""
        await logger_instance.log_security_event(
            event_type="integrity_check",
            severity="critical",
            details={"file": "anchor.yaml", "status": "failed"}
        )
        
        assert logger_instance.total_logged == 1
        assert logger_instance.log_buffer[0].entry_type == "security_event"
        assert logger_instance.log_buffer[0].level == LogLevel.ERROR
    
    @pytest.mark.asyncio
    async def test_log_custom(self, logger_instance):
        """Test logging custom entry."""
        await logger_instance.log_custom(
            entry_type="custom_event",
            data={"custom": "data"},
            level=LogLevel.WARNING
        )
        
        assert logger_instance.total_logged == 1
        assert logger_instance.log_buffer[0].entry_type == "custom_event"
        assert logger_instance.log_buffer[0].level == LogLevel.WARNING
    
    @pytest.mark.asyncio
    async def test_auto_flush_on_batch_size(self, logger_instance):
        """Test that buffer auto-flushes when batch size is reached."""
        # Batch size is 3, so after 3 logs it should auto-flush
        await logger_instance.log_custom("test1", {"data": 1})
        await logger_instance.log_custom("test2", {"data": 2})
        await logger_instance.log_custom("test3", {"data": 3})
        
        # Give async task time to execute
        await asyncio.sleep(0.1)
        
        # Buffer should be empty after auto-flush
        assert len(logger_instance.log_buffer) == 0
        assert logger_instance.total_flushed >= 3
    
    @pytest.mark.asyncio
    async def test_manual_flush(self, logger_instance):
        """Test manual flush operation."""
        await logger_instance.log_custom("test", {"data": "test"})
        
        assert len(logger_instance.log_buffer) == 1
        
        await logger_instance.flush()
        
        assert len(logger_instance.log_buffer) == 0
        assert logger_instance.total_flushed == 1
    
    @pytest.mark.asyncio
    async def test_periodic_flush(self, temp_log_dir):
        """Test periodic background flushing."""
        logger_obj = ConvexStateLogger(
            convex_url=None,
            flush_interval=0.3,  # Short interval for testing
            enable_local_backup=True,
            local_backup_path=temp_log_dir
        )
        
        await logger_obj.start()
        
        # Add a log
        await logger_obj.log_custom("test", {"data": "test"})
        
        # Wait for periodic flush
        await asyncio.sleep(0.5)
        
        # Should have been flushed
        assert logger_obj.total_flushed >= 1
        
        await logger_obj.stop()
    
    @pytest.mark.asyncio
    async def test_local_backup_created(self, logger_instance):
        """Test that local backup files are created."""
        await logger_instance.log_custom("test", {"data": "test"})
        await logger_instance.flush()
        
        # Check if backup file was created
        backup_dir = Path(logger_instance.local_backup_path)
        backup_files = list(backup_dir.glob("state_log_*.json"))
        
        assert len(backup_files) > 0
        
        # Verify backup content
        with open(backup_files[0], 'r') as f:
            backup_data = json.load(f)
        
        assert "timestamp" in backup_data
        assert "count" in backup_data
        assert "entries" in backup_data
        assert backup_data["count"] == 1
    
    @pytest.mark.asyncio
    async def test_stop_flushes_remaining_logs(self, logger_instance):
        """Test that stop() flushes remaining logs."""
        await logger_instance.start()
        
        # Add logs
        await logger_instance.log_custom("test1", {"data": 1})
        await logger_instance.log_custom("test2", {"data": 2})
        
        # Stop should flush remaining
        await logger_instance.stop()
        
        assert len(logger_instance.log_buffer) == 0
        assert logger_instance.total_flushed >= 2
    
    def test_get_stats(self, logger_instance):
        """Test getting logger statistics."""
        stats = logger_instance.get_stats()
        
        assert "total_logged" in stats
        assert "total_flushed" in stats
        assert "buffer_size" in stats
        assert "is_running" in stats
        assert "mock_mode" in stats
        
        assert stats["mock_mode"] is True


class TestConvexStateLoggerContext:
    """Test the context manager for ConvexStateLogger."""
    
    @pytest.mark.asyncio
    async def test_context_manager(self, temp_log_dir):
        """Test using logger as context manager."""
        async with ConvexStateLoggerContext(
            convex_url=None,
            local_backup_path=temp_log_dir
        ) as logger_obj:
            # Logger should be running inside context
            assert logger_obj.is_running is True
            
            # Log something
            await logger_obj.log_custom("test", {"data": "test"})
            assert logger_obj.total_logged == 1
        
        # Logger should be stopped after context exit
        assert logger_obj.is_running is False


class TestConvexSchema:
    """Test Convex schema utilities."""
    
    def test_schema_export(self):
        """Test exporting Convex schema."""
        schema_json = get_convex_schema_export()
        
        assert schema_json is not None
        
        # Should be valid JSON
        schema = json.loads(schema_json)
        
        # Should contain expected tables
        assert "neurotransmitter_state" in schema
        assert "dialectical_chain" in schema
        assert "interaction" in schema
        assert "emotional_event" in schema
        assert "security_event" in schema


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_logging_workflow(self, temp_log_dir):
        """Test complete workflow with multiple log types."""
        async with ConvexStateLoggerContext(
            convex_url=None,
            batch_size=10,
            enable_local_backup=True,
            local_backup_path=temp_log_dir
        ) as logger_obj:
            # Log neurotransmitter state
            await logger_obj.log_neurotransmitter_state({
                "dopamine": 0.7,
                "serotonin": 0.6,
                "cortisol": 0.3
            })
            
            # Log dialectical chain
            await logger_obj.log_dialectical_chain({
                "user_input": "Test question",
                "thesis": {"content": "Thesis"},
                "antithesis": {"content": "Antithesis"},
                "synthesis": {"content": "Synthesis"}
            })
            
            # Log interaction
            await logger_obj.log_interaction(
                user_input="Hello",
                agent_output="Hi!"
            )
            
            # Log emotional event
            await logger_obj.log_emotional_event(
                event_type="positive_feedback",
                description="User praised response",
                emotional_impact={"dopamine": 0.1}
            )
            
            # All should be logged
            assert logger_obj.total_logged == 4
    
    @pytest.mark.asyncio
    async def test_high_volume_logging(self, temp_log_dir):
        """Test handling high volume of logs."""
        async with ConvexStateLoggerContext(
            convex_url=None,
            batch_size=5,
            enable_local_backup=True,
            local_backup_path=temp_log_dir
        ) as logger_obj:
            # Log many entries rapidly
            for i in range(20):
                await logger_obj.log_custom(f"test_{i}", {"index": i})
            
            # Give time for auto-flushes
            await asyncio.sleep(0.5)
            
            # All should be logged
            assert logger_obj.total_logged == 20
            
            # Most should be flushed (auto-flush on batch size)
            assert logger_obj.total_flushed >= 15
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, logger_instance):
        """Test that logger continues after errors."""
        # This would test recovery from network errors, etc.
        # In mock mode, we can just verify buffer handling
        
        await logger_instance.log_custom("test1", {"data": 1})
        await logger_instance.log_custom("test2", {"data": 2})
        
        # Even if flush "fails", entries should be preserved
        await logger_instance.flush()
        
        # Logger should still function
        await logger_instance.log_custom("test3", {"data": 3})
        assert logger_instance.total_logged == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
