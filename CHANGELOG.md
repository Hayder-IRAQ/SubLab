# Changelog

All notable changes to SubLab will be documented in this file.

## [3.0.0] — 2025

### Added
- First-run Setup Wizard (auto-installs FFmpeg, verifies packages, selects language)
- Multi-language UI: English, Arabic, Russian, French, German, Spanish, Portuguese, Chinese, Japanese, Korean
- RTL layout support for Arabic UI
- Vosk offline speech engine with 40+ language models
- Argos Translate offline translation engine
- Video Maker tab — burn subtitles into video with custom styles
- Batch processing for multiple video files
- Export to SRT, VTT, CSV, JSON
- Dark / Light mode toggle
- GPU (CUDA) acceleration for Whisper
- Bilingual engine messages (English / Arabic)
- Template manager for subtitle styles
- Subtitle editor with in-app preview

### Improved
- Whisper engine: model caching, thread safety, progress callbacks
- Vosk engine: streaming download with progress, automatic extraction and renaming
- Config manager: cross-platform paths, safe save with recursion guard
- Audio extractor: FFmpeg primary + OpenCV silent fallback

## [2.0.0] — Earlier

- Initial multi-engine architecture
- Google Translate integration
- Basic SRT export
