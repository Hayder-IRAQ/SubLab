# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# translation/translator.py
"""المدير الموحد لمحركات الترجمة المختلفة"""

import logging
from typing import List, Dict, Optional, Callable

# استيراد محركات الترجمة
try:
    from .google_translator import GoogleTranslateEngine
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from .argos_translator import ArgosTranslator
    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False

logger = logging.getLogger(__name__)


class Translator:
    """الفئة الرئيسية للترجمة التي تدعم محركات متعددة"""

    ENGINES = {
        'google': {
            'name': 'Google Translate',
            'requires_internet': True,
            'available': GOOGLE_AVAILABLE
        },
        'argos': {
            'name': 'Argos Translate',
            'requires_internet': False,
            'available': ARGOS_AVAILABLE
        }
    }

    def __init__(self, engine: str = 'google'):
        """تهيئة المترجم باستخدام المحرك المحدد"""
        self.engine_name = engine.lower()
        self.engine = None

        try:
            if self.engine_name == 'google' and GOOGLE_AVAILABLE:
                self.engine = GoogleTranslateEngine()
                logger.info("تم تحميل محرك Google Translate")
            elif self.engine_name == 'argos' and ARGOS_AVAILABLE:
                self.engine = ArgosTranslator()
                logger.info("تم تحميل محرك Argos Translate")
            else:
                logger.warning(f"محرك الترجمة {engine} غير متوفر")

        except Exception as e:
            logger.error(f"خطأ في تحميل محرك الترجمة {engine}: {e}")
            self.engine = None

    def translate_subtitles(self, subtitles: List[Dict], src_lang: str,
                            dest_lang: str, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        ترجمة قائمة الترجمات النصية

        Args:
            subtitles: قائمة قواميس الترجمات النصية
            src_lang: رمز اللغة المصدر
            dest_lang: رمز اللغة الهدف
            progress_callback: دالة تحديث التقدم (message: str, progress: float)

        Returns:
            قائمة الترجمات النصية مع حقل 'translated_text' مضاف
        """
        if not self.engine:
            logger.error("لا يوجد محرك ترجمة متوفر")
            return subtitles

        if src_lang == dest_lang or dest_lang == 'none':
            logger.info("اللغة المصدر والهدف متشابهة أو لا توجد ترجمة مطلوبة")
            # إضافة النص الأصلي كترجمة
            for sub in subtitles:
                sub['translated_text'] = sub['text']
                sub['translation_language'] = src_lang
            return subtitles

        try:
            # استخدام الدالة المخصصة لكل محرك
            if hasattr(self.engine, 'translate_subtitles'):
                return self.engine.translate_subtitles(subtitles, src_lang, dest_lang, progress_callback)
            else:
                # Fallback للمحركات التي لا تدعم translate_subtitles
                return self._translate_subtitles_fallback(subtitles, src_lang, dest_lang, progress_callback)

        except Exception as e:
            logger.error(f"خطأ في الترجمة: {e}")
            if progress_callback:
                progress_callback(f"Translation failed: {e}", -1)
            return subtitles

    def _translate_subtitles_fallback(self, subtitles: List[Dict], src_lang: str,
                                      dest_lang: str, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """ترجمة احتياطية للمحركات التي لا تدعم translate_subtitles"""
        total = len(subtitles)
        translated_count = 0
        failed_count = 0

        for i, subtitle in enumerate(subtitles):
            try:
                original_text = subtitle.get('text', '')

                if not original_text.strip():
                    subtitle['translated_text'] = original_text
                    subtitle['translation_language'] = dest_lang
                    continue

                if hasattr(self.engine, 'translate_text'):
                    translated = self.engine.translate_text(original_text, src_lang, dest_lang)
                else:
                    translated = original_text  # Fallback

                if translated and translated.strip():
                    subtitle['translated_text'] = translated
                    subtitle['translation_language'] = dest_lang
                    translated_count += 1
                else:
                    subtitle['translated_text'] = original_text
                    subtitle['translation_language'] = src_lang
                    failed_count += 1

                # تحديث التقدم
                if progress_callback and (i % 5 == 0 or i == total - 1):
                    progress = ((i + 1) / total) * 100
                    progress_callback(
                        f"Translating... {i + 1}/{total} (success: {translated_count}, failed: {failed_count})",
                        progress
                    )

            except Exception as e:
                logger.error(f"خطأ في ترجمة الترجمة النصية {i}: {e}")
                subtitle['translated_text'] = subtitle.get('text', '')
                subtitle['translation_language'] = src_lang
                failed_count += 1

        if progress_callback:
            progress_callback(f"Translation completed: {translated_count} success, {failed_count} failed", 100)

        return subtitles

    def get_supported_languages(self) -> Dict[str, str]:
        """الحصول على اللغات المدعومة للمحرك الحالي"""
        if self.engine and hasattr(self.engine, 'get_supported_languages'):
            return self.engine.get_supported_languages()
        return {'none': 'بدون ترجمة', 'en': 'English'}

    def get_available_engines(self) -> List[Dict]:
        """الحصول على قائمة محركات الترجمة المتوفرة"""
        engines = []
        for key, info in self.ENGINES.items():
            engines.append({
                'id': key,
                'name': info['name'],
                'requires_internet': info['requires_internet'],
                'available': info['available'],
                'active': key == self.engine_name
            })
        return engines

    def is_available(self) -> bool:
        """التحقق من توفر المحرك"""
        return self.engine is not None

    def get_engine_info(self) -> Dict:
        """الحصول على معلومات المحرك الحالي"""
        if not self.engine:
            return {'name': 'غير متوفر', 'available': False}

        # محاولة الحصول على معلومات من المحرك نفسه
        if hasattr(self.engine, 'get_engine_info'):
            return self.engine.get_engine_info()

        # معلومات أساسية
        info = {
            'name': self.ENGINES[self.engine_name]['name'],
            'requires_internet': self.ENGINES[self.engine_name]['requires_internet'],
            'available': True,
            'engine_type': self.engine_name
        }

        # معلومات إضافية للـ Argos
        if (self.engine_name == 'argos' and
                hasattr(self.engine, 'check_installation')):
            try:
                status = self.engine.check_installation()
                info.update({
                    'languages_count': status.get('languages_count', 0),
                    'packages_count': status.get('packages_count', 0),
                    'installation_status': status
                })
            except Exception as e:
                logger.warning(f"Could not get Argos installation status: {e}")

        return info

    # دوال خاصة بـ Argos Translate
    def download_package(self, from_lang: str, to_lang: str, progress_callback: Optional[Callable] = None) -> bool:
        """تنزيل حزمة ترجمة (خاص بـ Argos)"""
        if (self.engine_name == 'argos' and
                hasattr(self.engine, 'install_language_package')):
            return self.engine.install_language_package(from_lang, to_lang, progress_callback)
        return False

    def get_installed_packages(self) -> List[Dict]:
        """الحصول على الحزم المثبتة (خاص بـ Argos)"""
        if (self.engine_name == 'argos' and
                hasattr(self.engine, 'get_installed_packages')):
            return self.engine.get_installed_packages()
        return []

    def is_package_installed(self, from_lang: str, to_lang: str) -> bool:
        """التحقق من تثبيت حزمة (خاص بـ Argos)"""
        if (self.engine_name == 'argos' and
                hasattr(self.engine, 'is_package_installed')):
            return self.engine.is_package_installed(from_lang, to_lang)
        return True  # افتراضي للمحركات الأخرى

    def requires_package_download(self, from_lang: str, to_lang: str) -> bool:
        """التحقق من الحاجة لتنزيل حزمة"""
        if self.engine_name == 'argos':
            return not self.is_package_installed(from_lang, to_lang)
        return False

    def get_translation_capabilities(self) -> Dict:
        """الحصول على قدرات الترجمة للمحرك"""
        capabilities = {
            'supports_auto_detect': False,
            'supports_offline': False,
            'requires_packages': False,
            'batch_translation': False
        }

        if self.engine_name == 'google':
            capabilities.update({
                'supports_auto_detect': True,
                'supports_offline': False,
                'requires_packages': False,
                'batch_translation': True
            })
        elif self.engine_name == 'argos':
            capabilities.update({
                'supports_auto_detect': False,
                'supports_offline': True,
                'requires_packages': True,
                'batch_translation': True
            })

        return capabilities

    @staticmethod
    def get_available_engine_names() -> List[str]:
        """الحصول على أسماء المحركات المتوفرة"""
        available = []
        if GOOGLE_AVAILABLE:
            available.append('google')
        if ARGOS_AVAILABLE:
            available.append('argos')
        return available