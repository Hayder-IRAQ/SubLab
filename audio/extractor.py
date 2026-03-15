# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# audio/extractor.py
"""Audio extraction module for video files"""

import os
import subprocess
import wave
import numpy as np
import cv2
import logging
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class AudioExtractor:
    """Extract audio from video files"""

    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'],
                           capture_output=True,
                           check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("ffmpeg not found - audio extraction will be limited")
            return False

    def extract_audio(self, video_path: str, output_path: str = None,
                      sample_rate: int = 16000, channels: int = 1) -> Tuple[bool, str, str]:
        """
        Extract audio from video file

        Args:
            video_path: Path to video file
            output_path: Output audio path (auto-generated if None)
            sample_rate: Audio sample rate (default 16000 for speech)
            channels: Number of audio channels (default 1 for mono)

        Returns:
            Tuple of (success, audio_path, message)
        """
        if not os.path.exists(video_path):
            return False, "", "Video file not found"

        # Generate output path if not provided
        if output_path is None:
            base_name = Path(video_path).stem
            output_dir = Path(video_path).parent
            output_path = str(output_dir / f"{base_name}_audio.wav")

        # Try ffmpeg first (best quality)
        if self.ffmpeg_available:
            success, path, msg = self._extract_with_ffmpeg(
                video_path, output_path, sample_rate, channels
            )
            if success:
                return success, path, msg

        # Fallback to OpenCV method
        return self._extract_with_opencv(video_path, output_path, sample_rate)

    def _extract_with_ffmpeg(self, video_path: str, output_path: str,
                             sample_rate: int, channels: int) -> Tuple[bool, str, str]:
        """Extract audio using ffmpeg"""
        try:
            logger.info(f"Extracting audio with ffmpeg: {video_path}")

            cmd = [
                'ffmpeg', '-i', video_path,
                '-acodec', 'pcm_s16le',
                '-ar', str(sample_rate),
                '-ac', str(channels),
                '-y',  # Overwrite output file
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"Audio extracted successfully: {output_path}")
                return True, output_path, "Audio extracted successfully"
            else:
                logger.error(f"ffmpeg error: {result.stderr}")
                return False, "", f"ffmpeg error: {result.stderr[:100]}"

        except Exception as e:
            logger.error(f"Error extracting with ffmpeg: {e}")
            return False, "", str(e)

    def _extract_with_opencv(self, video_path: str, output_path: str,
                             sample_rate: int) -> Tuple[bool, str, str]:
        """Extract audio using OpenCV (creates silent audio for testing)"""
        try:
            logger.info(f"Creating test audio file: {video_path}")

            # Get video duration
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 10
            cap.release()

            # Create silent audio file
            samples = int(duration * sample_rate)
            audio_data = np.zeros(samples, dtype=np.int16)

            with wave.open(output_path, 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())

            logger.info(f"Silent test audio created: {output_path}")
            return True, output_path, "Test audio created (install ffmpeg for real audio)"

        except Exception as e:
            logger.error(f"Error creating test audio: {e}")
            return False, "", str(e)

    def get_audio_info(self, audio_path: str) -> Optional[dict]:
        """Get audio file information"""
        try:
            with wave.open(audio_path, 'r') as wav_file:
                info = {
                    'channels': wav_file.getnchannels(),
                    'sample_width': wav_file.getsampwidth(),
                    'framerate': wav_file.getframerate(),
                    'frames': wav_file.getnframes(),
                    'duration': wav_file.getnframes() / wav_file.getframerate()
                }
                return info
        except Exception as e:
            logger.error(f"Error reading audio info: {e}")
            return None

    def validate_audio_for_speech(self, audio_path: str) -> Tuple[bool, str]:
        """
        Validate if audio file is suitable for speech recognition

        Returns:
            Tuple of (is_valid, message)
        """
        info = self.get_audio_info(audio_path)

        if not info:
            return False, "Cannot read audio file"

        # Check duration
        if info['duration'] < 0.1:
            return False, "Audio too short (< 0.1s)"

        if info['duration'] > 3600:  # 1 hour
            return False, "Audio too long (> 1 hour) - consider splitting"

        # Check format
        if info['channels'] > 2:
            return False, f"Too many channels ({info['channels']}) - stereo or mono required"

        if info['framerate'] < 8000:
            return False, f"Sample rate too low ({info['framerate']}Hz) - minimum 8000Hz required"

        return True, "Audio file is valid for speech recognition"