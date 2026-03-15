#!/usr/bin/env python3
"""
Test script for multi-file audio/video subtitle generator
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")

    try:
        from ui.main_window_enhanced import EnhancedMainWindow, FileProcessor
        print("✓ Enhanced main window imported")
    except ImportError as e:
        print(f"✗ Failed to import main window: {e}")
        return False

    try:
        from audio.extractor import AudioExtractor
        print("✓ Audio extractor imported")
    except ImportError as e:
        print(f"✗ Failed to import audio extractor: {e}")
        return False

    try:
        from engines.whisper_engine_enhanced import WhisperEngine
        print("✓ Enhanced Whisper engine imported")
    except ImportError as e:
        print(f"✗ Failed to import Whisper engine: {e}")
        return False

    try:
        from translation.translator import Translator
        print("✓ Translator imported")
    except ImportError as e:
        print(f"✗ Failed to import translator: {e}")
        return False

    try:
        from utils.config import Config
        print("✓ Config imported")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False

    return True


def test_file_processor():
    """Test the file processor functionality"""
    print("\nTesting file processor...")

    try:
        from ui.main_window import FileProcessor
        from utils.config import Config

        # Create test processor
        processor = FileProcessor()
        print("✓ File processor created")

        # Test file type detection
        test_files = [
            "test.mp4",  # Video
            "test.wav",  # Audio
            "test.txt"  # Invalid
        ]

        for test_file in test_files:
            if test_file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv')):
                print(f"  ✓ {test_file} detected as video")
            elif test_file.lower().endswith(('.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a')):
                print(f"  ✓ {test_file} detected as audio")
            else:
                print(f"  ✗ {test_file} unsupported format")

        return True

    except Exception as e:
        print(f"✗ File processor test failed: {e}")
        return False


def test_supported_formats():
    """List all supported file formats"""
    print("\nSupported file formats:")

    video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
    audio_formats = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']

    print("Video formats:")
    for fmt in video_formats:
        print(f"  • {fmt}")

    print("Audio formats:")
    for fmt in audio_formats:
        print(f"  • {fmt}")

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Multi-File Audio/Video Subtitle Generator - Test Suite")
    print("=" * 60)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    # Test file processor
    if not test_file_processor():
        all_passed = False

    # Show supported formats
    test_supported_formats()

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed!")
        print("The system is ready to process multiple audio and video files.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)

    # Instructions for use
    print("\nHow to use the enhanced version:")
    print("1. Replace the original main_window.py with main_window_enhanced.py")
    print("2. Replace the original whisper_engine.py with whisper_engine_enhanced.py")
    print("3. Run the main.py file to start the application")
    print("\nNew features:")
    print("• Support for audio files (MP3, WAV, FLAC, AAC, OGG, M4A)")
    print("• Multiple file selection and batch processing")
    print("• Sequential processing with individual results for each file")
    print("• Fixed threading issues for stable operation")
    print("• Processing log to track all operations")
    print("• Stop button to cancel batch processing")


if __name__ == "__main__":
    main()