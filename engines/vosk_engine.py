# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# engines/vosk_engine.py
"""Vosk speech recognition engine with bilingual support"""

import os
import json
import wave
import logging
import urllib.request
import zipfile
from typing import List, Dict, Tuple, Optional, Callable
from pathlib import Path
from dataclasses import dataclass

try:
    import vosk

    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class VoskMessages:
    """Bilingual messages for Vosk engine"""
    model_exists_en: str = "Model {model} already exists"
    model_exists_ar: str = "النموذج {model} موجود بالفعل"

    starting_download_en: str = "Starting download of {model} ({size})..."
    starting_download_ar: str = "جاري بدء تحميل {model} ({size})..."

    downloading_en: str = "Downloading {model}: {downloaded:.1f}MB / {total:.1f}MB ({progress:.0f}%)"
    downloading_ar: str = "جاري التحميل {model}: {downloaded:.1f}MB / {total:.1f}MB ({progress:.0f}%)"

    download_completed_en: str = "Download completed. Extracting {model}..."
    download_completed_ar: str = "اكتمل التحميل. جاري استخراج {model}..."

    model_extracted_en: str = "Model {model} extracted and ready"
    model_extracted_ar: str = "تم استخراج النموذج {model} وهو جاهز"

    download_failed_en: str = "Download failed: {error}"
    download_failed_ar: str = "فشل التحميل: {error}"

    loading_vosk_en: str = "Loading Vosk model..."
    loading_vosk_ar: str = "جاري تحميل نموذج Vosk..."

    model_loaded_en: str = "Vosk model loaded successfully"
    model_loaded_ar: str = "تم تحميل نموذج Vosk بنجاح"

    model_not_found_en: str = "Model {model} not found, downloading..."
    model_not_found_ar: str = "النموذج {model} غير موجود، جاري التحميل..."

    processing_audio_en: str = "Processing audio with Vosk..."
    processing_audio_ar: str = "جاري معالجة الصوت باستخدام Vosk..."

    processing_progress_en: str = "Processing audio... {progress:.0f}%"
    processing_progress_ar: str = "جاري معالجة الصوت... {progress:.0f}%"

    transcription_completed_en: str = "Vosk transcription completed"
    transcription_completed_ar: str = "اكتمل النسخ باستخدام Vosk"

    transcription_failed_en: str = "Transcription failed: {error}"
    transcription_failed_ar: str = "فشل النسخ: {error}"

    audio_format_error_en: str = "Audio must be mono PCM 16-bit"
    audio_format_error_ar: str = "يجب أن يكون الصوت أحادي القناة PCM 16-bit"

    def get(self, key: str, lang: str = 'en', **kwargs) -> str:
        """Get message in specified language"""
        attr_name = f"{key}_{lang}"
        if hasattr(self, attr_name):
            template = getattr(self, attr_name)
            return template.format(**kwargs) if kwargs else template
        return key


class VoskEngine:
    """Vosk speech recognition engine for offline processing with bilingual support"""

    # Available models
    MODELS = {
        # ── English ──
        'en-us-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
            'size': '40 MB', 'language': 'English (US)', 'quality': 'Good',
        },
        'en-us': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip',
            'size': '1.8 GB', 'language': 'English (US)', 'quality': 'Best',
        },
        'en-us-lgraph': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip',
            'size': '128 MB', 'language': 'English (US)', 'quality': 'Good',
        },
        'en-us-gigaspeech': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip',
            'size': '2.3 GB', 'language': 'English (US)', 'quality': 'Best',
        },
        # ── Indian English ──
        'en-in': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip',
            'size': '1 GB', 'language': 'English (India)', 'quality': 'Good',
        },
        'en-in-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip',
            'size': '36 MB', 'language': 'English (India)', 'quality': 'Good',
        },
        # ── Chinese ──
        'cn-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip',
            'size': '42 MB', 'language': 'Chinese', 'quality': 'Good',
        },
        'cn': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip',
            'size': '1.3 GB', 'language': 'Chinese', 'quality': 'Best',
        },
        # ── Russian ──
        'ru': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip',
            'size': '1.8 GB', 'language': 'Russian', 'quality': 'Best',
        },
        'ru-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip',
            'size': '45 MB', 'language': 'Russian', 'quality': 'Good',
        },
        # ── French ──
        'fr': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip',
            'size': '1.4 GB', 'language': 'French', 'quality': 'Best',
        },
        'fr-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip',
            'size': '41 MB', 'language': 'French', 'quality': 'Good',
        },
        # ── German ──
        'de': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip',
            'size': '1.9 GB', 'language': 'German', 'quality': 'Best',
        },
        'de-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip',
            'size': '45 MB', 'language': 'German', 'quality': 'Good',
        },
        # ── Spanish ──
        'es': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip',
            'size': '1.4 GB', 'language': 'Spanish', 'quality': 'Best',
        },
        'es-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip',
            'size': '39 MB', 'language': 'Spanish', 'quality': 'Good',
        },
        # ── Arabic ──
        'ar': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-ar-0.22-linto-1.1.0.zip',
            'size': '1.3 GB', 'language': 'Arabic', 'quality': 'Good',
        },
        'ar-mgb2': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-ar-mgb2-0.4.zip',
            'size': '318 MB', 'language': 'Arabic', 'quality': 'Good',
        },
        # ── Portuguese ──
        'pt-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip',
            'size': '31 MB', 'language': 'Portuguese', 'quality': 'Good',
        },
        'pt': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-pt-fb-v0.1.1-20220516_2113.zip',
            'size': '1.6 GB', 'language': 'Portuguese', 'quality': 'Good',
        },
        # ── Italian ──
        'it': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-it-0.22.zip',
            'size': '1.2 GB', 'language': 'Italian', 'quality': 'Best',
        },
        'it-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip',
            'size': '48 MB', 'language': 'Italian', 'quality': 'Good',
        },
        # ── Dutch ──
        'nl-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-nl-0.22.zip',
            'size': '39 MB', 'language': 'Dutch', 'quality': 'Good',
        },
        'nl': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-nl-spraakherkenning-0.6.zip',
            'size': '860 MB', 'language': 'Dutch', 'quality': 'Good',
        },
        # ── Turkish ──
        'tr-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip',
            'size': '35 MB', 'language': 'Turkish', 'quality': 'Good',
        },
        # ── Vietnamese ──
        'vn-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-vn-0.4.zip',
            'size': '32 MB', 'language': 'Vietnamese', 'quality': 'Good',
        },
        'vn': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-vn-0.4.zip',
            'size': '78 MB', 'language': 'Vietnamese', 'quality': 'Good',
        },
        # ── Japanese ──
        'ja-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip',
            'size': '48 MB', 'language': 'Japanese', 'quality': 'Good',
        },
        'ja': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip',
            'size': '1 GB', 'language': 'Japanese', 'quality': 'Best',
        },
        # ── Korean ──
        'ko-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-ko-0.22.zip',
            'size': '82 MB', 'language': 'Korean', 'quality': 'Good',
        },
        # ── Hindi ──
        'hi-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip',
            'size': '42 MB', 'language': 'Hindi', 'quality': 'Good',
        },
        'hi': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip',
            'size': '1.5 GB', 'language': 'Hindi', 'quality': 'Best',
        },
        # ── Polish ──
        'pl-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip',
            'size': '50 MB', 'language': 'Polish', 'quality': 'Good',
        },
        # ── Ukrainian ──
        'uk-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-uk-v3-small.zip',
            'size': '133 MB', 'language': 'Ukrainian', 'quality': 'Good',
        },
        'uk': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-uk-v3.zip',
            'size': '343 MB', 'language': 'Ukrainian', 'quality': 'Good',
        },
        # ── Greek ──
        'el': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-el-gr-0.7.zip',
            'size': '1.1 GB', 'language': 'Greek', 'quality': 'Good',
        },
        # ── Czech ──
        'cs-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-cs-0.4-rhasspy.zip',
            'size': '44 MB', 'language': 'Czech', 'quality': 'Good',
        },
        # ── Catalan ──
        'ca-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-ca-0.4.zip',
            'size': '42 MB', 'language': 'Catalan', 'quality': 'Good',
        },
        # ── Esperanto ──
        'eo-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-eo-0.42.zip',
            'size': '42 MB', 'language': 'Esperanto', 'quality': 'Good',
        },
        # ── Farsi (Persian) ──
        'fa': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-fa-0.42.zip',
            'size': '1.6 GB', 'language': 'Farsi', 'quality': 'Good',
        },
        'fa-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-fa-0.42.zip',
            'size': '53 MB', 'language': 'Farsi', 'quality': 'Good',
        },
        # ── Filipino (Tagalog) ──
        'tl': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-tl-ph-generic-0.6.zip',
            'size': '320 MB', 'language': 'Filipino', 'quality': 'Good',
        },
        # ── Kazakh ──
        'kz-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-kz-0.42.zip',
            'size': '58 MB', 'language': 'Kazakh', 'quality': 'Good',
        },
        'kz': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-kz-0.42.zip',
            'size': '1.3 GB', 'language': 'Kazakh', 'quality': 'Best',
        },
        # ── Swedish ──
        'sv-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-sv-rhasspy-0.15.zip',
            'size': '289 MB', 'language': 'Swedish', 'quality': 'Good',
        },
        # ── Uzbek ──
        'uz-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-uz-0.22.zip',
            'size': '49 MB', 'language': 'Uzbek', 'quality': 'Good',
        },
        # ── Breton ──
        'br': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-br-0.8.zip',
            'size': '70 MB', 'language': 'Breton', 'quality': 'Good',
        },
        # ── Gujarati ──
        'gu': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-gu-0.42.zip',
            'size': '700 MB', 'language': 'Gujarati', 'quality': 'Good',
        },
        'gu-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-gu-0.42.zip',
            'size': '100 MB', 'language': 'Gujarati', 'quality': 'Good',
        },
        # ── Tajik ──
        'tg': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-tg-0.22.zip',
            'size': '327 MB', 'language': 'Tajik', 'quality': 'Good',
        },
        'tg-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-tg-0.22.zip',
            'size': '50 MB', 'language': 'Tajik', 'quality': 'Good',
        },
        # ── Telugu ──
        'te-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-te-0.42.zip',
            'size': '58 MB', 'language': 'Telugu', 'quality': 'Good',
        },
        # ── Kyrgyz ──
        'ky-small': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-small-ky-0.42.zip',
            'size': '49 MB', 'language': 'Kyrgyz', 'quality': 'Good',
        },
        'ky': {
            'url': 'https://alphacephei.com/vosk/models/vosk-model-ky-0.42.zip',
            'size': '1.1 GB', 'language': 'Kyrgyz', 'quality': 'Best',
        },
    }

    def __init__(self, model_path: Optional[str] = None, model_name: str = 'en-us-small',
                 language: str = 'en'):
        """
        Initialize Vosk engine

        Args:
            model_path: Path to Vosk model directory
            model_name: Name of model to use
            language: UI language for messages ('en' or 'ar')
        """
        self.model_path = model_path
        self.model_name = model_name
        self.model = None
        self.is_available = VOSK_AVAILABLE
        self.ui_language = language
        self.messages = VoskMessages()

        if not self.is_available:
            logger.warning("Vosk not installed")

    def _get_message(self, key: str, **kwargs) -> str:
        """Get localized message"""
        return self.messages.get(key, self.ui_language, **kwargs)

    def set_ui_language(self, language: str):
        """Set UI language for messages"""
        self.ui_language = language

    def get_model_dir(self) -> Path:
        """Get model directory path - using project directory structure"""
        if self.model_path:
            return Path(self.model_path)

        # Use project directory instead of home directory
        current_dir = Path(__file__).parent.parent

        # Create models directory inside project
        model_dir = current_dir / 'models' / 'vosk'
        model_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Using model directory: {model_dir}")
        return model_dir

    @staticmethod
    def check_model_exists(model_name: str) -> bool:
        """Check if a Vosk model exists locally"""
        try:
            current_dir = Path(__file__).parent.parent
            model_dir = current_dir / 'models' / 'vosk'
            model_path = model_dir / model_name
            return model_path.exists()
        except:
            return False

    def download_model(self, model_name: str, progress_callback: Optional[Callable] = None) -> bool:
        """Download Vosk model with improved progress tracking"""
        if model_name not in self.MODELS:
            logger.error(f"Unknown model: {model_name}")
            if progress_callback:
                progress_callback(f"Unknown model: {model_name}", -1)
            return False

        model_info = self.MODELS[model_name]
        model_dir = self.get_model_dir()
        model_path = model_dir / model_name

        # Check if already downloaded
        if model_path.exists():
            logger.info(f"Model already exists: {model_path}")
            if progress_callback:
                progress_callback(
                    self._get_message('model_exists', model=model_name), 100
                )
            return True

        try:
            # Download model
            url = model_info['url']
            zip_path = model_dir / f"{model_name}.zip"

            logger.info(f"Downloading Vosk model: {model_name} to {model_dir}")
            if progress_callback:
                progress_callback(
                    self._get_message('starting_download', model=model_name, size=model_info['size']), 0
                )

            # Download with robust streaming (urlretrieve is unreliable for progress)
            import urllib.request
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'SubLab/3.0')

            with urllib.request.urlopen(req, timeout=60) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                chunk_size = 1024 * 256  # 256KB chunks
                last_reported_pct = -1

                with open(zip_path, 'wb') as out_file:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0 and progress_callback:
                            # Cap at 80% (reserve 20% for extraction)
                            progress_pct = int(min((downloaded / total_size) * 80, 80))
                            if progress_pct != last_reported_pct:
                                last_reported_pct = progress_pct
                                mb_downloaded = downloaded / (1024 * 1024)
                                mb_total = total_size / (1024 * 1024)
                                progress_callback(
                                    self._get_message('downloading',
                                                      model=model_name,
                                                      downloaded=mb_downloaded,
                                                      total=mb_total,
                                                      progress=progress_pct),
                                    progress_pct
                                )

            # Extract model
            logger.info(f"Extracting Vosk model: {model_name}")
            if progress_callback:
                progress_callback(
                    self._get_message('download_completed', model=model_name), 85
                )

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract all files
                zip_ref.extractall(model_dir)

            # Find extracted directory (might have different name)
            extracted_dirs = [d for d in model_dir.iterdir()
                              if d.is_dir() and d.name != model_name and 'vosk-model' in d.name]

            if extracted_dirs:
                # Rename the extracted directory to match model_name
                extracted_dirs[0].rename(model_path)
                logger.info(f"Renamed {extracted_dirs[0]} to {model_path}")

            # Clean up zip file
            try:
                zip_path.unlink()
                logger.info(f"Cleaned up zip file: {zip_path}")
            except Exception as cleanup_error:
                logger.warning(f"Could not remove zip file: {cleanup_error}")

            if progress_callback:
                progress_callback(
                    self._get_message('model_extracted', model=model_name), 100
                )

            logger.info(f"Vosk model downloaded successfully to: {model_path}")
            return True

        except Exception as e:
            logger.error(f"Error downloading Vosk model: {e}")
            if progress_callback:
                progress_callback(
                    self._get_message('download_failed', error=str(e)), -1
                )

            # Clean up partial files
            try:
                if 'zip_path' in locals() and zip_path.exists():
                    zip_path.unlink()
                if model_path.exists():
                    import shutil
                    shutil.rmtree(model_path)
                logger.info("Cleaned up partial download files")
            except Exception as cleanup_error:
                logger.warning(f"Could not clean up partial files: {cleanup_error}")

            return False

    def load_model(self, progress_callback: Optional[Callable] = None) -> bool:
        """Load Vosk model"""
        if not self.is_available:
            logger.error("Vosk not available")
            return False

        try:
            model_dir = self.get_model_dir()
            model_path = model_dir / self.model_name

            # Download if not exists
            if not model_path.exists():
                logger.info(f"Model {self.model_name} not found, downloading...")
                if progress_callback:
                    progress_callback(
                        self._get_message('model_not_found', model=self.model_name), 0
                    )
                if not self.download_model(self.model_name, progress_callback):
                    return False

            # Load model
            logger.info(f"Loading Vosk model from: {model_path}")
            if progress_callback:
                progress_callback(self._get_message('loading_vosk'), 50)

            # Set log level to reduce Vosk output
            vosk.SetLogLevel(-1)  # Disable Vosk logging

            # Create model
            self.model = vosk.Model(str(model_path))

            if progress_callback:
                progress_callback(self._get_message('model_loaded'), 100)

            logger.info(f"Vosk model loaded successfully from {model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            if progress_callback:
                progress_callback(f"Failed to load model: {e}", -1)
            return False

    def transcribe(self, audio_path: str, language: Optional[str] = None,
                   progress_callback: Optional[Callable] = None) -> Tuple[List[Dict], str]:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            language: Language code (ignored for Vosk - determined by model)
            progress_callback: Callback for progress updates

        Returns:
            Tuple of (segments, detected_language)
        """
        if not self.model:
            if not self.load_model(progress_callback):
                return [], ""

        try:
            logger.info(f"Transcribing audio with Vosk: {audio_path}")

            # Open audio file
            wf = wave.open(audio_path, 'rb')

            # Check audio format
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                logger.error("Audio must be mono PCM 16-bit")
                if progress_callback:
                    progress_callback(self._get_message('audio_format_error'), -1)
                return [], ""

            # Create recognizer
            rec = vosk.KaldiRecognizer(self.model, wf.getframerate())
            rec.SetWords(True)  # Get word timestamps

            segments = []
            results = []

            # Process audio
            total_frames = wf.getnframes()
            processed_frames = 0

            if progress_callback:
                progress_callback(self._get_message('processing_audio'), 0)

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result.get('text'):
                        results.append(result)

                processed_frames += 4000
                progress = int(min((processed_frames / total_frames) * 100, 99))

                if progress_callback and progress % 10 == 0:
                    progress_callback(
                        self._get_message('processing_progress', progress=progress), progress
                    )

            # Get final result
            final_result = json.loads(rec.FinalResult())
            if final_result.get('text'):
                results.append(final_result)

            # Convert results to segments
            for result in results:
                if 'result' in result:
                    words = result['result']
                    if words:
                        segment = {
                            'start_time': words[0]['start'],
                            'end_time': words[-1]['end'],
                            'text': result['text'],
                            'words': words
                        }
                        segments.append(segment)

            # Determine language from model
            language_map = {
                'en': 'en', 'cn': 'zh', 'ru': 'ru',
                'fr': 'fr', 'de': 'de', 'es': 'es', 'ar': 'ar'
            }
            detected_lang = language_map.get(self.model_name.split('-')[0], 'en')

            if progress_callback:
                progress_callback(self._get_message('transcription_completed'), 100)

            logger.info(f"Vosk transcription completed: {len(segments)} segments")
            return segments, detected_lang

        except Exception as e:
            logger.error(f"Vosk transcription error: {e}")
            if progress_callback:
                progress_callback(
                    self._get_message('transcription_failed', error=str(e)), -1
                )
            return [], ""
        finally:
            if 'wf' in locals():
                wf.close()

    def get_available_models(self) -> List[Dict]:
        """Get list of available models"""
        model_dir = self.get_model_dir()
        available = []

        for model_name, info in self.MODELS.items():
            model_path = model_dir / model_name
            available.append({
                'name': model_name,
                'language': info['language'],
                'size': info['size'],
                'quality': info['quality'],
                'downloaded': model_path.exists(),
                'path': str(model_path)
            })

        return available

    def get_model_info(self) -> Dict:
        """Get information about current model"""
        if self.model_name in self.MODELS:
            info = self.MODELS[self.model_name].copy()
            info['loaded'] = self.model is not None
            info['model_path'] = str(self.get_model_dir() / self.model_name)
            return info
        return {
            'name': self.model_name,
            'loaded': self.model is not None,
            'model_path': str(self.get_model_dir() / self.model_name)
        }
