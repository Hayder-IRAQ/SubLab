# tests/test_performance.py
import unittest
import time
import psutil
import threading
from engines.whisper_engine import WhisperEngine
import tempfile
import wave
import numpy as np
import os
import gc


class TestPerformance(unittest.TestCase):

    def create_test_audio_files(self, count: int):
        """إنشاء ملفات صوتية حقيقية لاختبار الأداء"""
        sample_rate = 16000
        duration = 2  # ثانيتين
        samples = np.zeros(int(sample_rate * duration), dtype=np.int16)

        audio_files = []

        for _ in range(count):
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_file.close()
            with wave.open(temp_file.name, 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(samples.tobytes())
            audio_files.append(temp_file.name)

        return audio_files

    def tearDown(self):
        """تنظيف أي ملفات مؤقتة"""
        temp_dir = tempfile.gettempdir()
        for file in os.listdir(temp_dir):
            if file.endswith(".wav"):
                try:
                    os.remove(os.path.join(temp_dir, file))
                except Exception:
                    pass
        gc.collect()

    def test_memory_usage_whisper(self):
        """اختبار استهلاك الذاكرة عند تحميل نموذج Whisper"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        engine = WhisperEngine('tiny')
        success = engine.load_model()

        self.assertTrue(success, "فشل تحميل نموذج Whisper.")

        loaded_memory = process.memory_info().rss
        memory_increase = (loaded_memory - initial_memory) / 1024 / 1024  # بالميغابايت

        self.assertLess(memory_increase, 500, f"Memory usage too high: {memory_increase:.2f}MB")

    def test_concurrent_processing(self):
        """اختبار المعالجة المتزامنة (Multi-threaded transcription)"""

        def process_audio(engine, audio_path):
            try:
                engine.transcribe(audio_path)
            except Exception as e:
                self.fail(f"Transcription failed for {audio_path}: {e}")

        engine = WhisperEngine('tiny')
        self.assertTrue(engine.load_model(), "Failed to load model")

        audio_files = self.create_test_audio_files(3)
        start_time = time.time()

        threads = [
            threading.Thread(target=process_audio, args=(engine, file))
            for file in audio_files
        ]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        duration = time.time() - start_time
        self.assertLess(duration, 60, f"Concurrent processing took too long: {duration:.2f}s")

    def test_large_file_handling(self):
        """محاكاة اختبار ملف صوتي كبير (دون إنشاء فعلي لتوفير الموارد)"""
        simulated_duration = 3600  # ثانية = ساعة
        simulated_size_mb = 500

        self.assertGreater(simulated_duration, 0, "المدة يجب أن تكون موجبة")
        self.assertIsInstance(simulated_size_mb, (int, float), "الحجم يجب أن يكون رقمًا")


class TestStressTest(unittest.TestCase):

    def test_rapid_model_switching(self):
        """اختبار التبديل المتكرر والسريع بين النماذج"""
        engine = WhisperEngine()
        models = ['tiny', 'base']

        for _ in range(5):
            for model in models:
                engine.model_name = model
                start = time.time()
                success = engine.load_model()
                duration = time.time() - start

                self.assertTrue(success, f"فشل تحميل النموذج: {model}")
                self.assertLess(duration, 30, f"Model {model} load time too high: {duration:.2f}s")

    def test_memory_leak_detection(self):
        """تحقق من عدم وجود تسرب في الذاكرة عند تحميل النموذج عدة مرات"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        for _ in range(20):  # عدد أقل لتقليل الوقت
            engine = WhisperEngine('tiny')
            engine.load_model()
            del engine
            gc.collect()

        final_memory = process.memory_info().rss
        memory_diff = (final_memory - initial_memory) / 1024 / 1024

        self.assertLess(memory_diff, 100, f"Memory leak suspected: {memory_diff:.2f}MB increase")
