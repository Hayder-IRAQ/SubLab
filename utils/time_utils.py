
# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# utils/time_utils.py
"""Time formatting utilities"""

from datetime import timedelta

def format_time(seconds: float) -> str:
    """Format time to HH:MM:SS"""
    return str(timedelta(seconds=int(seconds)))

def format_srt_time(seconds: float) -> str:
    """Format time for SRT (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def parse_srt_time(time_str: str) -> float:
    """Parse SRT time format to seconds"""
    try:
        parts = time_str.replace(',', '.').split(':')
        h = int(parts[0])
        m = int(parts[1])
        s = float(parts[2])
        return h * 3600 + m * 60 + s
    except Exception:
        return 0.0

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    else:
        return f"{seconds / 3600:.1f}h"
