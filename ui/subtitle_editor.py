# ui/subtitle_editor.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
from typing import List, Dict


class SubtitleEditor(QWidget):
    """محرر ترجمات تفاعلي"""

    subtitles_changed = pyqtSignal(list)  # إشارة تغيير الترجمات

    def __init__(self, parent=None):
        super().__init__(parent)
        self.subtitles = []
        self.current_index = -1
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # شريط الأدوات
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)

        # منطقة التحرير الرئيسية
        main_area = QHBoxLayout()

        # قائمة الترجمات
        self.subtitle_list = QListWidget()
        self.subtitle_list.itemClicked.connect(self.on_subtitle_selected)
        main_area.addWidget(self.subtitle_list, 1)

        # منطقة التحرير التفصيلي
        edit_area = self.create_edit_area()
        main_area.addWidget(edit_area, 2)

        layout.addLayout(main_area)

        # شريط الحالة
        self.status_bar = QLabel("Ready")
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    def create_toolbar(self) -> QToolBar:
        """إنشاء شريط الأدوات"""
        toolbar = QToolBar()

        # أزرار التحرير
        add_action = QAction("➕ Add", self)
        add_action.triggered.connect(self.add_subtitle)
        toolbar.addAction(add_action)

        delete_action = QAction("🗑️ Delete", self)
        delete_action.triggered.connect(self.delete_subtitle)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        # أزرار التشغيل
        play_action = QAction("▶️ Play", self)
        play_action.triggered.connect(self.play_current_segment)
        toolbar.addAction(play_action)

        toolbar.addSeparator()

        # أدوات التحقق
        spellcheck_action = QAction("📝 Spell Check", self)
        spellcheck_action.triggered.connect(self.run_spell_check)
        toolbar.addAction(spellcheck_action)

        return toolbar

    def create_edit_area(self) -> QWidget:
        """إنشاء منطقة التحرير التفصيلي"""
        widget = QWidget()
        layout = QVBoxLayout()

        # تحرير التوقيت
        time_group = QGroupBox("Timing")
        time_layout = QGridLayout()

        time_layout.addWidget(QLabel("Start Time:"), 0, 0)
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("hh:mm:ss.zzz")
        self.start_time_edit.timeChanged.connect(self.on_timing_changed)
        time_layout.addWidget(self.start_time_edit, 0, 1)

        time_layout.addWidget(QLabel("End Time:"), 1, 0)
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("hh:mm:ss.zzz")
        self.end_time_edit.timeChanged.connect(self.on_timing_changed)
        time_layout.addWidget(self.end_time_edit, 1, 1)

        # عرض المدة
        time_layout.addWidget(QLabel("Duration:"), 2, 0)
        self.duration_label = QLabel("0.00s")
        time_layout.addWidget(self.duration_label, 2, 1)

        time_group.setLayout(time_layout)
        layout.addWidget(time_group)

        # تحرير النص
        text_group = QGroupBox("Text")
        text_layout = QVBoxLayout()

        # النص الأصلي
        text_layout.addWidget(QLabel("Original:"))
        self.original_text = QTextEdit()
        self.original_text.setMaximumHeight(80)
        self.original_text.textChanged.connect(self.on_text_changed)
        text_layout.addWidget(self.original_text)

        # النص المترجم
        text_layout.addWidget(QLabel("Translation:"))
        self.translated_text = QTextEdit()
        self.translated_text.setMaximumHeight(80)
        self.translated_text.textChanged.connect(self.on_text_changed)
        text_layout.addWidget(self.translated_text)

        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        # معلومات إضافية
        info_group = QGroupBox("Information")
        info_layout = QGridLayout()

        info_layout.addWidget(QLabel("Language:"), 0, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["en", "ar", "es", "fr", "de"])
        info_layout.addWidget(self.language_combo, 0, 1)

        info_layout.addWidget(QLabel("Confidence:"), 1, 0)
        self.confidence_label = QLabel("N/A")
        info_layout.addWidget(self.confidence_label, 1, 1)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        widget.setLayout(layout)
        return widget

    def load_subtitles(self, subtitles: List[Dict]):
        """تحميل الترجمات في المحرر"""
        self.subtitles = subtitles.copy()
        self.refresh_subtitle_list()

        if self.subtitles:
            self.select_subtitle(0)

    def refresh_subtitle_list(self):
        """تحديث قائمة الترجمات"""
        self.subtitle_list.clear()

        for i, subtitle in enumerate(self.subtitles):
            start_time = self.format_time(subtitle['start_time'])
            end_time = self.format_time(subtitle['end_time'])
            text = subtitle['text'][:50] + "..." if len(subtitle['text']) > 50 else subtitle['text']

            item_text = f"{i + 1}. [{start_time} → {end_time}] {text}"
            item = QListWidgetItem(item_text)

            # تلوين حسب الحالة
            if 'error' in subtitle:
                item.setBackground(QColor(255, 200, 200))  # أحمر فاتح للأخطاء
            elif 'translated_text' in subtitle:
                item.setBackground(QColor(200, 255, 200))  # أخضر فاتح للمترجم

            self.subtitle_list.addItem(item)

    def select_subtitle(self, index: int):
        """تحديد ترجمة للتحرير"""
        if 0 <= index < len(self.subtitles):
            self.current_index = index
            subtitle = self.subtitles[index]

            # تحديث حقول التحرير
            self.start_time_edit.setTime(self.seconds_to_qtime(subtitle['start_time']))
            self.end_time_edit.setTime(self.seconds_to_qtime(subtitle['end_time']))
            self.original_text.setPlainText(subtitle['text'])

            translated = subtitle.get('translated_text', '')
            self.translated_text.setPlainText(translated)

            # تحديث المعلومات
            language = subtitle.get('original_language', 'en')
            index = self.language_combo.findText(language)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)

            confidence = subtitle.get('confidence', 0)
            self.confidence_label.setText(f"{confidence:.2%}" if confidence else "N/A")

            self.update_duration()
            self.subtitle_list.setCurrentRow(index)

    def on_subtitle_selected(self, item):
        """معالج تحديد ترجمة من القائمة"""
        index = self.subtitle_list.row(item)
        self.select_subtitle(index)

    def on_timing_changed(self):
        """معالج تغيير التوقيت"""
        if self.current_index >= 0:
            start_seconds = self.qtime_to_seconds(self.start_time_edit.time())
            end_seconds = self.qtime_to_seconds(self.end_time_edit.time())

            self.subtitles[self.current_index]['start_time'] = start_seconds
            self.subtitles[self.current_index]['end_time'] = end_seconds

            self.update_duration()
            self.refresh_subtitle_list()
            self.subtitles_changed.emit(self.subtitles)

    def on_text_changed(self):
        """معالج تغيير النص"""
        if self.current_index >= 0:
            original = self.original_text.toPlainText()
            translated = self.translated_text.toPlainText()

            self.subtitles[self.current_index]['text'] = original
            if translated:
                self.subtitles[self.current_index]['translated_text'] = translated

            self.refresh_subtitle_list()
            self.subtitles_changed.emit(self.subtitles)

    def update_duration(self):
        """تحديث عرض المدة"""
        if self.current_index >= 0:
            subtitle = self.subtitles[self.current_index]
            duration = subtitle['end_time'] - subtitle['start_time']
            self.duration_label.setText(f"{duration:.2f}s")

    def add_subtitle(self):
        """إضافة ترجمة جديدة"""
        new_subtitle = {
            'start_time': 0.0,
            'end_time': 2.0,
            'text': 'New subtitle',
            'original_language': 'en'
        }

        self.subtitles.append(new_subtitle)
        self.refresh_subtitle_list()
        self.select_subtitle(len(self.subtitles) - 1)
        self.subtitles_changed.emit(self.subtitles)

    def delete_subtitle(self):
        """حذف الترجمة الحالية"""
        if self.current_index >= 0:
            reply = QMessageBox.question(
                self, "Delete Subtitle",
                "Are you sure you want to delete this subtitle?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                del self.subtitles[self.current_index]
                self.refresh_subtitle_list()

                # تحديد العنصر التالي
                if self.subtitles:
                    new_index = min(self.current_index, len(self.subtitles) - 1)
                    self.select_subtitle(new_index)
                else:
                    self.current_index = -1

                self.subtitles_changed.emit(self.subtitles)

    def run_spell_check(self):
        """تشغيل فحص الإملاء"""
        # يمكن تطوير هذه الميزة لاحقاً
        QMessageBox.information(self, "Spell Check", "Spell check feature coming soon!")

    def play_current_segment(self):
        """تشغيل المقطع الحالي"""
        # يمكن تطوير هذه الميزة لاحقاً
        QMessageBox.information(self, "Play Segment", "Audio playback feature coming soon!")

    @staticmethod
    def format_time(seconds: float) -> str:
        """تنسيق الوقت للعرض"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    @staticmethod
    def seconds_to_qtime(seconds: float) -> QTime:
        """تحويل الثواني إلى QTime"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        msecs = int((seconds % 1) * 1000)
        return QTime(hours, minutes, secs, msecs)

    @staticmethod
    def qtime_to_seconds(qtime: QTime) -> float:
        """تحويل QTime إلى ثواني"""
        return qtime.hour() * 3600 + qtime.minute() * 60 + qtime.second() + qtime.msec() / 1000