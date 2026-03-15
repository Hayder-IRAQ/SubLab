# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# ui/video_maker_tab.py
"""Video Maker Tab — Unlimited SRT tracks — Full i18n support"""

import os
import threading
import logging
from pathlib import Path
from typing import Optional, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QComboBox, QProgressBar, QTextEdit,
    QGroupBox, QMessageBox, QSizePolicy, QScrollArea, QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont

from utils.i18n import t

logger = logging.getLogger(__name__)

_TRACK_COLORS = [
    "#1565C0", "#7B1FA2", "#00695C", "#E65100",
    "#AD1457", "#00838F", "#4E342E", "#283593",
    "#1B5E20", "#BF360C", "#4A148C", "#006064",
]


class VideoMakerSignals(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    log = pyqtSignal(str)


class _SrtTrackRow(QFrame):
    """Single SRT track row"""
    remove_requested = pyqtSignal(object)
    file_changed = pyqtSignal()

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.file_path: Optional[str] = None
        self._color = _TRACK_COLORS[index % len(_TRACK_COLORS)]
        self._build()

    def _build(self):
        self.setFrameShape(QFrame.NoFrame)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        self.lbl_num = QLabel(f"  SRT {self.index + 1}  ")
        self.lbl_num.setFixedWidth(70)
        self.lbl_num.setAlignment(Qt.AlignCenter)
        self._apply_color_style()
        layout.addWidget(self.lbl_num)

        self.lbl_file = QLabel(t("vm_tab.no_file_selected"))
        self.lbl_file.setStyleSheet("color: gray; font-style: italic; font-size: 11px;")
        self.lbl_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.lbl_file)

        self.btn_choose = QPushButton(t("vm_tab.choose"))
        self.btn_choose.setFixedWidth(90)
        self.btn_choose.setCursor(Qt.PointingHandCursor)
        self.btn_choose.clicked.connect(self._choose_file)
        layout.addWidget(self.btn_choose)

        self.btn_remove = QPushButton("✕")
        self.btn_remove.setFixedSize(28, 28)
        self.btn_remove.setCursor(Qt.PointingHandCursor)
        self.btn_remove.setToolTip(t("vm_tab.remove_track_tooltip"))
        self.btn_remove.setStyleSheet("""
            QPushButton {
                background-color: #C62828; color: white;
                border-radius: 14px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #B71C1C; }
        """)
        self.btn_remove.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(self.btn_remove)

    def _apply_color_style(self):
        c = self._color
        self.lbl_num.setStyleSheet(f"""
            background-color: {c}; color: white; border-radius: 4px;
            font-weight: bold; font-size: 11px; padding: 3px;
        """)

    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("vm_tab.choose_srt", n=self.index + 1), "",
            "SRT Files (*.srt);;All Files (*.*)"
        )
        if path:
            self.file_path = path
            self.lbl_file.setText(Path(path).name)
            self.lbl_file.setStyleSheet("color: #2E7D32; font-weight: bold; font-size: 11px;")
            self.file_changed.emit()

    def update_index(self, new_index):
        self.index = new_index
        self._color = _TRACK_COLORS[new_index % len(_TRACK_COLORS)]
        self.lbl_num.setText(f"  SRT {new_index + 1}  ")
        self._apply_color_style()

    def refresh_texts(self):
        """Refresh i18n texts"""
        if not self.file_path:
            self.lbl_file.setText(t("vm_tab.no_file_selected"))
        self.btn_choose.setText(t("vm_tab.choose"))
        self.btn_remove.setToolTip(t("vm_tab.remove_track_tooltip"))


class VideoMakerTab(QWidget):
    """Video maker tab — fully internationalized"""

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.signals = VideoMakerSignals()
        self._is_generating = False
        self.audio_path: Optional[str] = None
        self.output_path: Optional[str] = None
        self._srt_rows: List[_SrtTrackRow] = []

        self._build_ui()
        self._connect_signals()

        for _ in range(3):
            self._add_srt_track()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self._title_label = QLabel(t("vm_tab.title"))
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self._title_label)

        self._desc_label = QLabel(t("vm_tab.description"))
        self._desc_label.setAlignment(Qt.AlignCenter)
        self._desc_label.setStyleSheet("color: gray; font-size: 11px;")
        self._desc_label.setWordWrap(True)
        layout.addWidget(self._desc_label)

        # Audio
        self._audio_group = QGroupBox(t("vm_tab.audio_file"))
        audio_layout = QHBoxLayout()
        self.lbl_audio = QLabel(t("vm_tab.no_file_selected"))
        self.lbl_audio.setStyleSheet("color: gray; font-style: italic;")
        self.lbl_audio.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.btn_audio = QPushButton(t("vm_tab.choose"))
        self.btn_audio.setFixedWidth(100)
        audio_layout.addWidget(self.lbl_audio)
        audio_layout.addWidget(self.btn_audio)
        self._audio_group.setLayout(audio_layout)
        layout.addWidget(self._audio_group)

        # SRT Tracks
        self._srt_group = QGroupBox(t("vm_tab.srt_files"))
        srt_outer = QVBoxLayout()

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setMinimumHeight(60)
        self._scroll.setMaximumHeight(260)

        self._tracks_container = QWidget()
        self._tracks_layout = QVBoxLayout(self._tracks_container)
        self._tracks_layout.setContentsMargins(0, 0, 0, 0)
        self._tracks_layout.setSpacing(4)
        self._tracks_layout.addStretch()

        self._scroll.setWidget(self._tracks_container)
        srt_outer.addWidget(self._scroll)

        add_row = QHBoxLayout()
        self.btn_add_track = QPushButton(t("vm_tab.add_srt_track"))
        self.btn_add_track.setCursor(Qt.PointingHandCursor)
        self.btn_add_track.setFixedHeight(34)
        self.btn_add_track.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32; color: white;
                border-radius: 6px; font-weight: bold; font-size: 12px;
                padding: 0 16px;
            }
            QPushButton:hover { background-color: #1B5E20; }
        """)
        self.lbl_track_count = QLabel("")
        self.lbl_track_count.setStyleSheet("color: gray; font-size: 10px;")
        add_row.addStretch()
        add_row.addWidget(self.btn_add_track)
        add_row.addWidget(self.lbl_track_count)
        add_row.addStretch()
        srt_outer.addLayout(add_row)

        self._srt_group.setLayout(srt_outer)
        layout.addWidget(self._srt_group)

        # Settings
        self._settings_group = QGroupBox(t("vm_tab.video_settings"))
        settings_layout = QVBoxLayout()

        style_row = QHBoxLayout()
        self._lbl_style = QLabel(t("vm_tab.video_style"))
        style_row.addWidget(self._lbl_style)
        self.style_combo = QComboBox()
        self.style_combo.addItem(t("vm_tab.style_default"), "default")
        self.style_combo.addItem(t("vm_tab.style_dark"), "dark")
        self.style_combo.addItem(t("vm_tab.style_cinema"), "cinema")
        self.style_combo.addItem(t("vm_tab.style_minimal"), "minimal")
        self.style_combo.setFixedWidth(200)
        style_row.addWidget(self.style_combo)
        style_row.addStretch()
        settings_layout.addLayout(style_row)

        out_row = QHBoxLayout()
        self._lbl_output = QLabel(t("vm_tab.output_file"))
        out_row.addWidget(self._lbl_output)
        self.lbl_output = QLabel("output_video.mp4")
        self.lbl_output.setStyleSheet("color: #1565C0; font-weight: bold;")
        self.lbl_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.btn_output = QPushButton(t("vm_tab.browse"))
        self.btn_output.setFixedWidth(100)
        out_row.addWidget(self.lbl_output)
        out_row.addWidget(self.btn_output)
        settings_layout.addLayout(out_row)

        self._settings_group.setLayout(settings_layout)
        layout.addWidget(self._settings_group)

        # Generate
        self.btn_generate = QPushButton(t("vm_tab.generate_video"))
        self.btn_generate.setFixedHeight(50)
        self.btn_generate.setFont(QFont("Arial", 13, QFont.Bold))
        self.btn_generate.setStyleSheet("""
            QPushButton { background-color: #E53935; color: white; border-radius: 8px; }
            QPushButton:hover { background-color: #C62828; }
            QPushButton:disabled { background-color: #9E9E9E; }
        """)
        self.btn_generate.setEnabled(False)
        layout.addWidget(self.btn_generate)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Log
        self._log_group = QGroupBox(t("vm_tab.operations_log"))
        log_layout = QVBoxLayout()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(120)
        self.log_box.setStyleSheet("font-size: 10px; font-family: Consolas;")
        log_layout.addWidget(self.log_box)
        self._log_group.setLayout(log_layout)
        layout.addWidget(self._log_group)

    def _connect_signals(self):
        self.btn_audio.clicked.connect(self._choose_audio)
        self.btn_output.clicked.connect(self._choose_output)
        self.btn_generate.clicked.connect(self._start_generation)
        self.btn_add_track.clicked.connect(self._add_srt_track)
        self.signals.progress.connect(self._on_progress)
        self.signals.finished.connect(self._on_finished)
        self.signals.log.connect(self._append_log)

    # ── Public: refresh all texts ──
    def refresh_texts(self):
        self._title_label.setText(t("vm_tab.title"))
        self._desc_label.setText(t("vm_tab.description"))
        self._audio_group.setTitle(t("vm_tab.audio_file"))
        if not self.audio_path:
            self.lbl_audio.setText(t("vm_tab.no_file_selected"))
        self.btn_audio.setText(t("vm_tab.choose"))
        self._srt_group.setTitle(t("vm_tab.srt_files"))
        self.btn_add_track.setText(t("vm_tab.add_srt_track"))
        self._settings_group.setTitle(t("vm_tab.video_settings"))
        self._lbl_style.setText(t("vm_tab.video_style"))
        self.style_combo.setItemText(0, t("vm_tab.style_default"))
        self.style_combo.setItemText(1, t("vm_tab.style_dark"))
        self.style_combo.setItemText(2, t("vm_tab.style_cinema"))
        self.style_combo.setItemText(3, t("vm_tab.style_minimal"))
        self._lbl_output.setText(t("vm_tab.output_file"))
        self.btn_output.setText(t("vm_tab.browse"))
        if not self._is_generating:
            self.btn_generate.setText(t("vm_tab.generate_video"))
        self._log_group.setTitle(t("vm_tab.operations_log"))
        self._update_track_count()
        for row in self._srt_rows:
            row.refresh_texts()

    # ── Track Management ──
    def _add_srt_track(self):
        idx = len(self._srt_rows)
        row = _SrtTrackRow(idx)
        row.remove_requested.connect(self._remove_srt_track)
        row.file_changed.connect(self._check_ready)

        self._tracks_layout.insertWidget(self._tracks_layout.count() - 1, row)
        self._srt_rows.append(row)
        self._update_track_count()
        self._check_ready()
        self._append_log(t("vm_tab.added_track", n=idx + 1))
        self._scroll.ensureWidgetVisible(row)

    def _remove_srt_track(self, row):
        if len(self._srt_rows) <= 1:
            QMessageBox.warning(self, t("tr_tab.warning"), t("vm_tab.min_one_track"))
            return

        self._srt_rows.remove(row)
        self._tracks_layout.removeWidget(row)
        row.deleteLater()

        for i, r in enumerate(self._srt_rows):
            r.update_index(i)

        self._update_track_count()
        self._check_ready()
        self._append_log(t("vm_tab.removed_track", n=len(self._srt_rows)))

    def _update_track_count(self):
        n = len(self._srt_rows)
        filled = sum(1 for r in self._srt_rows if r.file_path)
        self.lbl_track_count.setText(t("vm_tab.track_count", filled=filled, total=n))

    def _choose_audio(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("vm_tab.choose_audio"), "",
            "Audio Files (*.mp3 *.wav *.m4a *.aac *.ogg *.flac);;All Files (*.*)"
        )
        if path:
            self.audio_path = path
            self.lbl_audio.setText(Path(path).name)
            self.lbl_audio.setStyleSheet("color: #1565C0; font-weight: bold;")
            self._append_log(t("vm_tab.audio_selected", name=Path(path).name))
            self._check_ready()

    def _choose_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("vm_tab.save_video"), "output_video.mp4", "MP4 Video (*.mp4)"
        )
        if path:
            self.output_path = path
            self.lbl_output.setText(Path(path).name)
            self._check_ready()

    def _check_ready(self):
        ready = (
            self.audio_path is not None
            and len(self._srt_rows) >= 1
            and all(r.file_path is not None for r in self._srt_rows)
        )
        self.btn_generate.setEnabled(ready)
        self._update_track_count()

    def _start_generation(self):
        if self._is_generating:
            return
        srt_paths = [r.file_path for r in self._srt_rows]
        output = self.output_path or "output_video.mp4"

        self._is_generating = True
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText(t("vm_tab.generating"))
        self.btn_add_track.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        style_key = self.style_combo.currentData()
        thread = threading.Thread(
            target=self._generate_worker,
            args=(self.audio_path, srt_paths, output, style_key),
            daemon=True,
        )
        thread.start()

    def _generate_worker(self, audio, srts, output, style_key):
        try:
            n = len(srts)
            self.signals.log.emit(f"🔄 {n} tracks...")

            from ui.video_generator import VideoGenerator, STYLE_PRESETS
            style = STYLE_PRESETS.get(style_key)

            def progress_cb(msg, pct=None):
                if pct is not None:
                    self.signals.progress.emit(int(pct), msg)
                self.signals.log.emit(msg)

            gen = VideoGenerator(
                audio_path=audio, srt_paths=srts,
                output_path=output, style=style,
                progress_callback=progress_cb,
            )
            gen.create()
            self.signals.finished.emit(True, output)
        except Exception as e:
            logger.error(f"Video generation error: {e}", exc_info=True)
            self.signals.log.emit(f"❌ {e}")
            self.signals.finished.emit(False, str(e))

    def _on_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"{msg}  ({pct}%)")

    def _on_finished(self, success, result):
        self._is_generating = False
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText(t("vm_tab.generate_video"))
        self.btn_add_track.setEnabled(True)

        if success:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat(t("vm_tab.generation_complete"))
            self._append_log(f"✅ {result}")
            QMessageBox.information(self, t("msg.success"), t("vm_tab.video_saved", path=result))
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat(t("vm_tab.generation_failed"))
            QMessageBox.critical(self, t("msg.error"), t("vm_tab.video_failed_msg", error=result))

    def _append_log(self, msg):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.append(f"[{ts}] {msg}")
        sb = self.log_box.verticalScrollBar()
        sb.setValue(sb.maximum())

    def apply_theme(self, theme):
        if theme == 'dark':
            self.log_box.setStyleSheet(
                "background: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 10px;"
            )
        else:
            self.log_box.setStyleSheet("font-size: 10px; font-family: Consolas;")
