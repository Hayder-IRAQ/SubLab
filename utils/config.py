# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.

# utils/config.py
"""Configuration management for the application"""

import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Config:
    """Application configuration manager"""

    DEFAULT_CONFIG = {
        'whisper_model': 'base',
        'speech_engine': 'whisper',
        'transcription_language': 'auto',
        'translation_language': 'none',
        'auto_save': True,
        'export_format': 'both',
        'ui_theme': 'light',
        'dark_mode': False,
        'window_size': (900, 700),
        'vosk_model_path': '',
        'vosk_model': 'en-us-small',
        'recent_files': [],
        'max_recent_files': 10,
        'subtitle_preview_count': 5,
        'auto_detect_language': True,
        'translation_engine': 'google',
        'argos_models': {},
        'whisper_device': 'auto',
        'batch_size': 5,
        'num_workers': 2,
        'cache_models': True,
        'log_level': 'INFO',
        'last_save_dir': None,
        'language': 'en',
        'ui_language': 'en',
        'setup_completed': False
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_path = self._get_config_path(config_path)
        self.config = self._load_config()
        self._saving = False  # Flag to prevent recursive saves

    def _get_config_path(self, config_path: Optional[str] = None) -> Path:
        """Get the path to config file"""
        if config_path:
            return Path(config_path)

        # Windows: %APPDATA%\VideoSubtitleGenerator\Settings.json
        # Linux/Mac: ~/.config/VideoSubtitleGenerator/Settings.json
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA')
            config_dir = Path(appdata) / 'VideoSubtitleGenerator'
        else:  # Linux/Mac
            config_dir = Path.home() / '.config' / 'VideoSubtitleGenerator'

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'Settings.json'

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        config = self.DEFAULT_CONFIG.copy()

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # Only update with valid keys
                    for key, value in saved_config.items():
                        if key in self.DEFAULT_CONFIG:
                            config[key] = value
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                # Don't save here to prevent recursion

        return config

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        if self._saving:  # Prevent recursive saves
            return False

        self._saving = True
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Create a clean copy for saving
            save_config = {}
            for key, value in config.items():
                if key in self.DEFAULT_CONFIG:
                    # Convert Path objects to strings
                    if isinstance(value, Path):
                        value = str(value)
                    save_config[key] = value

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(save_config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
        finally:
            self._saving = False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default if default is not None else self.DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        """Set a configuration value"""
        self.config[key] = value
        if auto_save and self.config.get('auto_save', True) and not self._saving:
            self.save()

    def save(self) -> bool:
        """Save current configuration to file"""
        return self._save_config(self.config)

    def add_recent_file(self, file_path: str) -> None:
        """Add a file to recent files list"""
        recent = self.config.get('recent_files', [])
        # Convert to string in case it's a Path object
        file_path = str(file_path)

        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)

        max_recent = self.get('max_recent_files', 10)
        self.config['recent_files'] = recent[:max_recent]

        if self.config.get('auto_save', True):
            self.save()

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()

    def get_last_save_dir(self) -> Optional[str]:
        """Get last used save directory"""
        return self.get('last_save_dir')

    def set_last_save_dir(self, directory: str) -> None:
        """Set last used save directory"""
        # Convert to string in case it's a Path object
        self.set('last_save_dir', str(directory))

    def toggle_dark_mode(self) -> None:
        """Toggle dark mode setting"""
        dark_mode = not self.get('dark_mode', False)
        self.set('dark_mode', dark_mode)
        self.set('ui_theme', 'dark' if dark_mode else 'light')