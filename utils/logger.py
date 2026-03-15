# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.

# utils/logger.py
"""Logging configuration for the application"""

import logging
from pathlib import Path
from datetime import datetime

from typing import Tuple


def setup_logger(log_level='INFO', log_file=None):
    """Setup application logger"""

    # Create logs directory
    if log_file is None:
        log_dir = Path.home() / '.video_subtitle_generator' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # Suppress some verbose loggers
    logging.getLogger('numba').setLevel(logging.WARNING)
    logging.getLogger('whisper').setLevel(logging.WARNING)

    return logging.getLogger('VideoSubtitleGen')


# utils/time_utils.py
"""Time formatting utilities"""

from datetime import timedelta


def _parse_time_components(seconds: float) -> Tuple[int, int, int, int]:
    """Helper function to parse seconds into time components"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return hours, minutes, secs, millisecs


def format_time(seconds: float) -> str:
    """Format time to HH:MM:SS"""
    return str(timedelta(seconds=int(seconds)))


def format_srt_time(seconds: float) -> str:
    """Format time for SRT (HH:MM:SS,mmm)"""
    hours, minutes, secs, millisecs = _parse_time_components(seconds)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"


def parse_srt_time(time_str: str) -> float:
    """Parse SRT time format to seconds"""
    try:
        time_parts = time_str.replace(',', '.').split(':')
        if len(time_parts) != 3:
            return 0.0

        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = float(time_parts[2])
        return hours * 3600 + minutes * 60 + seconds
    except (ValueError, IndexError, AttributeError):
        return 0.0


def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"