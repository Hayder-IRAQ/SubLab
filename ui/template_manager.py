# ui/template_manager.py
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *


@dataclass
class SubtitleStyle:
    """نمط الترجمة"""
    font_family: str = "Arial"
    font_size: int = 16
    font_weight: str = "normal"  # normal, bold
    font_style: str = "normal"  # normal, italic
    color: str = "#FFFFFF"
    background_color: str = "#000000"
    outline_color: str = "#000000"
    outline_width: int = 1
    alignment: str = "center"  # left, center, right
    position: str = "bottom"  # top, center, bottom
    margin: int = 20


@dataclass
class ExportTemplate:
    """قالب التصدير"""
    name: str
    description: str
    format: str  # srt, ass, vtt, etc.
    style: SubtitleStyle
    settings: Dict


class TemplateManager:
    """مدير القوالب والأنماط"""

    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        self.templates = {}
        self.load_templates()

    def create_default_templates(self):
        """إنشاء القوالب الافتراضية"""
        templates = {
            "standard": ExportTemplate(
                name="Standard",
                description="Standard subtitle format",
                format="srt",
                style=SubtitleStyle(),
                settings={"encoding": "utf-8"}
            ),
            "arabic": ExportTemplate(
                name="Arabic Style",
                description="Optimized for Arabic subtitles",
                format="srt",
                style=SubtitleStyle(
                    font_family="Traditional Arabic",
                    font_size=18,
                    alignment="center"
                ),
                settings={"encoding": "utf-8", "rtl": True}
            ),
            "netflix": ExportTemplate(
                name="Netflix Style",
                description="Netflix-like subtitle style",
                format="ass",
                style=SubtitleStyle(
                    font_family="Netflix Sans",
                    font_size=16,
                    font_weight="bold",
                    color="#FFFFFF",
                    outline_color="#000000",
                    outline_width=2
                ),
                settings={"timing_precision": 3}
            ),
            "youtube": ExportTemplate(
                name="YouTube Style",
                description="YouTube closed captions style",
                format="vtt",
                style=SubtitleStyle(
                    font_family="Roboto",
                    font_size=14,
                    background_color="rgba(0,0,0,0.8)"
                ),
                settings={"cue_settings": True}
            )
        }

        for template_id, template in templates.items():
            self.save_template(template_id, template)

    def load_templates(self):
        """تحميل القوالب من الملفات"""
        if not any(self.templates_dir.glob("*.json")):
            self.create_default_templates()

        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                template = ExportTemplate(
                    name=data['name'],
                    description=data['description'],
                    format=data['format'],
                    style=SubtitleStyle(**data['style']),
                    settings=data['settings']
                )

                self.templates[template_file.stem] = template

            except Exception as e:
                print(f"Error loading template {template_file}: {e}")

    def save_template(self, template_id: str, template: ExportTemplate):
        """حفظ قالب"""
        template_file = self.templates_dir / f"{template_id}.json"

        data = {
            'name': template.name,
            'description': template.description,
            'format': template.format,
            'style': asdict(template.style),
            'settings': template.settings
        }

        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.templates[template_id] = template

    def get_template(self, template_id: str) -> ExportTemplate:
        """الحصول على قالب"""
        return self.templates.get(template_id)

    def get_template_list(self) -> List[Dict]:
        """الحصول على قائمة القوالب"""
        return [
            {
                'id': template_id,
                'name': template.name,
                'description': template.description,
                'format': template.format
            }
            for template_id, template in self.templates.items()
        ]


class StyleEditor(QDialog):
    """محرر الأنماط"""

    def __init__(self, style: SubtitleStyle = None, parent=None):
        super().__init__(parent)
        self.style = style or SubtitleStyle()
        self.setup_ui()
        self.load_style()

    def setup_ui(self):
        self.setWindowTitle("Style Editor")
        self.setModal(True)
        layout = QVBoxLayout()

        # تبويبات للإعدادات المختلفة
        tabs = QTabWidget()

        # تبويب الخط
        font_tab = self.create_font_tab()
        tabs.addTab(font_tab, "Font")

        # تبويب الألوان
        color_tab = self.create_color_tab()
        tabs.addTab(color_tab, "Colors")

        # تبويب الموضع
        position_tab = self.create_position_tab()
        tabs.addTab(position_tab, "Position")

        layout.addWidget(tabs)

        # أزرار التحكم
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def create_font_tab(self) -> QWidget:
        """إنشاء تبويب إعدادات الخط"""
        widget = QWidget()
        layout = QFormLayout()

        # عائلة الخط
        self.font_family = QFontComboBox()
        layout.addRow("Font Family:", self.font_family)

        # حجم الخط
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        layout.addRow("Font Size:", self.font_size)

        # وزن الخط
        self.font_weight = QComboBox()
        self.font_weight.addItems(["normal", "bold"])
        layout.addRow("Font Weight:", self.font_weight)

        # نمط الخط
        self.font_style = QComboBox()
        self.font_style.addItems(["normal", "italic"])
        layout.addRow("Font Style:", self.font_style)

        widget.setLayout(layout)
        return widget

    def create_color_tab(self) -> QWidget:
        """إنشاء تبويب إعدادات الألوان"""
        widget = QWidget()
        layout = QFormLayout()

        # لون النص
        self.text_color_btn = QPushButton()
        self.text_color_btn.clicked.connect(lambda: self.choose_color('text'))
        layout.addRow("Text Color:", self.text_color_btn)

        # لون الخلفية
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.clicked.connect(lambda: self.choose_color('background'))
        layout.addRow("Background Color:", self.bg_color_btn)

        # لون الحدود
        self.outline_color_btn = QPushButton()
        self.outline_color_btn.clicked.connect(lambda: self.choose_color('outline'))
        layout.addRow("Outline Color:", self.outline_color_btn)

        # عرض الحدود
        self.outline_width = QSpinBox()
        self.outline_width.setRange(0, 10)
        layout.addRow("Outline Width:", self.outline_width)

        widget.setLayout(layout)
        return widget

    def create_position_tab(self) -> QWidget:
        """إنشاء تبويب إعدادات الموضع"""
        widget = QWidget()
        layout = QFormLayout()

        # محاذاة النص
        self.alignment = QComboBox()
        self.alignment.addItems(["left", "center", "right"])
        layout.addRow("Alignment:", self.alignment)

        # موضع الترجمة
        self.position = QComboBox()
        self.position.addItems(["top", "center", "bottom"])
        layout.addRow("Position:", self.position)

        # الهامش
        self.margin = QSpinBox()
        self.margin.setRange(0, 100)
        layout.addRow("Margin:", self.margin)

        widget.setLayout(layout)
        return widget

    def load_style(self):
        """تحميل إعدادات النمط في الواجهة"""
        # إعدادات الخط
        self.font_family.setCurrentText(self.style.font_family)
        self.font_size.setValue(self.style.font_size)
        self.font_weight.setCurrentText(self.style.font_weight)
        self.font_style.setCurrentText(self.style.font_style)

        # إعدادات الألوان
        self.update_color_button(self.text_color_btn, self.style.color)
        self.update_color_button(self.bg_color_btn, self.style.background_color)
        self.update_color_button(self.outline_color_btn, self.style.outline_color)
        self.outline_width.setValue(self.style.outline_width)

        # إعدادات الموضع
        self.alignment.setCurrentText(self.style.alignment)
        self.position.setCurrentText(self.style.position)
        self.margin.setValue(self.style.margin)

    def save_style(self):
        """حفظ إعدادات النمط"""
        self.style.font_family = self.font_family.currentText()
        self.style.font_size = self.font_size.value()
        self.style.font_weight = self.font_weight.currentText()
        self.style.font_style = self.font_style.currentText()

        self.style.alignment = self.alignment.currentText()
        self.style.position = self.position.currentText()
        self.style.margin = self.margin.value()
        self.style.outline_width = self.outline_width.value()

    def choose_color(self, color_type: str):
        """اختيار لون"""
        current_color = getattr(self.style, f"{color_type}_color")
        color = QColorDialog.getColor(QColor(current_color), self)

        if color.isValid():
            setattr(self.style, f"{color_type}_color", color.name())
            button = getattr(self, f"{color_type}_color_btn")
            self.update_color_button(button, color.name())

    def update_color_button(self, button: QPushButton, color: str):
        """تحديث لون الزر"""
        button.setStyleSheet(f"background-color: {color}; color: white;")
        button.setText(color)

    def accept(self):
        """قبول التغييرات"""
        self.save_style()
        super().accept()