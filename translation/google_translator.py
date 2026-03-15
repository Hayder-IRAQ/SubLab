# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# translation/google_translator.py
"""محرك الترجمة الأونلاين باستخدام Google Translate فقط"""

import logging
from typing import List, Dict, Optional, Callable

try:
    from googletrans import Translator as GoogleTranslator
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

logger = logging.getLogger(__name__)


class GoogleTranslateEngine:
    """محرك Google Translate"""

    def __init__(self):
        if not GOOGLE_AVAILABLE:
            raise ImportError("googletrans غير مثبت. استخدم: pip install googletrans==4.0.0rc1")
        self.translator = GoogleTranslator()

    def translate_text(self, text: str, src_lang: str, dest_lang: str) -> str:
        """الترجمة باستخدام Google Translate"""
        try:
            # معالجة الكشف التلقائي
            if src_lang == 'auto':
                result = self.translator.translate(text, dest=dest_lang)
            else:
                result = self.translator.translate(text, src=src_lang, dest=dest_lang)

            return result.text if result and result.text else text

        except Exception as e:
            logger.error(f"خطأ في ترجمة Google: {e}")
            return text

    def translate_subtitles(self, subtitles: List[Dict], src_lang: str, dest_lang: str,
                            progress_callback: Optional[Callable] = None) -> List[Dict]:
        """ترجمة قائمة الترجمات النصية باستخدام Google Translate"""
        if not subtitles:
            logger.warning("لا توجد ترجمات للترجمة")
            return subtitles

        if src_lang == dest_lang or dest_lang == 'none':
            logger.info("اللغة المصدر والهدف متشابهة أو لا توجد ترجمة مطلوبة")
            # إضافة النص الأصلي كترجمة
            for sub in subtitles:
                sub['translated_text'] = sub['text']
                sub['translation_language'] = src_lang
            return subtitles

        try:
            total = len(subtitles)
            logger.info(f"ترجمة {total} ترجمة نصية من {src_lang} إلى {dest_lang} باستخدام Google")

            translated_count = 0
            failed_count = 0

            for i, subtitle in enumerate(subtitles):
                try:
                    # ترجمة النص
                    original_text = subtitle.get('text', '')

                    if not original_text.strip():
                        subtitle['translated_text'] = original_text
                        subtitle['translation_language'] = dest_lang
                        continue

                    translated = self.translate_text(original_text, src_lang, dest_lang)

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
                            f"Translating with Google... {i + 1}/{total} (success: {translated_count}, failed: {failed_count})",
                            progress
                        )

                except Exception as e:
                    logger.error(f"خطأ في ترجمة الترجمة النصية {i}: {e}")
                    subtitle['translated_text'] = subtitle.get('text', '')
                    subtitle['translation_language'] = src_lang
                    failed_count += 1

            if progress_callback:
                progress_callback(f"Google translation completed: {translated_count} success, {failed_count} failed", 100)

            logger.info(f"انتهت الترجمة: {translated_count} نجح، {failed_count} فشل")
            return subtitles

        except Exception as e:
            logger.error(f"خطأ في الترجمة: {e}")
            if progress_callback:
                progress_callback(f"Google translation failed: {e}", -1)
            return subtitles

    def get_supported_languages(self) -> Dict[str, str]:
        """الحصول على اللغات المدعومة من Google Translate"""
        return {
            'none': 'بدون ترجمة',
            'en': 'English',
            'ar': 'العربية',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'zh-cn': '中文 (مبسط)',
            'zh-tw': '中文 (تقليدي)',
            'zh': '中文',
            'ja': '日本語',
            'ko': '한국어',
            'hi': 'हिन्दी',
            'tr': 'Türkçe',
            'pl': 'Polski',
            'nl': 'Nederlands',
            'sv': 'Svenska',
            'da': 'Dansk',
            'no': 'Norsk',
            'fi': 'Suomi',
            'cs': 'Čeština',
            'hu': 'Magyar',
            'el': 'Ελληνικά',
            'he': 'עברית',
            'th': 'ไทย',
            'vi': 'Tiếng Việt',
            'id': 'Bahasa Indonesia',
            'ms': 'Bahasa Melayu',
            'uk': 'Українська',
            'bg': 'Български',
            'hr': 'Hrvatski',
            'sk': 'Slovenčina',
            'sl': 'Slovenščina',
            'et': 'Eesti',
            'lv': 'Latviešu',
            'lt': 'Lietuvių',
            'ro': 'Română'
        }

    def get_engine_info(self) -> Dict:
        """الحصول على معلومات محرك Google"""
        return {
            'name': 'Google Translate',
            'engine_type': 'google',
            'requires_internet': True,
            'supports_auto_detect': True,
            'supports_offline': False,
            'requires_packages': False,
            'batch_translation': True,
            'available': GOOGLE_AVAILABLE
        }

    @staticmethod
    def is_available() -> bool:
        """التحقق من توفر Google Translate"""
        return GOOGLE_AVAILABLE