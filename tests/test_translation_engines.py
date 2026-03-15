# tests/test_translation_engines.py

import unittest
import asyncio
import tracemalloc
import gc
from translation.translator import Translator  # ← تأكد أن المسار صحيح

# بدء تتبع استهلاك الذاكرة
tracemalloc.start()

class TestTranslationEngines(unittest.TestCase):
    """اختبارات محركات الترجمة"""

    def setUp(self):
        """تشغيل قبل كل اختبار"""
        print("\n🧪 بدء اختبار جديد...")

    def tearDown(self):
        """تشغيل بعد كل اختبار"""
        asyncio.run(asyncio.sleep(0.1))  # انتظار لغلق الاتصالات
        gc.collect()  # تنظيف الذاكرة

        # طباعة إحصاءات استخدام الذاكرة
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        print("\n🔍 أعلى 3 مواقع استهلاك للذاكرة:")
        for stat in top_stats[:3]:
            print(stat)

    def test_google_translation(self):
        """اختبار الترجمة بمحرك Google"""
        translator = Translator('google')
        result = translator.translate_text("Hello", "en", "ar")
        self.assertIsInstance(result, str)
        self.assertNotEqual(result.strip(), "")
        print("✅ Google Translation:", result)

    def test_argos_translation(self):
        """اختبار الترجمة بمحرك Argos"""
        translator = Translator('argos')
        result = translator.translate_text("Hello", "en", "ar")
        self.assertIsInstance(result, str)
        self.assertNotEqual(result.strip(), "")
        print("✅ Argos Translation:", result)


class TestAsyncTranslation(unittest.TestCase):
    """اختبارات الترجمة غير المتزامنة"""

    def tearDown(self):
        asyncio.run(asyncio.sleep(0.1))
        gc.collect()
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        print("\n🔍 أعلى 3 مواقع استهلاك للذاكرة:")
        for stat in top_stats[:3]:
            print(stat)

    def test_concurrent_translation(self):
        """اختبار الترجمة المتزامنة لعدة نصوص"""
        asyncio.run(self._run_concurrent_translation())

    async def _run_concurrent_translation(self):
        translator = Translator('google')
        texts = ['Hello', 'World', 'Testing', 'Language', 'Model']

        tasks = [self._translate_async(translator, text) for text in texts]
        results = await asyncio.gather(*tasks)

        self.assertEqual(len(results), len(texts))
        for result in results:
            self.assertIsInstance(result, str)
            self.assertNotEqual(result.strip(), "")
            print("🌐 Translated:", result)

    async def _translate_async(self, translator, text):
        """دالة مساعدة لتنفيذ الترجمة داخل المهام غير المتزامنة"""
        return translator.translate_text(text, "en", "ar")
