# tests/test_regression.py
import unittest
from engines.whisper_engine import WhisperEngine


class TestRegression(unittest.TestCase):
    """اختبارات للتأكد من عدم كسر الميزات الموجودة"""

    def test_backward_compatibility(self):
        """اختبار التوافق العكسي"""
        # اختبار أن الإعدادات القديمة لا تزال تعمل
        old_config = {
            'whisper_model': 'base',
            'speech_engine': 'whisper'
        }

        engine = WhisperEngine(old_config['whisper_model'])
        self.assertEqual(engine.model_name, 'base')

    def test_api_stability(self):
        """اختبار استقرار واجهة البرمجة"""
        # التأكد من أن الدوال الأساسية لا تزال موجودة
        engine = WhisperEngine()

        # الدوال المطلوبة
        required_methods = ['load_model', 'transcribe', 'detect_language']

        for method in required_methods:
            self.assertTrue(hasattr(engine, method))
            self.assertTrue(callable(getattr(engine, method)))