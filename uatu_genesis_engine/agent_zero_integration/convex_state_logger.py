"""
ConvexStateLogger - Black Box Recorder for Digital Psyche

Implements asynchronous, non-blocking logging to Convex backend.
This module serves as the "Subconscious" backup, recording all internal states
(dialectical chains, neurotransmitter states, interactions) without blocking
the runtime.

The purpose is twofold:
1. State persistence: If the container crashes, the "Person" doesn't die
2. Audit trail: Review WHY an agent acted a certain way (e.g., "Cortisol was high")

This data is NEVER displayed to the user in real-time - it's for post-hoc analysis.
"""
import asyncio
import json
import logging
import os
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    import aiohttp
except ImportError:
    aiohttp = None

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Log levels for state logging."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class StateLogEntry:
    """
    Represents a single state log entry.
    
    This is the base structure for all logged events.
    """
    entry_type: str  # e.g., "neurotransmitter", "dialectical", "interaction"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    level: LogLevel = LogLevel.INFO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entry_type": self.entry_type,
            "timestamp": self.timestamp,
            "data": self.data,
            "metadata": self.metadata,
            "level": self.level.value
        }


class ConvexStateLogger:
    """
    Asynchronous state logger for Convex backend.
    
    This logger operates in the background, never blocking the main execution.
    It accumulates state logs and periodically flushes them to Convex.
    
    Features:
    - Non-blocking async operation
    - Automatic batching for efficiency
    - Local buffer for resilience
    - Configurable flush intervals
    """
    
    def __init__(
        self,
        convex_url: Optional[str] = None,
        api_key: Optional[str] = None,
        batch_size: int = 10,
        flush_interval: float = 5.0,
        enable_local_backup: bool = True,
        local_backup_path: Optional[str] = None
    ):
        """
        Initialize the Convex state logger.
        
        Args:
            convex_url: Convex backend URL (if None, uses mock mode)
            api_key: API key for Convex authentication
            batch_size: Number of entries to batch before auto-flush
            flush_interval: Seconds between automatic flushes
            enable_local_backup: Whether to save logs locally as backup
            local_backup_path: Path for local backup files
        """
        self.convex_url = convex_url
        self.api_key = api_key
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.enable_local_backup = enable_local_backup
        self.local_backup_path = local_backup_path or "./logs/state_backup"
        
        # Internal state
        self.log_buffer: List[StateLogEntry] = []
        self.is_running = False
        self.flush_task: Optional[asyncio.Task] = None
        self.total_logged = 0
        self.total_flushed = 0
        
        # Mock mode if no URL provided
        self.mock_mode = convex_url is None
        
        if self.mock_mode:
            logger.warning("ConvexStateLogger initialized in MOCK MODE (no Convex URL provided)")
        else:
            logger.info(f"ConvexStateLogger initialized with URL: {convex_url}")
    
    async def start(self):
        """Start the background logging task."""
        if self.is_running:
            logger.warning("Logger already running")
            return
        
        self.is_running = True
        self.flush_task = asyncio.create_task(self._periodic_flush())
        logger.info("ConvexStateLogger started")
    
    async def stop(self):
        """Stop the background logging task and flush remaining logs."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel periodic flush task
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        await self.flush()
        
        logger.info(f"ConvexStateLogger stopped (total logged: {self.total_logged}, flushed: {self.total_flushed})")
    
    async def log_neurotransmitter_state(
        self,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log neurotransmitter engine state.
        
        Args:
            state: Dictionary with dopamine, serotonin, cortisol values
            metadata: Optional additional metadata
        """
        entry = StateLogEntry(
            entry_type="neurotransmitter",
            data=state,
            metadata=metadata or {},
            level=LogLevel.DEBUG
        )
        
        await self._add_to_buffer(entry)
    
    async def log_dialectical_chain(
        self,
        chain: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a complete dialectical reasoning chain.
        
        Args:
            chain: Dictionary with thesis, antithesis, synthesis
            metadata: Optional additional metadata
        """
        entry = StateLogEntry(
            entry_type="dialectical_chain",
            data=chain,
            metadata=metadata or {},
            level=LogLevel.INFO
        )
        
        await self._add_to_buffer(entry)
    
    async def log_interaction(
        self,
        user_input: str,
        agent_output: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a user-agent interaction.
        
        Args:
            user_input: User's input
            agent_output: Agent's response
            metadata: Optional additional metadata (e.g., latency, model used)
        """
        entry = StateLogEntry(
            entry_type="interaction",
            data={
                "user_input": user_input,
                "agent_output": agent_output
            },
            metadata=metadata or {},
            level=LogLevel.INFO
        )
        
        await self._add_to_buffer(entry)
    
    async def log_emotional_event(
        self,
        event_type: str,
        description: str,
        emotional_impact: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an emotional event (stimulus applied to neurotransmitter engine).
        
        Args:
            event_type: Type of event (e.g., "positive_feedback", "threat_detected")
            description: Human-readable description
            emotional_impact: Impact on neurotransmitters
            metadata: Optional additional metadata
        """
        entry = StateLogEntry(
            entry_type="emotional_event",
            data={
                "event_type": event_type,
                "description": description,
                "emotional_impact": emotional_impact
            },
            metadata=metadata or {},
            level=LogLevel.INFO
        )
        
        await self._add_to_buffer(entry)
    
    async def log_security_event(
        self,
        event_type: str,
        severity: str,
        details: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a security-related event.
        
        Args:
            event_type: Type of security event
            severity: Severity level (info, warning, critical)
            details: Event details
            metadata: Optional additional metadata
        """
        level_map = {
            "info": LogLevel.INFO,
            "warning": LogLevel.WARNING,
            "critical": LogLevel.ERROR
        }
        
        entry = StateLogEntry(
            entry_type="security_event",
            data={
                "event_type": event_type,
                "severity": severity,
                "details": details
            },
            metadata=metadata or {},
            level=level_map.get(severity, LogLevel.WARNING)
        )
        
        await self._add_to_buffer(entry)
    
    async def log_custom(
        self,
        entry_type: str,
        data: Dict[str, Any],
        level: LogLevel = LogLevel.INFO,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a custom entry.
        
        Args:
            entry_type: Custom entry type
            data: Data to log
            level: Log level
            metadata: Optional metadata
        """
        entry = StateLogEntry(
            entry_type=entry_type,
            data=data,
            metadata=metadata or {},
            level=level
        )
        
        await self._add_to_buffer(entry)
    
    async def _add_to_buffer(self, entry: StateLogEntry):
        """
        Add entry to buffer and trigger flush if needed.
        
        This is non-blocking - it queues the entry and returns immediately.
        """
        self.log_buffer.append(entry)
        self.total_logged += 1
        
        logger.debug(f"Logged {entry.entry_type} entry (buffer: {len(self.log_buffer)}/{self.batch_size})")
        
        # Auto-flush if buffer is full
        if len(self.log_buffer) >= self.batch_size:
            asyncio.create_task(self.flush())
    
    async def flush(self):
        """
        Flush buffered logs to Convex backend.
        
        This is called automatically but can also be called manually.
        """
        if not self.log_buffer:
            return
        
        entries_to_flush = self.log_buffer.copy()
        self.log_buffer.clear()
        
        try:
            if self.mock_mode:
                await self._mock_flush(entries_to_flush)
            else:
                await self._real_flush(entries_to_flush)
            
            self.total_flushed += len(entries_to_flush)
            logger.debug(f"Flushed {len(entries_to_flush)} entries to Convex")
            
        except Exception as e:
            logger.error(f"Error flushing logs: {e}")
            # Put entries back in buffer for retry
            self.log_buffer.extend(entries_to_flush)
            
            # Also save to local backup if enabled
            if self.enable_local_backup:
                await self._save_local_backup(entries_to_flush)
    
    async def _real_flush(self, entries: List[StateLogEntry]):
        """
        Flush entries to actual Convex backend.
        
        This would make HTTP requests to Convex API.
        """
        if aiohttp is None:
            raise ImportError(
                "aiohttp is required for Convex backend integration. "
                "Install it with: pip install aiohttp"
            )
        
        payload = {
            "entries": [entry.to_dict() for entry in entries],
            "timestamp": datetime.now().isoformat()
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.convex_url}/api/log_state",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    raise Exception(f"Convex API error: {response.status}")
                
                logger.debug("Successfully flushed to Convex")
    
    async def _mock_flush(self, entries: List[StateLogEntry]):
        """
        Mock flush for testing/development.
        
        Simulates flushing without actual backend.
        """
        logger.debug(f"[MOCK] Would flush {len(entries)} entries to Convex")
        
        # Optionally save to local file for inspection
        if self.enable_local_backup:
            await self._save_local_backup(entries)
    
    async def _save_local_backup(self, entries: List[StateLogEntry]):
        """
        Save entries to local file as backup.
        
        Useful for development and as failsafe.
        """
        backup_dir = Path(self.local_backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"state_log_{timestamp}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "count": len(entries),
            "entries": [entry.to_dict() for entry in entries]
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.debug(f"Saved local backup: {backup_file}")
    
    async def _periodic_flush(self):
        """
        Periodic background task that flushes logs at regular intervals.
        
        This ensures logs are persisted even if buffer doesn't fill up.
        """
        while self.is_running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get logger statistics.
        
        Returns:
            Dictionary with logging stats
        """
        return {
            "total_logged": self.total_logged,
            "total_flushed": self.total_flushed,
            "buffer_size": len(self.log_buffer),
            "is_running": self.is_running,
            "mock_mode": self.mock_mode
        }


class ConvexStateLoggerContext:
    """
    Context manager for ConvexStateLogger.
    
    Makes it easy to use the logger with automatic start/stop:
    
    async with ConvexStateLoggerContext(url, key) as logger:
        await logger.log_interaction(...)
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize with same args as ConvexStateLogger."""
        self.logger = ConvexStateLogger(*args, **kwargs)
    
    async def __aenter__(self):
        """Start logger on context entry."""
        await self.logger.start()
        return self.logger
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop logger on context exit."""
        await self.logger.stop()


# Convex Schema Definitions
# These would be used in the Convex backend schema

CONVEX_SCHEMA = {
    "neurotransmitter_state": {
        "fields": {
            "dopamine": "float",
            "serotonin": "float",
            "cortisol": "float",
            "flags": "object",
            "timestamp": "string"
        },
        "indexes": ["timestamp"]
    },
    
    "dialectical_chain": {
        "fields": {
            "user_input": "string",
            "thesis": "object",
            "antithesis": "object",
            "synthesis": "object",
            "final_output": "string",
            "metadata": "object",
            "created_at": "string"
        },
        "indexes": ["created_at"]
    },
    
    "interaction": {
        "fields": {
            "user_input": "string",
            "agent_output": "string",
            "metadata": "object",
            "timestamp": "string"
        },
        "indexes": ["timestamp"]
    },
    
    "emotional_event": {
        "fields": {
            "event_type": "string",
            "description": "string",
            "emotional_impact": "object",
            "metadata": "object",
            "timestamp": "string"
        },
        "indexes": ["timestamp", "event_type"]
    },
    
    "security_event": {
        "fields": {
            "event_type": "string",
            "severity": "string",
            "details": "object",
            "metadata": "object",
            "timestamp": "string"
        },
        "indexes": ["timestamp", "severity"]
    }
}


def get_convex_schema_export() -> str:
    """
    Export Convex schema as JSON for backend setup.
    
    Returns:
        JSON string of schema definition
    """
    return json.dumps(CONVEX_SCHEMA, indent=2)
