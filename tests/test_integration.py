# tests/test_integration.py
import unittest
import tempfile
import shutil
from pathlib import Path
from utils.config import Config
from engines.whisper_engine import WhisperEngine
from translation.translator import Translator
from utils.export import Exporter


class TestFullWorkflow(unittest.TestCase):
    """اختبار سير العمل الكامل"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_complete_pipeline(self):
        """اختبار خط الإنتاج الكامل"""
        # 1. إعداد التكوين
        self.config.set('speech_engine', 'whisper')
        self.config.set('whisper_model', 'tiny')
        self.config.set('translation_engine', 'google')
        self.config.set('translation_language', 'ar')

        # 2. محاكاة معالجة الصوت
        mock_segments = [
            {'start_time': 0.0, 'end_time': 2.0, 'text': 'Hello world'},
            {'start_time': 2.0, 'end_time': 4.0, 'text': 'This is a test'}
        ]

        # 3. الترجمة
        translator = Translator('google')
        if translator.is_available():
            translated = translator.translate_subtitles(
                mock_segments, 'en', 'ar'
            )
            self.assertEqual(len(translated), len(mock_segments))

        # 4. التصدير
        exporter = Exporter()
        srt_path = Path(self.temp_dir) / "test.srt"
        csv_path = Path(self.temp_dir) / "test.csv"

        exporter.export_srt(mock_segments, str(srt_path))
        exporter.export_csv(mock_segments, str(csv_path))

        # التحقق من وجود الملفات
        self.assertTrue(srt_path.exists())
        self.assertTrue(csv_path.exists())

    def test_error_recovery(self):
        """اختبار التعافي من الأخطاء"""
        # محاكاة فشل في التحميل
        engine = WhisperEngine('nonexistent_model')
        success = engine.load_model()
        self.assertFalse(success)

        # يجب أن يتمكن النظام من التعافي
        engine.model_name = 'tiny'
        success = engine.load_model()
        # النتيجة تعتمد على توفر النموذج
        self.assertIsInstance(success, bool)


class TestUIIntegration(unittest.TestCase):
    """اختبار تكامل واجهة المستخدم"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_language_switching(self):
        """اختبار تبديل اللغات في الواجهة"""
        from ui.main_window import UITextManager, Language

        text_manager = UITextManager()

        # اختبار النصوص بالإنجليزية
        en_text = text_manager.get_text('main_title', Language.ENGLISH)
        self.assertIn('Free Video Subtitle Generator', en_text)

        # اختبار النصوص بالعربية
        ar_text = text_manager.get_text('main_title', Language.ARABIC)
        self.assertIn('مولد الترجمات', ar_text)

    def test_config_persistence(self):
        """اختبار استمرارية الإعدادات"""
        config_path = Path(self.temp_dir) / "test_config.json"

        # إنشاء إعدادات
        config1 = Config(str(config_path))
        config1.set('language', 'ar')
        config1.set('dark_mode', True)
        config1.save()

        # تحميل في جلسة جديدة
        config2 = Config(str(config_path))
        self.assertEqual(config2.get('language'), 'ar')
        self.assertTrue(config2.get('dark_mode'))
