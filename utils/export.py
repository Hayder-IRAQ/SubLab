# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.

# utils/export.py
"""Export utilities for subtitles"""

import csv
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from utils.time_utils import format_time, format_srt_time

logger = logging.getLogger(__name__)


class Exporter:
    """Export subtitles to various formats"""

    def __init__(self):
        """Initialize exporter"""
        pass  # لم نعد بحاجة إلى output_dir

    def export_srt(self, subtitles: List[Dict], output_path: str) -> str:
        """
        Export subtitles to SRT format

        Args:
            subtitles: List of subtitle dictionaries
            output_path: Full path including filename for output file

        Returns:
            Path to exported file
        """
        try:
            # تأكد من أن المسار يحتوي على الامتداد الصحيح
            if not output_path.lower().endswith('.srt'):
                output_path += '.srt'

            with open(output_path, 'w', encoding='utf-8') as f:
                for i, sub in enumerate(subtitles, 1):
                    # Subtitle number
                    f.write(f"{i}\n")

                    # Timecodes
                    start = format_srt_time(sub['start_time'])
                    end = format_srt_time(sub['end_time'])
                    f.write(f"{start} --> {end}\n")

                    # Text (use translated if available)
                    text = sub.get('translated_text', sub['text'])
                    f.write(f"{text}\n\n")

            logger.info(f"Exported SRT: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error exporting SRT: {e}")
            raise

    def export_csv(self, subtitles: List[Dict], output_path: str,
                   include_translation: bool = False) -> str:
        """
        Export subtitles to CSV format

        Args:
            subtitles: List of subtitle dictionaries
            output_path: Full path including filename for output file
            include_translation: Whether to include translation columns

        Returns:
            Path to exported file
        """
        try:
            # تأكد من أن المسار يحتوي على الامتداد الصحيح
            if not output_path.lower().endswith('.csv'):
                output_path += '.csv'

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                # Determine fields
                if include_translation and subtitles and 'translated_text' in subtitles[0]:
                    fieldnames = [
                        'index', 'start_time', 'end_time', 'duration',
                        'original_text', 'original_language',
                        'translated_text', 'translation_language'
                    ]
                else:
                    fieldnames = [
                        'index', 'start_time', 'end_time', 'duration',
                        'text', 'language'
                    ]

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                # Write rows
                for i, sub in enumerate(subtitles, 1):
                    row = {
                        'index': i,
                        'start_time': format_time(sub['start_time']),
                        'end_time': format_time(sub['end_time']),
                        'duration': f"{sub['end_time'] - sub['start_time']:.2f}s"
                    }

                    if include_translation and 'translated_text' in sub:
                        row.update({
                            'original_text': sub['text'],
                            'original_language': sub.get('original_language', 'unknown'),
                            'translated_text': sub.get('translated_text', sub['text']),
                            'translation_language': sub.get('translation_language', 'unknown')
                        })
                    else:
                        row.update({
                            'text': sub['text'],
                            'language': sub.get('original_language', 'unknown')
                        })

                    writer.writerow(row)

            logger.info(f"Exported CSV: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            raise

    def export_webvtt(self, subtitles: List[Dict], output_path: str) -> str:
        """
        Export subtitles to WebVTT format

        Args:
            subtitles: List of subtitle dictionaries
            output_path: Full path including filename for output file

        Returns:
            Path to exported file
        """
        try:
            # تأكد من أن المسار يحتوي على الامتداد الصحيح
            if not output_path.lower().endswith('.vtt'):
                output_path += '.vtt'

            with open(output_path, 'w', encoding='utf-8') as f:
                # WebVTT header
                f.write("WEBVTT\n\n")

                for i, sub in enumerate(subtitles):
                    # Optional cue identifier
                    f.write(f"{i + 1}\n")

                    # Timecodes (WebVTT uses same format as SRT)
                    start = format_srt_time(sub['start_time'])
                    end = format_srt_time(sub['end_time'])
                    f.write(f"{start} --> {end}\n")

                    # Text
                    text = sub.get('translated_text', sub['text'])
                    f.write(f"{text}\n\n")

            logger.info(f"Exported WebVTT: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error exporting WebVTT: {e}")
            raise

    def export_json(self, subtitles: List[Dict], output_path: str) -> str:
        """
        Export subtitles to JSON format

        Args:
            subtitles: List of subtitle dictionaries
            output_path: Full path including filename for output file

        Returns:
            Path to exported file
        """
        import json

        try:
            # تأكد من أن المسار يحتوي على الامتداد الصحيح
            if not output_path.lower().endswith('.json'):
                output_path += '.json'

            # Prepare data
            export_data = {
                'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'subtitle_count': len(subtitles),
                'subtitles': subtitles
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Exported JSON: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            raise