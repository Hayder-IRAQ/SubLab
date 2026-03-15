# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# utils/setup_wizard.py
"""
SubLab First-Run Setup Wizard
- Language selection
- FFmpeg auto-download (ffmpeg-master-latest-win64-gpl-shared)
- Python packages verification & install
- Whisper/Vosk model check
"""

import os
import sys
import shutil
import zipfile
import platform
import subprocess
import logging
import urllib.request
from pathlib import Path
from typing import List, Tuple, Optional

from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextEdit, QComboBox,
    QGroupBox, QMessageBox, QApplication, QFrame, QCheckBox,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from utils.i18n import (
    SUPPORTED_LANGUAGES, set_language, get_language, t, is_rtl,
)

logger = logging.getLogger(__name__)

APP_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEPS_DIR = APP_DIR / "deps"
FFMPEG_DIR = DEPS_DIR / "ffmpeg"
MODELS_DIR = APP_DIR / "models"

# FFmpeg download URL — Windows GPL shared build
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
FFMPEG_LINUX_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl-shared.tar.xz"

# Required pip packages grouped by feature
REQUIRED_PACKAGES = {
    "core": [
        ("PyQt5", "PyQt5"),
        ("numpy", "numpy"),
        ("Pillow", "Pillow"),
    ],
    "video": [
        ("cv2", "opencv-python"),
        ("moviepy", "moviepy"),
    ],
    "speech": [
        ("whisper", "openai-whisper"),
    ],
    "translation": [
        ("googletrans", "googletrans==4.0.0-rc.1"),
    ],
    "arabic": [
        ("arabic_reshaper", "arabic-reshaper"),
        ("bidi", "python-bidi"),
    ],
}

# ─── Helper: check if a command exists ────────────────────────────────────────

def _which(name: str) -> Optional[str]:
    return shutil.which(name)


def find_ffmpeg() -> Optional[str]:
    """Find ffmpeg binary — system PATH or bundled."""
    # Check bundled first
    if platform.system() == "Windows":
        bundled = FFMPEG_DIR / "bin" / "ffmpeg.exe"
    else:
        bundled = FFMPEG_DIR / "bin" / "ffmpeg"
    if bundled.exists():
        return str(bundled)
    # Check system
    return _which("ffmpeg")


def find_ffprobe() -> Optional[str]:
    if platform.system() == "Windows":
        bundled = FFMPEG_DIR / "bin" / "ffprobe.exe"
    else:
        bundled = FFMPEG_DIR / "bin" / "ffprobe"
    if bundled.exists():
        return str(bundled)
    return _which("ffprobe")


def check_missing_packages() -> List[Tuple[str, str]]:
    """Return list of (import_name, pip_name) for missing packages."""
    missing = []
    for group_pkgs in REQUIRED_PACKAGES.values():
        for import_name, pip_name in group_pkgs:
            try:
                __import__(import_name)
            except ImportError:
                missing.append((import_name, pip_name))
    return missing


def add_ffmpeg_to_path():
    """Add bundled ffmpeg to PATH if it exists."""
    bin_dir = FFMPEG_DIR / "bin"
    if bin_dir.exists():
        path = os.environ.get("PATH", "")
        if str(bin_dir) not in path:
            os.environ["PATH"] = str(bin_dir) + os.pathsep + path


# ─── Download Worker Thread ──────────────────────────────────────────────────

class _DownloadWorker(QThread):
    progress = pyqtSignal(int, str)  # percent, message
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, task: str, parent=None):
        super().__init__(parent)
        self.task = task  # "ffmpeg" | "pip" | "models"
        self.missing_pkgs: List[Tuple[str, str]] = []

    def run(self):
        try:
            if self.task == "ffmpeg":
                self._install_ffmpeg()
            elif self.task == "pip":
                self._install_pip_packages()
            elif self.task == "models":
                self._download_models()
        except Exception as e:
            logger.error(f"Setup task '{self.task}' failed: {e}", exc_info=True)
            self.finished.emit(False, str(e))

    def _install_ffmpeg(self):
        DEPS_DIR.mkdir(parents=True, exist_ok=True)
        is_win = platform.system() == "Windows"
        url = FFMPEG_URL if is_win else FFMPEG_LINUX_URL
        ext = ".zip" if is_win else ".tar.xz"
        archive_path = DEPS_DIR / f"ffmpeg{ext}"

        self.progress.emit(5, t("setup.installing") + " FFmpeg...")

        # Download with progress
        def _reporthook(block_num, block_size, total_size):
            if total_size > 0:
                pct = min(int(block_num * block_size * 70 / total_size), 70)
                self.progress.emit(5 + pct, f"Downloading FFmpeg... {pct}%")

        urllib.request.urlretrieve(url, str(archive_path), _reporthook)
        self.progress.emit(75, "Extracting FFmpeg...")

        # Extract
        if is_win:
            with zipfile.ZipFile(str(archive_path), 'r') as zf:
                zf.extractall(str(DEPS_DIR))
        else:
            import tarfile
            with tarfile.open(str(archive_path), 'r:xz') as tf:
                tf.extractall(str(DEPS_DIR))

        self.progress.emit(90, "Configuring FFmpeg...")

        # The archive extracts to a subfolder — find and rename it
        extracted = None
        for item in DEPS_DIR.iterdir():
            if item.is_dir() and item.name.startswith("ffmpeg-"):
                extracted = item
                break

        if extracted:
            target = FFMPEG_DIR
            if target.exists():
                shutil.rmtree(target)
            extracted.rename(target)

        # Cleanup archive
        try:
            archive_path.unlink()
        except Exception:
            pass

        add_ffmpeg_to_path()
        self.progress.emit(100, "✅ FFmpeg installed!")
        self.finished.emit(True, "FFmpeg installed successfully")

    def _install_pip_packages(self):
        if not self.missing_pkgs:
            self.finished.emit(True, "No packages to install")
            return

        total = len(self.missing_pkgs)
        for i, (import_name, pip_name) in enumerate(self.missing_pkgs):
            pct = int((i / total) * 90) + 5
            self.progress.emit(pct, f"Installing {pip_name}...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pip_name, "-q"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    timeout=300,
                )
            except subprocess.CalledProcessError as e:
                self.finished.emit(False, f"Failed to install {pip_name}: {e}")
                return
            except subprocess.TimeoutExpired:
                self.finished.emit(False, f"Timeout installing {pip_name}")
                return

        self.progress.emit(100, "✅ All packages installed!")
        self.finished.emit(True, "All packages installed")

    def _download_models(self):
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        (MODELS_DIR / "whisper").mkdir(exist_ok=True)
        (MODELS_DIR / "vosk").mkdir(exist_ok=True)

        self.progress.emit(50, "Models directory prepared")
        # Whisper models download on first use (handled by openai-whisper).
        # We just ensure directories exist.
        self.progress.emit(100, "✅ Models directory ready!")
        self.finished.emit(True, "Models directory configured")


# ═══════════════════════════════════════════════════════════════════════════════
# Wizard Pages
# ═══════════════════════════════════════════════════════════════════════════════

class LanguagePage(QWizardPage):
    """Page 1: Select interface language."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Logo / welcome
        logo = QLabel("🎬 SubLab")
        logo.setFont(QFont("Arial", 28, QFont.Bold))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        welcome = QLabel("Welcome • مرحباً • Добро пожаловать • 欢迎")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(QFont("Arial", 12))
        welcome.setStyleSheet("color: gray;")
        layout.addWidget(welcome)

        layout.addSpacing(20)

        # Language selector
        lbl = QLabel("Select Interface Language / اختر لغة الواجهة:")
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        self.lang_combo = QComboBox()
        self.lang_combo.setFixedWidth(300)
        self.lang_combo.setFixedHeight(36)
        self.lang_combo.setFont(QFont("Arial", 12))
        for code, name in SUPPORTED_LANGUAGES:
            flag = {
                "en": "🇬🇧", "ar": "🇸🇦", "ru": "🇷🇺", "fr": "🇫🇷", "de": "🇩🇪",
                "es": "🇪🇸", "pt": "🇧🇷", "zh": "🇨🇳", "ja": "🇯🇵", "ko": "🇰🇷",
            }.get(code, "🌐")
            self.lang_combo.addItem(f"{flag}  {name}", code)

        # Default to saved or system
        saved = self.config.get("ui_language", "en")
        idx = self.lang_combo.findData(saved)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.lang_combo)
        hbox.addStretch()
        layout.addLayout(hbox)
        layout.addStretch()

    def validatePage(self):
        code = self.lang_combo.currentData()
        set_language(code)
        self.config.set("ui_language", code, auto_save=True)
        return True


class DependencyPage(QWizardPage):
    """Page 2: Check and install FFmpeg + pip packages + models."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._worker: Optional[_DownloadWorker] = None
        self._ffmpeg_ok = False
        self._pip_ok = False
        self._models_ok = False
        self._missing_pkgs: List[Tuple[str, str]] = []
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.title_lbl = QLabel("🔍 Checking Dependencies...")
        self.title_lbl.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_lbl)

        layout.addSpacing(10)

        # ── FFmpeg ──
        ffmpeg_group = QGroupBox("FFmpeg")
        fg_layout = QVBoxLayout()
        self.ffmpeg_status = QLabel("⏳ Checking...")
        self.ffmpeg_status.setFont(QFont("Arial", 11))
        fg_layout.addWidget(self.ffmpeg_status)
        self.btn_ffmpeg = QPushButton("⬇️ Install FFmpeg")
        self.btn_ffmpeg.setFixedHeight(34)
        self.btn_ffmpeg.setVisible(False)
        self.btn_ffmpeg.setStyleSheet(
            "QPushButton{background:#1565C0;color:white;border-radius:4px;font-weight:bold;}"
            "QPushButton:hover{background:#0D47A1;}"
        )
        self.btn_ffmpeg.clicked.connect(self._install_ffmpeg)
        fg_layout.addWidget(self.btn_ffmpeg)
        ffmpeg_group.setLayout(fg_layout)
        layout.addWidget(ffmpeg_group)

        # ── Pip Packages ──
        pip_group = QGroupBox("Python Packages")
        pg_layout = QVBoxLayout()
        self.pip_status = QLabel("⏳ Checking...")
        self.pip_status.setFont(QFont("Arial", 11))
        pg_layout.addWidget(self.pip_status)
        self.btn_pip = QPushButton("⬇️ Install Packages")
        self.btn_pip.setFixedHeight(34)
        self.btn_pip.setVisible(False)
        self.btn_pip.setStyleSheet(
            "QPushButton{background:#2E7D32;color:white;border-radius:4px;font-weight:bold;}"
            "QPushButton:hover{background:#1B5E20;}"
        )
        self.btn_pip.clicked.connect(self._install_pip)
        pg_layout.addWidget(self.btn_pip)
        pip_group.setLayout(pg_layout)
        layout.addWidget(pip_group)

        # ── Models ──
        models_group = QGroupBox("Models")
        mg_layout = QVBoxLayout()
        self.models_status = QLabel("⏳ Checking...")
        self.models_status.setFont(QFont("Arial", 11))
        mg_layout.addWidget(self.models_status)
        self.btn_models = QPushButton("📁 Prepare Models Directory")
        self.btn_models.setFixedHeight(34)
        self.btn_models.setVisible(False)
        self.btn_models.setStyleSheet(
            "QPushButton{background:#E65100;color:white;border-radius:4px;font-weight:bold;}"
            "QPushButton:hover{background:#BF360C;}"
        )
        self.btn_models.clicked.connect(self._prepare_models)
        mg_layout.addWidget(self.btn_models)
        models_group.setLayout(mg_layout)
        layout.addWidget(models_group)

        # ── Progress ──
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        # ── Log ──
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(120)
        self.log.setStyleSheet("font-size:10px;font-family:Consolas;")
        layout.addWidget(self.log)

    def initializePage(self):
        """Called when page becomes visible — run checks."""
        self._update_texts()
        self._check_all()

    def _update_texts(self):
        self.title_lbl.setText(f"🔍 {t('setup.checking')}")

    def _log(self, msg: str):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.append(f"[{ts}] {msg}")

    # ── Checks ────────────────────────────────────────────────────────────────

    def _check_all(self):
        self._check_ffmpeg()
        self._check_pip()
        self._check_models()

    def _check_ffmpeg(self):
        ffpath = find_ffmpeg()
        if ffpath:
            self._ffmpeg_ok = True
            self.ffmpeg_status.setText(t("setup.ffmpeg_ok") + f"  ({ffpath})")
            self.ffmpeg_status.setStyleSheet("color: #2E7D32;")
            self.btn_ffmpeg.setVisible(False)
            self._log(f"FFmpeg: {ffpath}")
        else:
            self._ffmpeg_ok = False
            self.ffmpeg_status.setText(t("setup.ffmpeg_missing"))
            self.ffmpeg_status.setStyleSheet("color: #C62828;")
            self.btn_ffmpeg.setVisible(True)
            self.btn_ffmpeg.setText(f"⬇️ {t('setup.install')} FFmpeg")
            self._log("FFmpeg not found")
        self.completeChanged.emit()

    def _check_pip(self):
        self._missing_pkgs = check_missing_packages()
        if not self._missing_pkgs:
            self._pip_ok = True
            self.pip_status.setText(t("setup.pip_ok"))
            self.pip_status.setStyleSheet("color: #2E7D32;")
            self.btn_pip.setVisible(False)
            self._log("All Python packages OK")
        else:
            self._pip_ok = False
            names = ", ".join(p[1] for p in self._missing_pkgs)
            self.pip_status.setText(t("setup.pip_missing", pkgs=names))
            self.pip_status.setStyleSheet("color: #C62828;")
            self.btn_pip.setVisible(True)
            self.btn_pip.setText(f"⬇️ {t('setup.install')} ({len(self._missing_pkgs)} packages)")
            self._log(f"Missing: {names}")
        self.completeChanged.emit()

    def _check_models(self):
        whisper_dir = MODELS_DIR / "whisper"
        vosk_dir = MODELS_DIR / "vosk"
        if whisper_dir.exists() and vosk_dir.exists():
            self._models_ok = True
            self.models_status.setText("✅ Models directory ready")
            self.models_status.setStyleSheet("color: #2E7D32;")
            self.btn_models.setVisible(False)
            self._log("Models directory OK")
        else:
            self._models_ok = False
            self.models_status.setText("📁 Models directory needs setup")
            self.models_status.setStyleSheet("color: #E65100;")
            self.btn_models.setVisible(True)
            self._log("Models directory not found")
        self.completeChanged.emit()

    # ── Install Actions ───────────────────────────────────────────────────────

    def _install_ffmpeg(self):
        self.btn_ffmpeg.setEnabled(False)
        self.btn_ffmpeg.setText(t("setup.installing"))
        self.progress.setVisible(True)
        self.progress.setValue(0)

        self._worker = _DownloadWorker("ffmpeg")
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_ffmpeg_done)
        self._worker.start()

    def _install_pip(self):
        self.btn_pip.setEnabled(False)
        self.btn_pip.setText(t("setup.installing"))
        self.progress.setVisible(True)
        self.progress.setValue(0)

        self._worker = _DownloadWorker("pip")
        self._worker.missing_pkgs = self._missing_pkgs
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_pip_done)
        self._worker.start()

    def _prepare_models(self):
        self.btn_models.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)

        self._worker = _DownloadWorker("models")
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_models_done)
        self._worker.start()

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_progress(self, pct: int, msg: str):
        self.progress.setValue(pct)
        self.progress.setFormat(f"{msg}  ({pct}%)")
        self._log(msg)

    def _on_ffmpeg_done(self, success: bool, msg: str):
        if success:
            self._log("✅ " + msg)
            self._check_ffmpeg()
        else:
            self._log("❌ " + msg)
            self.btn_ffmpeg.setEnabled(True)
            self.btn_ffmpeg.setText(f"⬇️ {t('setup.install')} FFmpeg (retry)")
            QMessageBox.warning(self, t("msg.error"), msg)
        self.progress.setVisible(False)

    def _on_pip_done(self, success: bool, msg: str):
        if success:
            self._log("✅ " + msg)
            self._check_pip()
        else:
            self._log("❌ " + msg)
            self.btn_pip.setEnabled(True)
            self.btn_pip.setText(f"⬇️ {t('setup.install')} (retry)")
            QMessageBox.warning(self, t("msg.error"), msg)
        self.progress.setVisible(False)

    def _on_models_done(self, success: bool, msg: str):
        if success:
            self._log("✅ " + msg)
            self._check_models()
        else:
            self._log("❌ " + msg)
            self.btn_models.setEnabled(True)
            QMessageBox.warning(self, t("msg.error"), msg)
        self.progress.setVisible(False)

    def isComplete(self):
        # Allow continuing even if not everything installed (user can skip)
        return True


class SummaryPage(QWizardPage):
    """Page 3: Summary and launch."""

    def __init__(self, dep_page: DependencyPage, parent=None):
        super().__init__(parent)
        self.dep_page = dep_page
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl = QLabel(f"🎬 SubLab")
        lbl.setFont(QFont("Arial", 22, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        self.summary_lbl = QLabel()
        self.summary_lbl.setFont(QFont("Arial", 12))
        self.summary_lbl.setAlignment(Qt.AlignCenter)
        self.summary_lbl.setWordWrap(True)
        layout.addWidget(self.summary_lbl)

        layout.addStretch()

        self.done_lbl = QLabel(t("setup.done"))
        self.done_lbl.setFont(QFont("Arial", 14, QFont.Bold))
        self.done_lbl.setAlignment(Qt.AlignCenter)
        self.done_lbl.setStyleSheet("color: #2E7D32;")
        layout.addWidget(self.done_lbl)

        layout.addStretch()

    def initializePage(self):
        items = []
        items.append(f"✅ Language: {get_language().upper()}")
        items.append("✅ FFmpeg" if self.dep_page._ffmpeg_ok else "⚠️ FFmpeg (not installed)")
        items.append("✅ Python packages" if self.dep_page._pip_ok else "⚠️ Some packages missing")
        items.append("✅ Models directory" if self.dep_page._models_ok else "⚠️ Models not configured")
        self.summary_lbl.setText("\n".join(items))
        self.done_lbl.setText(t("setup.done"))


# ═══════════════════════════════════════════════════════════════════════════════
# Main Wizard
# ═══════════════════════════════════════════════════════════════════════════════

class SetupWizard(QWizard):
    """First-run setup wizard for SubLab."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config

        self.setWindowTitle("SubLab — Setup")
        self.setFixedSize(620, 560)
        self.setWizardStyle(QWizard.ModernStyle)

        # Pages
        self.lang_page = LanguagePage(config)
        self.dep_page = DependencyPage(config)
        self.summary_page = SummaryPage(self.dep_page)

        self.addPage(self.lang_page)
        self.addPage(self.dep_page)
        self.addPage(self.summary_page)

        # Button text
        self.setButtonText(QWizard.NextButton, "Next →")
        self.setButtonText(QWizard.BackButton, "← Back")
        self.setButtonText(QWizard.FinishButton, "🚀 Launch SubLab")
        self.setButtonText(QWizard.CancelButton, t("setup.skip"))


def needs_setup(config) -> bool:
    """Check if first-run setup is needed."""
    if config.get("setup_completed", False):
        # Even if completed before, verify ffmpeg still exists
        if find_ffmpeg():
            return False
        # FFmpeg disappeared — re-run setup
        return True
    return True


def run_setup_wizard(config) -> bool:
    """
    Show setup wizard. Returns True if user completed it, False if cancelled.
    """
    wizard = SetupWizard(config)
    result = wizard.exec_()
    if result == QWizard.Accepted:
        config.set("setup_completed", True, auto_save=True)
        add_ffmpeg_to_path()
        return True
    else:
        # User skipped — still try to add ffmpeg if it exists
        add_ffmpeg_to_path()
        return False
