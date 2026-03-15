# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# ui/main_window.py
"""
SubLab — Main Window with Tabbed Interface & 10-language i18n
Tab 1: Subtitle Generator (from video/audio)
Tab 2: Subtitle File Translator
Tab 3: Video Maker (audio + N SRT → video)
"""

import sys
import logging
import queue
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QWidget, QFileDialog, QMessageBox,
    QProgressBar, QProgressDialog, QTextEdit, QComboBox, QStyleFactory, QListWidget,
    QTabWidget, QSplitter, QFrame, QStatusBar, QToolBar, QAction,
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

from audio.extractor import AudioExtractor
from engines.whisper_engine import WhisperEngine
from engines.vosk_engine import VoskEngine
from translation.translator import Translator
from utils.export import Exporter
from utils.time_utils import format_time
from utils.i18n import (
    t, set_language, get_language, is_rtl, SUPPORTED_LANGUAGES,
)
from ui.subtitle_translator_tab import SubtitleTranslatorTab
from ui.video_maker_tab import VideoMakerTab

import os
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
logger = logging.getLogger(__name__)

APP_VERSION = "3.0"
APP_NAME = "SubLab"


# ─── File Processor Thread ───────────────────────────────────────────────────

class FileProcessor(QThread):
    progress = pyqtSignal(str, float)
    status = pyqtSignal(str, str)
    file_completed = pyqtSignal(str, bool, str)
    all_completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.files_queue = queue.Queue()
        self.speech_engine = None
        self.translator = None
        self.config = None
        self.audio_extractor = AudioExtractor()
        self.exporter = Exporter()
        self.is_running = False
        self.should_stop = False

    def setup(self, speech_engine, translator, config):
        self.speech_engine = speech_engine
        self.translator = translator
        self.config = config

    def add_files(self, file_paths: List[str]):
        for path in file_paths:
            self.files_queue.put(path)

    def stop_processing(self):
        self.should_stop = True

    def run(self):
        self.is_running = True
        self.should_stop = False
        while not self.files_queue.empty() and not self.should_stop:
            file_path = self.files_queue.get()
            success = self._process_single(file_path)
            self.file_completed.emit(file_path, success, "Completed" if success else "Failed")
        self.is_running = False
        self.all_completed.emit()

    def _process_single(self, file_path: str) -> bool:
        try:
            file_name = Path(file_path).name
            self.status.emit(f"Processing: {file_name}", "info")

            audio_path = None
            video_exts = ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv')
            audio_exts = ('.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a')

            if file_path.lower().endswith(video_exts):
                self.status.emit(f"Extracting audio: {file_name}", "info")
                success, audio_path, msg = self.audio_extractor.extract_audio(file_path)
                if not success:
                    self.status.emit(f"Audio extraction failed: {msg}", "error")
                    return False
            elif file_path.lower().endswith(audio_exts):
                audio_path = file_path
            else:
                self.status.emit(f"Unsupported format: {file_name}", "error")
                return False

            if self.should_stop:
                return False

            self.progress.emit(f"Transcribing {file_name}...", 25)
            lang = self.config.get('transcription_language', 'auto')
            if lang == 'auto':
                lang = None

            def pcb(msg, prog):
                self.progress.emit(msg, prog)

            segments, detected_lang = self.speech_engine.transcribe(
                audio_path, language=lang, progress_callback=pcb
            )
            if not segments:
                self.status.emit(f"No subtitles for: {file_name}", "error")
                return False

            if self.should_stop:
                return False

            base_name = Path(file_path).stem
            output_dir = Path(file_path).parent
            srt_path = output_dir / f"{base_name}_subtitles.srt"
            self.exporter.export_srt(segments, str(srt_path))
            self.progress.emit(f"Saved: {srt_path.name}", 50)

            if self.should_stop:
                return False

            target_lang = self.config.get('translation_language', 'none')
            if target_lang != 'none' and self.translator and self.translator.is_available():
                self.progress.emit(f"Translating to {target_lang}...", 75)
                translated = self.translator.translate_subtitles(
                    segments, detected_lang or 'auto', target_lang, progress_callback=pcb
                )
                tr_path = output_dir / f"{base_name}_subtitles_{target_lang}.srt"
                self.exporter.export_srt(translated, str(tr_path))
                self.progress.emit(f"Saved translated: {tr_path.name}", 90)

            self.progress.emit(f"Completed: {file_name}", 100)
            return True

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            self.status.emit(f"Error: {Path(file_path).name}: {e}", "error")
            return False


# ─── Signal Emitter ──────────────────────────────────────────────────────────

class SignalEmitter(QObject):
    progress_updated = pyqtSignal(str, float)
    status_updated = pyqtSignal(str, str)
    subtitles_updated = pyqtSignal(list)


# ─── Main Window ─────────────────────────────────────────────────────────────

class SubLabMainWindow(QMainWindow):
    def __init__(self, config, gpu_info=None):
        super().__init__()
        self.config = config
        self.gpu_info = gpu_info or {}

        self.file_paths = []
        self.processing_results = {}
        self.is_processing = False
        self.file_processor = None

        self.signal_emitter = SignalEmitter()
        self.audio_extractor = AudioExtractor()
        self.speech_engine = None
        self.translator = None
        self.exporter = Exporter()

        self._init_ui()
        self._connect_signals()
        self._load_settings()

    # ── UI Build ──────────────────────────────────────────────────────────────

    def _init_ui(self):
        self.setWindowTitle(f"{t('app.title')} v{APP_VERSION}")
        self.setGeometry(100, 100, 1050, 850)
        self.setMinimumSize(800, 600)

        # Apply RTL if needed
        if is_rtl():
            self.setLayoutDirection(Qt.RightToLeft)

        # ── Toolbar with language switcher ──
        toolbar = QToolBar("Settings")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("QToolBar{spacing:6px;padding:2px 6px;}")
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        self.lbl_toolbar_language = QLabel(f"  {t('label.language')} ")
        toolbar.addWidget(self.lbl_toolbar_language)
        self.ui_lang_combo = QComboBox()
        self.ui_lang_combo.setFixedWidth(140)
        flags = {
            "en": "🇬🇧", "ar": "🇸🇦", "ru": "🇷🇺", "fr": "🇫🇷", "de": "🇩🇪",
            "es": "🇪🇸", "pt": "🇧🇷", "zh": "🇨🇳", "ja": "🇯🇵", "ko": "🇰🇷",
        }
        for code, name in SUPPORTED_LANGUAGES:
            flag = flags.get(code, "🌐")
            self.ui_lang_combo.addItem(f"{flag} {name}", code)
        idx = self.ui_lang_combo.findData(get_language())
        if idx >= 0:
            self.ui_lang_combo.setCurrentIndex(idx)
        toolbar.addWidget(self.ui_lang_combo)

        toolbar.addSeparator()

        # Theme toggle in toolbar
        self.btn_theme = QPushButton(t("btn.dark_mode"))
        self.btn_theme.setFixedWidth(100)
        self.btn_theme.setFixedHeight(28)
        toolbar.addWidget(self.btn_theme)

        # ── Central tab widget ──
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(QFont("Arial", 10))
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabPosition(QTabWidget.North)

        # Tab 1: Generator
        gen_widget = self._build_generator_tab()
        self.tab_widget.addTab(gen_widget, t("tab.generator"))

        # Tab 2: File Translator
        self.translator_tab = SubtitleTranslatorTab(config=self.config)
        self.tab_widget.addTab(self.translator_tab, t("tab.translator"))

        # Tab 3: Video Maker
        self.video_maker_tab = VideoMakerTab(config=self.config)
        self.tab_widget.addTab(self.video_maker_tab, t("tab.video_maker"))

        self.setCentralWidget(self.tab_widget)

        # Status bar
        self.statusBar().showMessage(f"{APP_NAME} v{APP_VERSION} — {t('app.ready')}")

        # Apply saved theme
        self.dark_mode = self.config.get('dark_mode', False)
        self.apply_theme('dark' if self.dark_mode else 'light')

    def _build_generator_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Header
        title = QLabel(t("app.title"))
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))

        subtitle = QLabel(t("app.subtitle"))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setStyleSheet("color: gray;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # GPU info
        if self.gpu_info.get('cuda_available'):
            gpu_label = QLabel(f"⚡ GPU: {self.gpu_info['device_name']} ({self.gpu_info['memory']})")
            gpu_label.setAlignment(Qt.AlignCenter)
            gpu_label.setStyleSheet("color: #2E7D32; font-size: 10px;")
            layout.addWidget(gpu_label)

        # File list
        self.lbl_files = QLabel(t("label.files_list"))
        layout.addWidget(self.lbl_files)

        self.file_list_widget = QListWidget()
        self.file_list_widget.setMaximumHeight(140)
        layout.addWidget(self.file_list_widget)

        # Buttons row
        btn_row = QHBoxLayout()
        self.btn_select = QPushButton(t("btn.select_files"))
        self.btn_clear = QPushButton(t("btn.clear"))
        self.btn_process = QPushButton(t("btn.process_all"))
        self.btn_stop = QPushButton(t("btn.stop"))
        self.btn_stop.setEnabled(False)

        for btn in (self.btn_select, self.btn_clear, self.btn_process, self.btn_stop):
            btn.setMinimumHeight(32)

        self.btn_process.setStyleSheet("""
            QPushButton { background-color: #1565C0; color: white; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #0D47A1; }
            QPushButton:disabled { background-color: #9E9E9E; }
        """)

        btn_row.addWidget(self.btn_select)
        btn_row.addWidget(self.btn_clear)
        btn_row.addWidget(self.btn_process)
        btn_row.addWidget(self.btn_stop)
        layout.addLayout(btn_row)

        # Engine controls
        engine_row = QHBoxLayout()
        self.lbl_engine = QLabel(t("label.speech_engine"))
        engine_row.addWidget(self.lbl_engine)
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(['Whisper', 'Vosk'])
        engine_row.addWidget(self.engine_combo)

        self.lbl_model = QLabel(t("label.model"))
        engine_row.addWidget(self.lbl_model)
        self.model_combo = QComboBox()
        self._update_model_combo()
        engine_row.addWidget(self.model_combo)
        engine_row.addStretch()
        layout.addLayout(engine_row)

        # Translation controls
        tr_row = QHBoxLayout()
        self.lbl_translation = QLabel(t("label.translation"))
        tr_row.addWidget(self.lbl_translation)
        self.tr_engine_combo = QComboBox()
        self.tr_engine_combo.addItems(['Google', 'Argos'])
        tr_row.addWidget(self.tr_engine_combo)

        self.lbl_translate_to = QLabel(t("label.translate_to"))
        tr_row.addWidget(self.lbl_translate_to)
        self.lang_combo = QComboBox()
        self._update_language_combo()
        tr_row.addWidget(self.lang_combo)
        tr_row.addStretch()
        layout.addLayout(tr_row)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel(t("app.ready"))
        self.status_label.setStyleSheet("padding: 4px;")
        layout.addWidget(self.status_label)

        # Log
        self.lbl_log = QLabel(t("label.processing_log"))
        layout.addWidget(self.lbl_log)
        self.processing_log = QTextEdit()
        self.processing_log.setReadOnly(True)
        self.processing_log.setMaximumHeight(180)
        layout.addWidget(self.processing_log)

        # Copyright
        copy_lbl = QLabel(f"© 2025 Hayder Odhafa — {APP_NAME} v{APP_VERSION} — CC BY-NC 4.0")
        copy_lbl.setAlignment(Qt.AlignCenter)
        copy_lbl.setStyleSheet("color: gray; font-size: 9px;")
        layout.addWidget(copy_lbl)

        widget.setLayout(layout)
        return widget

    # ── Signals ───────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.btn_select.clicked.connect(self.select_files)
        self.btn_clear.clicked.connect(self.clear_file_list)
        self.btn_process.clicked.connect(self.process_all_files)
        self.btn_stop.clicked.connect(self.stop_processing)
        self.btn_theme.clicked.connect(self.toggle_dark_mode)
        self.ui_lang_combo.currentIndexChanged.connect(self._on_language_changed)

        self.engine_combo.currentTextChanged.connect(self.change_engine)
        self.model_combo.currentIndexChanged.connect(self.change_model)
        self.tr_engine_combo.currentTextChanged.connect(self.change_translation_engine)

        self.signal_emitter.progress_updated.connect(self.update_progress)
        self.signal_emitter.status_updated.connect(self.update_status)

        # Guard flag to prevent cascading signal calls during combo updates
        self._updating_combos = False

    def _load_settings(self):
        self._updating_combos = True

        engine = self.config.get('speech_engine', 'whisper')
        self.engine_combo.blockSignals(True)
        self.engine_combo.setCurrentText(engine.capitalize())
        self.engine_combo.blockSignals(False)

        # Update model combo for current engine without triggering signals
        self._update_model_combo()

        # Restore saved model selection
        if engine == 'whisper':
            saved_model = self.config.get('whisper_model', 'base')
        else:
            saved_model = self.config.get('vosk_model', 'en-us-small')
        idx = self.model_combo.findData(saved_model)
        if idx >= 0:
            self.model_combo.blockSignals(True)
            self.model_combo.setCurrentIndex(idx)
            self.model_combo.blockSignals(False)

        tr_engine = self.config.get('translation_engine', 'google')
        self.tr_engine_combo.blockSignals(True)
        self.tr_engine_combo.setCurrentText(tr_engine.capitalize())
        self.tr_engine_combo.blockSignals(False)

        lang = self.config.get('translation_language', 'none')
        idx = self.lang_combo.findData(lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)

        self._updating_combos = False

        # Now safely load engine and translator
        self._load_speech_engine(engine)
        self._load_translator(tr_engine)

    # ── Language Switching ────────────────────────────────────────────────────

    def _on_language_changed(self):
        code = self.ui_lang_combo.currentData()
        if not code or code == get_language():
            return

        set_language(code)
        self.config.set("ui_language", code, auto_save=True)

        # RTL handling
        if is_rtl():
            self.setLayoutDirection(Qt.RightToLeft)
            QApplication.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
            QApplication.setLayoutDirection(Qt.LeftToRight)

        # Update all visible texts
        self._refresh_ui_texts()
        self.log_message(t("msg.restart_required"))

    def _refresh_ui_texts(self):
        """Live-update all translatable UI texts."""
        self.setWindowTitle(f"{t('app.title')} v{APP_VERSION}")

        # Tabs
        self.tab_widget.setTabText(0, t("tab.generator"))
        self.tab_widget.setTabText(1, t("tab.translator"))
        self.tab_widget.setTabText(2, t("tab.video_maker"))

        # Generator tab labels
        self.lbl_files.setText(t("label.files_list"))
        self.btn_select.setText(t("btn.select_files"))
        self.btn_clear.setText(t("btn.clear"))
        self.btn_process.setText(t("btn.process_all"))
        self.btn_stop.setText(t("btn.stop"))
        self.lbl_engine.setText(t("label.speech_engine"))
        self.lbl_model.setText(t("label.model"))
        self.lbl_translation.setText(t("label.translation"))
        self.lbl_translate_to.setText(t("label.translate_to"))
        self.lbl_log.setText(t("label.processing_log"))
        self.status_label.setText(t("app.ready"))

        # Theme button
        self.btn_theme.setText(t("btn.light_mode") if self.dark_mode else t("btn.dark_mode"))

        # Status bar
        self.statusBar().showMessage(f"{APP_NAME} v{APP_VERSION} — {t('app.ready')}")

        # Toolbar language label
        self.lbl_toolbar_language.setText(f"  {t('label.language')} ")

        # Refresh translation target combo first item
        if self.lang_combo.count() > 0:
            self.lang_combo.setItemText(0, t("label.no_translation"))

        # Refresh sub-tabs
        if hasattr(self, 'translator_tab'):
            self.translator_tab.refresh_texts()
        if hasattr(self, 'video_maker_tab'):
            self.video_maker_tab.refresh_texts()

    # ── Combos ────────────────────────────────────────────────────────────────

    def _update_model_combo(self):
        self._updating_combos = True
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        engine = self.engine_combo.currentText().lower()
        if engine == 'whisper':
            models = [
                ('tiny', 'Tiny (39MB)'), ('base', 'Base (74MB)'),
                ('small', 'Small (244MB)'), ('medium', 'Medium (769MB)'),
                ('large', 'Large (1550MB)'),
            ]
        else:
            # Vosk — all models from VoskEngine.MODELS
            from engines.vosk_engine import VoskEngine
            models = []
            for key, info in VoskEngine.MODELS.items():
                label = f"{info['language']} — {info['size']}"
                if info.get('quality') == 'Best':
                    label += " ⭐"
                if 'small' in key:
                    label += " (lite)"
                models.append((key, label))
        for value, text in models:
            self.model_combo.addItem(text, value)
        self.model_combo.blockSignals(False)
        self._updating_combos = False

    def _update_language_combo(self):
        self.lang_combo.clear()
        self.lang_combo.addItem(t("label.no_translation"), "none")
        for code, name in [
            ('en', 'English'), ('ar', 'العربية'), ('es', 'Español'),
            ('fr', 'Français'), ('de', 'Deutsch'), ('ru', 'Русский'),
            ('zh', '中文'), ('ja', '日本語'), ('ko', '한국어'),
            ('tr', 'Türkçe'), ('pt', 'Português'), ('it', 'Italiano'),
            ('hi', 'हिन्दी'), ('nl', 'Nederlands'), ('pl', 'Polski'),
        ]:
            self.lang_combo.addItem(name, code)

    # ── Engine Loading ────────────────────────────────────────────────────────

    def _load_speech_engine(self, engine_type: str):
        """Load speech engine — with download confirmation dialog if model not found"""
        # Stop any currently running loader
        if hasattr(self, '_engine_loader') and self._engine_loader.isRunning():
            self.log_message("⏳ Previous model still loading, please wait...")
            return

        if engine_type == 'whisper':
            model = self.model_combo.currentData()
            if not model:
                return
            device = self.config.get('whisper_device', 'auto')
            cache = self.config.get('cache_models', True)

            try:
                model_exists = WhisperEngine.check_model_exists(model)
            except Exception:
                model_exists = False

            if not model_exists:
                sizes = {'tiny': '39MB', 'base': '74MB', 'small': '244MB',
                         'medium': '769MB', 'large': '1.5GB'}
                size_str = sizes.get(model, '?')

                reply = QMessageBox.question(
                    self,
                    t("dlg.model_download_title"),
                    t("dlg.model_not_found", model=model, size=size_str),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply != QMessageBox.Yes:
                    self.log_message(t("dlg.download_cancelled"))
                    return

                self.log_message(f"⬇️ Downloading Whisper '{model}' ({size_str})...")
                self.update_status(t("dlg.downloading_progress", model=model, pct=0), "info")

            self._start_engine_loader_thread(engine_type, model, device, cache)

        elif engine_type == 'vosk':
            model_name = self.model_combo.currentData()
            if not model_name:
                return

            try:
                model_exists = VoskEngine.check_model_exists(model_name)
            except Exception:
                model_exists = False

            if not model_exists:
                vosk_info = VoskEngine.MODELS.get(model_name, {})
                size_str = vosk_info.get('size', '?')

                reply = QMessageBox.question(
                    self,
                    t("dlg.model_download_title"),
                    t("dlg.model_not_found", model=model_name, size=size_str),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply != QMessageBox.Yes:
                    self.log_message(t("dlg.download_cancelled"))
                    return

                self.log_message(f"⬇️ Downloading Vosk '{model_name}' ({size_str})...")

            self._start_engine_loader_thread(engine_type, model_name)

    def _start_engine_loader_thread(self, engine_type: str, model: str,
                                     device: str = 'auto', cache: bool = True):
        """Run model loading in a separate thread to avoid UI freeze"""
        from PyQt5.QtCore import QThread, pyqtSignal as Signal

        class _EngineLoaderThread(QThread):
            done = Signal(object, str)   # (engine_instance | None, error_msg)
            progress = Signal(str, int)  # (message, percent)

            def __init__(self, etype, model_name, dev='auto', use_cache=True):
                super().__init__()
                self.etype = etype
                self.model_name = model_name
                self.dev = dev
                self.use_cache = use_cache

            def run(self):
                try:
                    if self.etype == 'whisper':
                        engine = WhisperEngine(self.model_name, self.dev, self.use_cache)
                        ok = engine.load_model(progress_callback=self.progress.emit)
                        if ok:
                            self.done.emit(engine, "")
                        else:
                            self.done.emit(None, "Failed to load Whisper model")
                    elif self.etype == 'vosk':
                        engine = VoskEngine(model_name=self.model_name)
                        ok = engine.load_model(progress_callback=self.progress.emit)
                        if ok:
                            self.done.emit(engine, "")
                        else:
                            self.done.emit(None, "Failed to load Vosk model")
                    else:
                        self.done.emit(None, f"Unknown engine type: {self.etype}")
                except Exception as e:
                    self.done.emit(None, str(e))

        self._engine_loader = _EngineLoaderThread(engine_type, model, device, cache)
        self._engine_loader.done.connect(self._on_engine_loaded)

        # Create a visible progress dialog popup
        self._download_dialog = QProgressDialog(
            t("msg.loading_model"), t("dlg.cancel"), 0, 100, self
        )
        self._download_dialog.setWindowTitle(t("dlg.downloading_model"))
        self._download_dialog.setMinimumWidth(450)
        self._download_dialog.setWindowModality(Qt.WindowModal)
        self._download_dialog.setAutoClose(False)
        self._download_dialog.setAutoReset(False)
        self._download_dialog.setValue(0)

        # Connect progress signal to both dialog and log
        self._engine_loader.progress.connect(self._on_engine_download_progress)

        # Cancel button handling
        self._download_dialog.canceled.connect(self._cancel_engine_download)

        self._download_dialog.show()

        # Also show internal progress bar and disable process button
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(t("msg.loading_model"))
        self.btn_process.setEnabled(False)
        self.btn_process.setText(t("msg.loading_model"))
        self._engine_loader.start()

    def _cancel_engine_download(self):
        """Handle download cancel button"""
        if hasattr(self, '_engine_loader') and self._engine_loader.isRunning():
            self._engine_loader.terminate()
            self._engine_loader.wait(2000)
        self.log_message(t("dlg.download_cancelled"))
        self.btn_process.setEnabled(True)
        self.btn_process.setText(t("btn.process_all"))
        self.progress_bar.setVisible(False)

    def _on_engine_download_progress(self, msg: str, pct: int):
        """Update progress dialog and progress bar during model download"""
        # Clamp percentage to valid range
        pct = max(0, min(100, pct))
        # Update popup dialog
        if hasattr(self, '_download_dialog') and self._download_dialog.isVisible():
            self._download_dialog.setValue(pct)
            self._download_dialog.setLabelText(msg)
        # Update internal progress bar
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"{msg}  ({pct}%)")
        # Only log every 10% to avoid flooding
        if pct % 10 == 0 or pct <= 1 or pct >= 99:
            self.log_message(f"[{pct}%] {msg}")

    def _on_engine_loaded(self, engine, error_msg: str):
        """Handle engine load result"""
        # Close progress dialog
        if hasattr(self, '_download_dialog'):
            self._download_dialog.close()
            self._download_dialog.deleteLater()

        # Hide progress bar
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

        if engine:
            self.speech_engine = engine
            model_name = getattr(engine, 'model_name', '')
            self.log_message(f"✅ '{model_name}' loaded successfully")
            self.update_status(f"Model ready: {model_name}", "success")
        else:
            self.speech_engine = None
            logger.error(f"Engine load error: {error_msg}")
            self.update_status(f"Engine error: {error_msg}", "error")
            self.log_message(f"❌ {error_msg}")
            QMessageBox.critical(
                self, t("msg.engine_error_title"),
                t("msg.engine_load_failed", error=error_msg)
            )

        # Re-enable process button
        self.btn_process.setEnabled(True)
        self.btn_process.setText(t("btn.process_all"))

    def _load_translator(self, engine: str):
        try:
            self.translator = Translator(engine)
            if not self.translator.is_available():
                raise Exception(f"{engine} unavailable")
            self.log_message(t("msg.loaded_engine", name=engine))
        except Exception as e:
            logger.error(f"Translator error: {e}")
            self.translator = None

    # ── File Management ───────────────────────────────────────────────────────

    def select_files(self):
        last_dir = self.config.get('last_save_dir') or ""
        paths, _ = QFileDialog.getOpenFileNames(
            self, t("btn.select_files"), last_dir,
            "Media Files (*.mp4 *.avi *.mov *.mkv *.webm *.flv *.wav *.mp3 *.flac *.aac *.ogg *.m4a);;"
            "Video (*.mp4 *.avi *.mov *.mkv *.webm *.flv);;"
            "Audio (*.wav *.mp3 *.flac *.aac *.ogg *.m4a)"
        )
        if paths:
            self.file_paths.extend(paths)
            self._refresh_file_list()
            self.config.set_last_save_dir(str(Path(paths[0]).parent))
            self.log_message(t("msg.added_files", n=len(paths)))

    def clear_file_list(self):
        self.file_paths.clear()
        self.processing_results.clear()
        self.file_list_widget.clear()

    def _refresh_file_list(self):
        self.file_list_widget.clear()
        for path in self.file_paths:
            name = Path(path).name
            video_exts = ('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv')
            icon = "📹" if path.lower().endswith(video_exts) else "🔊"
            status = self.processing_results.get(path, "")
            suffix = {"Success": " ✅", "Failed": " ❌", "Processing": " ⏳"}.get(status, "")
            self.file_list_widget.addItem(f"{icon} {name}{suffix}")

    # ── Processing ────────────────────────────────────────────────────────────

    def process_all_files(self):
        idx = self.lang_combo.currentIndex()
        if idx >= 0:
            tl = self.lang_combo.itemData(idx)
            if tl:
                self.config.set('translation_language', tl)

        if not self.file_paths:
            QMessageBox.warning(self, t("msg.error"), t("msg.no_files"))
            return
        if not self.speech_engine:
            # Check if model is still loading
            if hasattr(self, '_engine_loader') and self._engine_loader.isRunning():
                QMessageBox.information(
                    self, t("msg.loading_title"),
                    t("msg.model_still_loading")
                )
            else:
                QMessageBox.critical(self, t("msg.error"), t("msg.no_engine"))
            return

        self.is_processing = True
        self.btn_process.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_select.setEnabled(False)
        self.btn_clear.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.processing_results.clear()

        self.file_processor = FileProcessor()
        self.file_processor.setup(self.speech_engine, self.translator, self.config)
        self.file_processor.add_files(self.file_paths)
        self.file_processor.progress.connect(self.update_progress)
        self.file_processor.status.connect(self.update_status)
        self.file_processor.file_completed.connect(self._on_file_done)
        self.file_processor.all_completed.connect(self._on_all_done)
        self.file_processor.start()
        self.log_message(f"Processing {len(self.file_paths)} files...")

    def stop_processing(self):
        if self.file_processor and self.file_processor.is_running:
            self.file_processor.stop_processing()
            self.log_message("Stopping...")

    def _on_file_done(self, path: str, success: bool, status: str):
        self.processing_results[path] = "Success" if success else "Failed"
        self._refresh_file_list()
        name = Path(path).name
        self.log_message(f"{'✅' if success else '❌'} {name}")

    def _on_all_done(self):
        self.is_processing = False
        self.btn_process.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_select.setEnabled(True)
        self.btn_clear.setEnabled(True)
        self.progress_bar.setVisible(False)

        ok = sum(1 for v in self.processing_results.values() if v == "Success")
        fail = sum(1 for v in self.processing_results.values() if v == "Failed")
        self.log_message(f"Done: {ok} succeeded, {fail} failed")

        if fail == 0:
            QMessageBox.information(self, t("msg.success"), t("msg.all_done"))
        else:
            self.update_status(f"Completed with {fail} errors", "warning")

    # ── UI Updates ────────────────────────────────────────────────────────────

    def update_progress(self, message: str, progress: float):
        self.progress_bar.setValue(int(progress))
        self.status_label.setText(message)

    def update_status(self, message: str, status_type: str = "info"):
        self.status_label.setText(message)
        colors = {"error": "red", "success": "#2E7D32", "warning": "orange"}
        color = colors.get(status_type, "inherit")
        self.status_label.setStyleSheet(f"QLabel {{ color: {color}; padding: 4px; }}")

    def log_message(self, msg: str):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.processing_log.append(f"[{ts}] {msg}")

    # ── Engine Changes ────────────────────────────────────────────────────────

    def change_engine(self):
        if self._updating_combos:
            return
        engine = self.engine_combo.currentText().lower()
        self.config.set('speech_engine', engine)
        self._update_model_combo()
        # After updating combo, load the first model in list
        model = self.model_combo.currentData()
        if model:
            self._load_speech_engine(engine)

    def change_model(self):
        if self._updating_combos:
            return
        model = self.model_combo.currentData()
        if not model:
            return
        engine = self.engine_combo.currentText().lower()
        key = 'whisper_model' if engine == 'whisper' else 'vosk_model'
        self.config.set(key, model)
        self._load_speech_engine(engine)

    def change_translation_engine(self):
        engine = self.tr_engine_combo.currentText().lower()
        self.config.set('translation_engine', engine)
        self._load_translator(engine)

    # ── Theme ─────────────────────────────────────────────────────────────────

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.config.set('dark_mode', self.dark_mode, auto_save=True)
        theme = 'dark' if self.dark_mode else 'light'
        self.apply_theme(theme)
        self.btn_theme.setText(t("btn.light_mode") if self.dark_mode else t("btn.dark_mode"))

    def apply_theme(self, theme: str):
        palette = QPalette()
        if theme == 'dark':
            palette.setColor(QPalette.Window, QColor(35, 35, 40))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 30))
            palette.setColor(QPalette.AlternateBase, QColor(40, 40, 45))
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(50, 50, 55))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.Highlight, QColor(30, 120, 200))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            self.processing_log.setStyleSheet(
                "QTextEdit { background-color: #1a1a1e; color: #d0d0d0; border: 1px solid #444; }"
            )
        else:
            palette.setColor(QPalette.Window, QColor(245, 245, 248))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.AlternateBase, QColor(240, 240, 244))
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, QColor(240, 240, 244))
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.Highlight, QColor(30, 120, 200))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            self.processing_log.setStyleSheet(
                "QTextEdit { background-color: white; color: black; border: 1px solid #ccc; }"
            )

        QApplication.setPalette(palette)
        self.config.set('ui_theme', theme, auto_save=True)

        if hasattr(self, 'translator_tab'):
            self.translator_tab.apply_theme(theme)
        if hasattr(self, 'video_maker_tab'):
            self.video_maker_tab.apply_theme(theme)


# ─── Legacy runner (kept for compatibility) ──────────────────────────────────

def run_app(config, gpu_info=None):
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    window = SubLabMainWindow(config, gpu_info)
    window.show()
    sys.exit(app.exec_())