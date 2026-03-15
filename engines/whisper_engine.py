# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# engines/whisper_engine.py
"""Whisper speech recognition engine with GPU acceleration - FINAL FIXED VERSION"""

import logging
import os
import warnings
import urllib.request
from typing import List, Dict, Optional, Tuple, Callable
import threading
from pathlib import Path
from dataclasses import dataclass

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    import whisper

    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class EngineMessages:
    """Bilingual messages for the engine"""
    loading_model_en: str = "Loading {model} model from cache..."
    loading_model_ar: str = "جاري تحميل نموذج {model} من الذاكرة المؤقتة..."

    model_loaded_cache_en: str = "Model loaded from cache"
    model_loaded_cache_ar: str = "تم تحميل النموذج من الذاكرة المؤقتة"

    model_not_found_en: str = "Model {model} not found locally, will download ({size})..."
    model_not_found_ar: str = "النموذج {model} غير موجود محلياً، سيتم تحميله ({size})..."

    loading_whisper_en: str = "Loading Whisper {model} model..."
    loading_whisper_ar: str = "جاري تحميل نموذج Whisper {model}..."

    initializing_device_en: str = "Initializing model on {device}..."
    initializing_device_ar: str = "جاري تهيئة النموذج على {device}..."

    gpu_detected_en: str = "GPU detected: {gpu_name}, using CUDA acceleration"
    gpu_detected_ar: str = "تم اكتشاف معالج الرسوميات: {gpu_name}، سيتم استخدام تسريع CUDA"

    no_gpu_detected_en: str = "No GPU detected, using CPU (slower performance)"
    no_gpu_detected_ar: str = "لم يتم اكتشاف معالج رسوميات، سيتم استخدام المعالج المركزي (أداء أبطأ)"

    download_failed_en: str = "Download failed. Please check your internet connection."
    download_failed_ar: str = "فشل التحميل. يرجى التحقق من اتصال الإنترنت."

    finalizing_en: str = "Finalizing model setup..."
    finalizing_ar: str = "جاري إتمام إعداد النموذج..."

    model_loaded_success_en: str = "{model} model loaded successfully on {device}"
    model_loaded_success_ar: str = "تم تحميل نموذج {model} بنجاح على {device}"

    transcribing_en: str = "Starting transcription..."
    transcribing_ar: str = "جاري بدء النسخ..."

    processing_segment_en: str = "Processing segment {current}/{total}"
    processing_segment_ar: str = "جاري معالجة المقطع {current}/{total}"

    transcription_completed_en: str = "Transcription completed"
    transcription_completed_ar: str = "اكتمل النسخ"

    transcription_failed_en: str = "Transcription failed: {error}"
    transcription_failed_ar: str = "فشل النسخ: {error}"

    detecting_language_en: str = "Detecting language..."
    detecting_language_ar: str = "جاري اكتشاف اللغة..."

    def get(self, key: str, lang: str = 'en', **kwargs) -> str:
        """Get message in specified language"""
        attr_name = f"{key}_{lang}"
        if hasattr(self, attr_name):
            message = getattr(self, attr_name)
            if kwargs:
                return message.format(**kwargs)
            return message
        return key


class WhisperEngine:
    """Speech recognition engine using OpenAI Whisper with GPU acceleration"""

    MODEL_SIZES = {
        'tiny': '39M',
        'base': '74M',
        'small': '244M',
        'medium': '769M',
        'large': '1550M',
        'large-v2': '1550M',
        'large-v3': '1550M'
    }

    def __init__(self, model_name: str = 'base', device: str = 'auto',
                 cache: bool = True, language: str = 'en'):
        """Initialize Whisper engine

        Args:
            model_name: Name of the model (tiny, base, small, medium, large)
            device: Device to use ('auto', 'cuda', 'cpu')
            cache: Whether to use cached models (boolean flag)
            language: Language for messages ('en' or 'ar')
        """
        self.model_name = model_name
        self.model = None
        self.language = language
        self.cache = cache
        self.messages = EngineMessages()
        self.cached_model = None

        # Set the download root directory
        self.download_root = str(Path.home() / ".cache" / "whisper")

        # Thread safety lock
        self._lock = threading.Lock()

        # Auto-detect device
        if device == 'auto':
            if TORCH_AVAILABLE and torch.cuda.is_available():
                self.device = 'cuda'
                gpu_name = torch.cuda.get_device_name(0) if TORCH_AVAILABLE else "Unknown"
                logger.info(self.messages.get('gpu_detected', self.language, gpu_name=gpu_name))
            else:
                self.device = 'cpu'
                logger.info(self.messages.get('no_gpu_detected', self.language))
        else:
            self.device = device

    def load_model(self, progress_callback: Optional[Callable] = None) -> bool:
        """Load Whisper model with proper parameters"""
        if not WHISPER_AVAILABLE:
            logger.error("Whisper not installed. Install with: pip install openai-whisper")
            return False

        try:
            with self._lock:
                # Update progress
                if progress_callback:
                    model_size = self.MODEL_SIZES.get(self.model_name, 'unknown')
                    message = self.messages.get('loading_whisper', self.language,
                                                model=self.model_name)
                    progress_callback(message, 10)

                logger.info(f"Loading Whisper model: {self.model_name} on {self.device}")

                # Clear GPU cache if using CUDA
                if self.device == 'cuda' and TORCH_AVAILABLE:
                    torch.cuda.empty_cache()

                # Load from cache if enabled and exists
                if self.cache and self.cached_model:
                    self.model = self.cached_model
                    if progress_callback:
                        message = self.messages.get('model_loaded_cache', self.language)
                        progress_callback(message, 100)
                else:
                    # Update progress - initializing device
                    if progress_callback:
                        message = self.messages.get('initializing_device', self.language,
                                                    device=self.device.upper())
                        progress_callback(message, 30)

                    # Load the model with correct parameters
                    self.model = whisper.load_model(
                        name=self.model_name,
                        device=self.device,
                        download_root=self.download_root  # This is a string path
                    )

                    # Cache the model if caching is enabled
                    if self.cache:
                        self.cached_model = self.model

                    # Update progress - finalizing
                    if progress_callback:
                        message = self.messages.get('finalizing', self.language)
                        progress_callback(message, 90)

                # Final success message
                if progress_callback:
                    message = self.messages.get('model_loaded_success', self.language,
                                                model=self.model_name,
                                                device=self.device.upper())
                    progress_callback(message, 100)

                logger.info(f"Whisper model {self.model_name} loaded successfully on {self.device}")
                return True

        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            if progress_callback:
                progress_callback(f"Failed to load model: {e}", -1)
            return False

    def transcribe(self, audio_path: str, language: Optional[str] = None,
                   progress_callback: Optional[Callable] = None) -> Tuple[List[Dict], str]:
        """Transcribe audio file"""
        if not self.model:
            logger.error("Model not loaded")
            return [], ""

        try:
            with self._lock:
                if progress_callback:
                    message = self.messages.get('transcribing', self.language)
                    progress_callback(message, 10)

                logger.info(f"Transcribing audio: {audio_path}")

                # Transcription options
                options = {
                    "fp16": self.device == "cuda",
                    "language": language,
                    "task": "transcribe",
                    "verbose": False
                }

                # Remove None values
                options = {k: v for k, v in options.items() if v is not None}

                if progress_callback:
                    progress_callback("Transcribing audio file...", 50)

                # Perform transcription
                result = self.model.transcribe(audio_path, **options)

                # Extract segments
                segments = []
                total_segments = len(result.get('segments', []))

                for idx, segment in enumerate(result.get('segments', [])):
                    if progress_callback and idx % 5 == 0:
                        message = self.messages.get('processing_segment', self.language,
                                                    current=idx + 1, total=total_segments)
                        progress = int(50 + (40 * (idx / total_segments)))
                        progress_callback(message, progress)

                    segments.append({
                        'start_time': segment['start'],
                        'end_time': segment['end'],
                        'text': segment['text'].strip(),
                        'original_language': result.get('language', 'unknown')
                    })

                detected_language = result.get('language', 'unknown')

                if progress_callback:
                    message = self.messages.get('transcription_completed', self.language)
                    progress_callback(f"{message} - {len(segments)} segments", 100)

                logger.info(f"Transcription completed: {len(segments)} segments, language: {detected_language}")
                return segments, detected_language

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            if progress_callback:
                message = self.messages.get('transcription_failed', self.language, error=str(e))
                progress_callback(message, -1)
            return [], ""

    def detect_language(self, audio_path: str) -> Tuple[str, float]:
        """Detect language from audio"""
        if not self.model:
            return "unknown", 0.0

        try:
            with self._lock:
                logger.info(f"Detecting language for: {audio_path}")

                # Load audio
                audio = whisper.load_audio(audio_path)
                audio = whisper.pad_or_trim(audio)

                # Make log-Mel spectrogram
                mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

                # Detect language
                _, probs = self.model.detect_language(mel)

                # Get most probable language
                lang = max(probs, key=probs.get)
                confidence = probs[lang]

                logger.info(f"Detected language: {lang} (confidence: {confidence:.2%})")
                return lang, confidence

        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "unknown", 0.0

    @staticmethod
    def check_model_exists(model_name: str) -> bool:
        """Check if model exists locally"""
        cache_dir = Path.home() / ".cache" / "whisper"
        model_file = cache_dir / f"{model_name}.pt"
        return model_file.exists()

    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available models"""
        return ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']

    @staticmethod
    def get_model_info(model_name: str) -> Dict:
        """Get model information"""
        model_info = {
            'tiny': {'size': '39M', 'parameters': '39M', 'english_only': True, 'multilingual': True},
            'base': {'size': '74M', 'parameters': '74M', 'english_only': True, 'multilingual': True},
            'small': {'size': '244M', 'parameters': '244M', 'english_only': True, 'multilingual': True},
            'medium': {'size': '769M', 'parameters': '769M', 'english_only': False, 'multilingual': True},
            'large': {'size': '1550M', 'parameters': '1550M', 'english_only': False, 'multilingual': True},
            'large-v2': {'size': '1550M', 'parameters': '1550M', 'english_only': False, 'multilingual': True},
            'large-v3': {'size': '1550M', 'parameters': '1550M', 'english_only': False, 'multilingual': True},
        }
        return model_info.get(model_name, {})

    def download_model_with_progress(self, model_name: str,
                                     progress_callback: Optional[Callable] = None) -> bool:
        """Download model with progress updates"""
        try:
            if progress_callback:
                model_size = self.MODEL_SIZES.get(model_name, 'unknown')
                progress_callback(f"Downloading {model_name} model ({model_size})...", 0)

            # Update model name and load
            self.model_name = model_name
            return self.load_model(progress_callback)

        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            if progress_callback:
                progress_callback(f"Download failed: {e}", -1)
            return False

    def cleanup(self):
        """Clean up resources"""
        with self._lock:
            if self.model:
                del self.model
                self.model = None

            if self.cached_model:
                del self.cached_model
                self.cached_model = None

            if self.device == 'cuda' and TORCH_AVAILABLE:
                torch.cuda.empty_cache()