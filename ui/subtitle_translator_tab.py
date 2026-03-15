# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# ui/subtitle_translator_tab.py
"""Subtitle File Translator Tab (SRT / CSV / TXT) — Full i18n support"""

import os
import re
import csv
import logging
import threading
from pathlib import Path
from typing import List, Dict, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QComboBox, QProgressBar, QTextEdit,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox,
    QCheckBox, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor

from utils.i18n import t

logger = logging.getLogger(__name__)


class TranslatorSignals(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    log = pyqtSignal(str)


class SubtitleFileHandler:
    """Read/write SRT / CSV / TXT files"""

    @staticmethod
    def read_srt(path: str) -> List[Dict]:
        subtitles = []
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            blocks = re.split(r'\n\s*\n', content.strip())
            for block in blocks:
                lines = block.strip().splitlines()
                if len(lines) < 3:
                    continue
                try:
                    index = int(lines[0].strip())
                    timecode = lines[1].strip()
                    text = ' '.join(line.strip() for line in lines[2:])
                    match = re.match(
                        r'(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})',
                        timecode
                    )
                    if match:
                        subtitles.append({
                            'index': index,
                            'start': match.group(1),
                            'end': match.group(2),
                            'text': text,
                        })
                except (ValueError, IndexError):
                    continue
        except Exception as e:
            logger.error(f"SRT read error: {e}")
        return subtitles

    @staticmethod
    def read_csv(path: str) -> List[Dict]:
        subtitles = []
        try:
            with open(path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    text = row.get('text') or row.get('Text') or row.get('transcript') or ''
                    if text:
                        subtitles.append({
                            'index': i,
                            'start': row.get('start_time', row.get('start', '')),
                            'end': row.get('end_time', row.get('end', '')),
                            'text': text.strip(),
                            '_row': row,
                        })
        except Exception as e:
            logger.error(f"CSV read error: {e}")
        return subtitles

    @staticmethod
    def read_txt(path: str) -> List[Dict]:
        subtitles = []
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            for i, line in enumerate(lines, 1):
                subtitles.append({'index': i, 'start': '', 'end': '', 'text': line})
        except Exception as e:
            logger.error(f"TXT read error: {e}")
        return subtitles

    @staticmethod
    def write_srt(subtitles, path, use_translated=True):
        with open(path, 'w', encoding='utf-8') as f:
            for sub in subtitles:
                text = sub.get('translated_text', sub['text']) if use_translated else sub['text']
                f.write(f"{sub['index']}\n{sub['start']} --> {sub['end']}\n{text}\n\n")

    @staticmethod
    def write_csv(subtitles, path, use_translated=True):
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['index', 'start_time', 'end_time', 'original_text', 'translated_text']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for sub in subtitles:
                writer.writerow({
                    'index': sub['index'],
                    'start_time': sub.get('start', ''),
                    'end_time': sub.get('end', ''),
                    'original_text': sub['text'],
                    'translated_text': sub.get('translated_text', sub['text']) if use_translated else sub['text'],
                })

    @staticmethod
    def write_txt(subtitles, path, use_translated=True):
        with open(path, 'w', encoding='utf-8') as f:
            for sub in subtitles:
                text = sub.get('translated_text', sub['text']) if use_translated else sub['text']
                f.write(text + '\n')


class SubtitleTranslatorTab(QWidget):
    """Subtitle file translator tab — fully internationalized"""

    LANGUAGES = [
        ('ar', 'العربية'), ('en', 'English'), ('fr', 'Français'),
        ('de', 'Deutsch'), ('es', 'Español'), ('it', 'Italiano'),
        ('pt', 'Português'), ('ru', 'Русский'), ('zh-cn', '中文 (简体)'),
        ('ja', '日本語'), ('ko', '한국어'), ('tr', 'Türkçe'),
        ('nl', 'Nederlands'), ('pl', 'Polski'), ('sv', 'Svenska'),
        ('hi', 'हिन्दी'), ('uk', 'Українська'), ('he', 'עברית'),
    ]

    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.handler = SubtitleFileHandler()
        self.signals = TranslatorSignals()
        self.loaded_subtitles: List[Dict] = []
        self.current_file_path: str = ''
        self._is_translating = False

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title
        self._title_label = QLabel(t("tr_tab.title"))
        self._title_label.setAlignment(Qt.AlignCenter)
        self._title_label.setFont(QFont("Arial", 15, QFont.Bold))
        layout.addWidget(self._title_label)

        self._desc_label = QLabel(t("tr_tab.description"))
        self._desc_label.setAlignment(Qt.AlignCenter)
        self._desc_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self._desc_label)

        # Source file group
        self._file_group = QGroupBox(t("tr_tab.source_file"))
        file_layout = QVBoxLayout()

        file_row = QHBoxLayout()
        self.lbl_file = QLabel(t("tr_tab.no_file_selected"))
        self.lbl_file.setStyleSheet("color: gray; font-style: italic;")
        self.btn_choose_file = QPushButton(t("tr_tab.choose_file"))
        self.btn_choose_file.setFixedWidth(120)
        file_row.addWidget(self.lbl_file, 1)
        file_row.addWidget(self.btn_choose_file)
        file_layout.addLayout(file_row)

        self.lbl_file_info = QLabel("")
        self.lbl_file_info.setStyleSheet("color: #888; font-size: 10px;")
        file_layout.addWidget(self.lbl_file_info)

        self._file_group.setLayout(file_layout)
        layout.addWidget(self._file_group)

        # Translation settings group
        self._settings_group = QGroupBox(t("tr_tab.translation_settings"))
        settings_layout = QVBoxLayout()

        engine_row = QHBoxLayout()
        self._lbl_engine = QLabel(t("tr_tab.translation_engine"))
        engine_row.addWidget(self._lbl_engine)
        self.engine_combo = QComboBox()
        self.engine_combo.addItem(t("tr_tab.google_online"), "google")
        self.engine_combo.addItem(t("tr_tab.argos_offline"), "argos")
        self.engine_combo.setFixedWidth(250)
        engine_row.addWidget(self.engine_combo)
        engine_row.addStretch()
        settings_layout.addLayout(engine_row)

        lang_row = QHBoxLayout()
        self._lbl_translate_to = QLabel(t("tr_tab.translate_to"))
        lang_row.addWidget(self._lbl_translate_to)
        self.lang_combo = QComboBox()
        for code, name in self.LANGUAGES:
            self.lang_combo.addItem(name, code)
        self.lang_combo.setFixedWidth(200)
        lang_row.addWidget(self.lang_combo)
        lang_row.addStretch()
        settings_layout.addLayout(lang_row)

        format_row = QHBoxLayout()
        self._lbl_save_as = QLabel(t("tr_tab.save_as"))
        format_row.addWidget(self._lbl_save_as)
        self.chk_srt = QCheckBox("SRT")
        self.chk_csv = QCheckBox("CSV")
        self.chk_txt = QCheckBox("TXT")
        self.chk_srt.setChecked(True)
        format_row.addWidget(self.chk_srt)
        format_row.addWidget(self.chk_csv)
        format_row.addWidget(self.chk_txt)
        format_row.addStretch()
        settings_layout.addLayout(format_row)

        self._settings_group.setLayout(settings_layout)
        layout.addWidget(self._settings_group)

        # Preview
        self._preview_group = QGroupBox(t("tr_tab.content_preview"))
        preview_layout = QVBoxLayout()
        self.preview_list = QListWidget()
        self.preview_list.setMaximumHeight(180)
        self.preview_list.setStyleSheet("font-size: 11px;")
        preview_layout.addWidget(self.preview_list)
        self._preview_group.setLayout(preview_layout)
        layout.addWidget(self._preview_group)

        # Translate button
        self.btn_translate = QPushButton(t("tr_tab.start_translation"))
        self.btn_translate.setFixedHeight(45)
        self.btn_translate.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_translate.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; border-radius: 8px; }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:disabled { background-color: #9E9E9E; }
        """)
        self.btn_translate.setEnabled(False)
        layout.addWidget(self.btn_translate)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Log
        self._log_group = QGroupBox(t("tr_tab.operations_log"))
        log_layout = QVBoxLayout()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(130)
        self.log_box.setStyleSheet("font-size: 10px; font-family: Consolas;")
        log_layout.addWidget(self.log_box)
        self._log_group.setLayout(log_layout)
        layout.addWidget(self._log_group)

    def _connect_signals(self):
        self.btn_choose_file.clicked.connect(self._choose_file)
        self.btn_translate.clicked.connect(self._start_translation)
        self.signals.progress.connect(self._on_progress)
        self.signals.finished.connect(self._on_finished)
        self.signals.log.connect(self._append_log)

    # ── Public: refresh all texts (called from main_window on language change) ──
    def refresh_texts(self):
        self._title_label.setText(t("tr_tab.title"))
        self._desc_label.setText(t("tr_tab.description"))
        self._file_group.setTitle(t("tr_tab.source_file"))
        if not self.current_file_path:
            self.lbl_file.setText(t("tr_tab.no_file_selected"))
        self.btn_choose_file.setText(t("tr_tab.choose_file"))
        self._settings_group.setTitle(t("tr_tab.translation_settings"))
        self._lbl_engine.setText(t("tr_tab.translation_engine"))
        # Update engine combo texts
        self.engine_combo.setItemText(0, t("tr_tab.google_online"))
        self.engine_combo.setItemText(1, t("tr_tab.argos_offline"))
        self._lbl_translate_to.setText(t("tr_tab.translate_to"))
        self._lbl_save_as.setText(t("tr_tab.save_as"))
        self._preview_group.setTitle(t("tr_tab.content_preview"))
        if not self._is_translating:
            self.btn_translate.setText(t("tr_tab.start_translation"))
        self._log_group.setTitle(t("tr_tab.operations_log"))

    def _choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("tr_tab.choose_subtitle_file"), "",
            t("tr_tab.subtitle_files_filter")
        )
        if not path:
            return

        self.current_file_path = path
        filename = Path(path).name
        self.lbl_file.setText(filename)
        self.lbl_file.setStyleSheet("color: #2196F3; font-weight: bold;")

        ext = Path(path).suffix.lower()
        if ext == '.srt':
            self.loaded_subtitles = self.handler.read_srt(path)
            self.chk_srt.setChecked(True)
        elif ext == '.csv':
            self.loaded_subtitles = self.handler.read_csv(path)
            self.chk_csv.setChecked(True)
        elif ext == '.txt':
            self.loaded_subtitles = self.handler.read_txt(path)
            self.chk_txt.setChecked(True)
        else:
            self._append_log(t("tr_tab.unsupported_format"))
            return

        count = len(self.loaded_subtitles)
        self.lbl_file_info.setText(t("tr_tab.loaded_n_subs", n=count))
        self._append_log(t("tr_tab.opened_file", name=filename, n=count))

        self.preview_list.clear()
        for sub in self.loaded_subtitles[:20]:
            time_part = f"[{sub['start']}]  " if sub.get('start') else f"[{sub['index']}]  "
            self.preview_list.addItem(time_part + sub['text'][:80])
        if count > 20:
            self.preview_list.addItem(t("tr_tab.and_n_more", n=count - 20))

        self.btn_translate.setEnabled(True)

    def _start_translation(self):
        if self._is_translating:
            return
        if not self.loaded_subtitles:
            QMessageBox.warning(self, t("tr_tab.warning"), t("tr_tab.choose_file_first"))
            return
        if not any([self.chk_srt.isChecked(), self.chk_csv.isChecked(), self.chk_txt.isChecked()]):
            QMessageBox.warning(self, t("tr_tab.warning"), t("tr_tab.choose_format"))
            return

        dest_lang = self.lang_combo.currentData()
        engine = self.engine_combo.currentData()

        self._is_translating = True
        self.btn_translate.setEnabled(False)
        self.btn_translate.setText(t("tr_tab.translating"))
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        thread = threading.Thread(
            target=self._translate_worker,
            args=(self.loaded_subtitles.copy(), dest_lang, engine),
            daemon=True
        )
        thread.start()

    def _translate_worker(self, subtitles, dest_lang, engine):
        try:
            self.signals.log.emit(f"🔄 {engine.upper()} → {dest_lang}...")

            try:
                from translation.translator import Translator
                translator = Translator(engine=engine)
            except Exception as e:
                self.signals.log.emit(f"❌ {e}")
                self.signals.finished.emit(False, "")
                return

            if not translator.is_available():
                self.signals.log.emit(f"❌ {engine} unavailable")
                self.signals.finished.emit(False, "")
                return

            total = len(subtitles)

            def progress_cb(msg, pct):
                if pct >= 0:
                    self.signals.progress.emit(int(pct), msg)

            translator_input = [
                {'text': sub['text'], 'start_time': sub.get('start', 0), 'end_time': sub.get('end', 0)}
                for sub in subtitles
            ]

            translated = translator.translate_subtitles(
                translator_input, 'auto', dest_lang, progress_cb
            )

            for i, sub in enumerate(subtitles):
                sub['translated_text'] = translated[i].get('translated_text', sub['text'])

            src_dir = str(Path(self.current_file_path).parent)
            src_stem = Path(self.current_file_path).stem

            save_dir = QFileDialog.getExistingDirectory(None, t("tr_tab.choose_save_dir"), src_dir)
            if not save_dir:
                save_dir = src_dir

            saved_files = []
            base_name = f"{src_stem}_{dest_lang}"

            if self.chk_srt.isChecked():
                out = os.path.join(save_dir, base_name + ".srt")
                self.handler.write_srt(subtitles, out)
                saved_files.append(out)
            if self.chk_csv.isChecked():
                out = os.path.join(save_dir, base_name + ".csv")
                self.handler.write_csv(subtitles, out)
                saved_files.append(out)
            if self.chk_txt.isChecked():
                out = os.path.join(save_dir, base_name + ".txt")
                self.handler.write_txt(subtitles, out)
                saved_files.append(out)

            summary = "\n".join([f"✅ {f}" for f in saved_files])
            self.signals.log.emit(f"💾 {summary}")
            self.signals.finished.emit(True, save_dir)

        except Exception as e:
            logger.error(f"Translation error: {e}")
            self.signals.log.emit(f"❌ {e}")
            self.signals.finished.emit(False, "")

    def _on_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"{msg}  ({pct}%)")

    def _on_finished(self, success, save_dir):
        self._is_translating = False
        self.btn_translate.setEnabled(True)
        self.btn_translate.setText(t("tr_tab.start_translation"))
        self.progress_bar.setValue(100 if success else 0)

        if success:
            self.progress_bar.setFormat(t("tr_tab.completed"))
            QMessageBox.information(
                self, t("tr_tab.translation_done"),
                t("tr_tab.translation_done_msg", path=save_dir)
            )
        else:
            self.progress_bar.setFormat(t("tr_tab.translation_failed"))
            QMessageBox.critical(self, t("tr_tab.translation_failed"),
                                 t("tr_tab.translation_failed_msg"))

    def _append_log(self, msg):
        self.log_box.append(msg)
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum()
        )

    def apply_theme(self, theme):
        if theme == 'dark':
            self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
            self.log_box.setStyleSheet("background: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 10px;")
        else:
            self.setStyleSheet("")
            self.log_box.setStyleSheet("font-size: 10px; font-family: Consolas;")
