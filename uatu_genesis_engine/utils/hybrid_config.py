"""
Configuration loader for hybrid settings.

Loads configuration from hybrid_settings.yaml and environment variables.
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class HybridConfig:
    """
    Configuration manager for Uatu Genesis Engine subsystems.
    
    Loads settings from hybrid_settings.yaml and environment variables,
    allowing seamless switching between local/cloud/mock modes.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to hybrid_settings.yaml (default: auto-detect)
        """
        if config_path is None:
            # Auto-detect config path
            possible_paths = [
                "./hybrid_settings.yaml",
                "../hybrid_settings.yaml",
                "../../hybrid_settings.yaml",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if config_path is None:
                raise FileNotFoundError(
                    "Could not find hybrid_settings.yaml. "
                    "Please ensure it exists in the project root."
                )
        
        self.config_path = config_path
        self.config = self._load_config()
        logger.info(f"Loaded configuration from {config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Substitute environment variables
        config = self._substitute_env_vars(config)
        
        return config
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """
        Recursively substitute environment variables in config.
        
        Replaces ${VAR_NAME} with the value of environment variable VAR_NAME.
        """
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable
            import re
            pattern = r'\$\{([^}]+)\}'
            
            def replacer(match):
                var_name = match.group(1)
                return os.environ.get(var_name, match.group(0))
            
            return re.sub(pattern, replacer, config)
        else:
            return config
    
    def get_convex_config(self) -> Dict[str, Any]:
        """Get Convex configuration based on current mode."""
        convex = self.config.get('convex', {})
        mode = convex.get('mode', 'mock')
        
        if mode == 'mock':
            return {
                'url': None,
                'api_key': None,
                'batch_size': convex.get('logging', {}).get('batch_size', 10),
                'flush_interval': convex.get('logging', {}).get('flush_interval_seconds', 5.0),
                'enable_local_backup': convex.get('logging', {}).get('enable_local_backup', True),
                'local_backup_path': convex.get('logging', {}).get('local_backup_path', './logs/state_backup'),
                'mode': 'mock'
            }
        elif mode == 'local':
            local_config = convex.get('local', {})
            return {
                'url': local_config.get('url'),
                'api_key': local_config.get('api_key'),
                'batch_size': convex.get('logging', {}).get('batch_size', 10),
                'flush_interval': convex.get('logging', {}).get('flush_interval_seconds', 5.0),
                'enable_local_backup': convex.get('logging', {}).get('enable_local_backup', True),
                'local_backup_path': convex.get('logging', {}).get('local_backup_path', './logs/state_backup'),
                'mode': 'local'
            }
        elif mode == 'cloud':
            cloud_config = convex.get('cloud', {})
            return {
                'url': cloud_config.get('url'),
                'api_key': cloud_config.get('api_key'),
                'batch_size': convex.get('logging', {}).get('batch_size', 10),
                'flush_interval': convex.get('logging', {}).get('flush_interval_seconds', 5.0),
                'enable_local_backup': convex.get('logging', {}).get('enable_local_backup', True),
                'local_backup_path': convex.get('logging', {}).get('local_backup_path', './logs/state_backup'),
                'mode': 'cloud'
            }
        else:
            raise ValueError(f"Unknown Convex mode: {mode}")
    
    def get_graphmert_config(self) -> Dict[str, Any]:
        """Get GraphMERT configuration based on current mode."""
        graphmert = self.config.get('graphmert', {})
        mode = graphmert.get('mode', 'mock')
        
        if mode == 'mock':
            return {
                'url': None,
                'api_key': None,
                'confidence_threshold': graphmert.get('extraction', {}).get('confidence_threshold', 0.6),
                'max_triples': graphmert.get('extraction', {}).get('max_triples_per_request', 50),
                'timeout': graphmert.get('extraction', {}).get('timeout_seconds', 5.0),
                'enable_mock': True,
                'mode': 'mock'
            }
        elif mode == 'local':
            local_config = graphmert.get('local', {})
            return {
                'url': local_config.get('url'),
                'api_key': local_config.get('api_key'),
                'confidence_threshold': graphmert.get('extraction', {}).get('confidence_threshold', 0.6),
                'max_triples': graphmert.get('extraction', {}).get('max_triples_per_request', 50),
                'timeout': graphmert.get('extraction', {}).get('timeout_seconds', 5.0),
                'enable_mock': False,
                'mode': 'local'
            }
        elif mode == 'cloud':
            cloud_config = graphmert.get('cloud', {})
            return {
                'url': cloud_config.get('url'),
                'api_key': cloud_config.get('api_key'),
                'confidence_threshold': graphmert.get('extraction', {}).get('confidence_threshold', 0.6),
                'max_triples': graphmert.get('extraction', {}).get('max_triples_per_request', 50),
                'timeout': graphmert.get('extraction', {}).get('timeout_seconds', 5.0),
                'enable_mock': False,
                'mode': 'cloud'
            }
        else:
            raise ValueError(f"Unknown GraphMERT mode: {mode}")
    
    def get_neurotransmitter_config(self) -> Dict[str, Any]:
        """Get NeurotransmitterEngine configuration."""
        nt = self.config.get('neurotransmitter', {})
        return {
            'initial_state': nt.get('initial_state', {}),
            'decay_rates': nt.get('decay_rates', {}),
            'baselines': nt.get('baselines', {}),
            'thresholds': nt.get('thresholds', {})
        }
    
    def get_dialectic_config(self) -> Dict[str, Any]:
        """Get DialecticInference configuration."""
        dialectic = self.config.get('dialectic', {})
        return {
            'enabled': dialectic.get('enabled', True),
            'enable_logging': dialectic.get('enable_logging', True),
            'default_bias_balance': dialectic.get('default_bias_balance', 0.6),
            'use_synthesis_output': dialectic.get('use_synthesis_output', True)
        }
    
    def get_soul_anchor_config(self) -> Dict[str, Any]:
        """Get SoulAnchorLedger configuration."""
        soul_anchor = self.config.get('soul_anchor', {})
        return {
            'enforce_verification': soul_anchor.get('enforce_verification', True),
            'refuse_boot_on_tamper': soul_anchor.get('refuse_boot_on_tamper', True),
            'hash_algorithm': soul_anchor.get('hash_algorithm', 'sha256')
        }
    
    def get_agent_loop_config(self) -> Dict[str, Any]:
        """Get agent loop integration configuration."""
        agent_loop = self.config.get('agent_loop', {})
        return {
            'enable_graphmert_filter': agent_loop.get('enable_graphmert_filter', True),
            'enable_neurotransmitter_updates': agent_loop.get('enable_neurotransmitter_updates', True),
            'enable_dialectic_reasoning': agent_loop.get('enable_dialectic_reasoning', True),
            'enable_convex_logging': agent_loop.get('enable_convex_logging', True),
            'reason_on_triples': agent_loop.get('reason_on_triples', True),
            'include_emotional_context': agent_loop.get('include_emotional_context', False),
            'include_dialectic_metadata': agent_loop.get('include_dialectic_metadata', False)
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        logging_config = self.config.get('logging', {})
        return {
            'level': logging_config.get('level', 'INFO'),
            'enable_file_logging': logging_config.get('enable_file_logging', True),
            'log_file_path': logging_config.get('log_file_path', './logs/uatu_engine.log'),
            'enable_console_logging': logging_config.get('enable_console_logging', True)
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        security = self.config.get('security', {})
        return {
            'enable_security_logging': security.get('enable_security_logging', True),
            'toxicity_threshold': security.get('toxicity_threshold', 0.7),
            'auto_escalate_toxic_inputs': security.get('auto_escalate_toxic_inputs', True)
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration."""
        performance = self.config.get('performance', {})
        return {
            'graphmert_timeout': performance.get('graphmert_timeout', 5.0),
            'convex_flush_timeout': performance.get('convex_flush_timeout', 3.0),
            'async_subsystems': performance.get('async_subsystems', True),
            'max_dialectic_history': performance.get('max_dialectic_history', 100),
            'max_neurotransmitter_history': performance.get('max_neurotransmitter_history', 500)
        }


# Global config instance
_config_instance: Optional[HybridConfig] = None


def get_config(config_path: Optional[str] = None) -> HybridConfig:
    """
    Get global configuration instance (singleton).
    
    Args:
        config_path: Path to config file (only used on first call)
        
    Returns:
        HybridConfig instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = HybridConfig(config_path)
    
    return _config_instance
