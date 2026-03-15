# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# translation/argos_translator.py
"""محرك الترجمة الأوفلاين باستخدام Argos Translate مع مسار مخصص للنماذج"""

import logging
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Callable

try:
    import argostranslate.package
    import argostranslate.translate
    import argostranslate.settings

    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ArgosTranslator:
    """مترجم أوفلاين باستخدام Argos Translate مع تخزين محلي"""

    def __init__(self):
        if not ARGOS_AVAILABLE:
            raise ImportError("argostranslate غير مثبت. استخدم: pip install argostranslate")

        self.installed_languages = []
        self.available_packages = []
        self._setup_local_directory()
        self._initialize()

    def _setup_local_directory(self):
        """إعداد مجلد محلي لحفظ نماذج Argos"""
        # الحصول على مسار المشروع
        current_dir = Path(__file__).parent.parent
        self.models_dir = current_dir / 'models' / 'argos'

        # إنشاء المجلدات المطلوبة
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # إنشاء مجلدات فرعية لـ Argos
        self.packages_dir = self.models_dir / 'packages'
        self.index_dir = self.models_dir / 'index'
        self.downloads_dir = self.models_dir / 'downloads'

        for dir_path in [self.packages_dir, self.index_dir, self.downloads_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # تعيين مسارات Argos للمجلد المحلي
        os.environ['ARGOS_PACKAGES_DIR'] = str(self.packages_dir)

        # تحديث إعدادات Argos لاستخدام المجلد المحلي
        argostranslate.settings.home_dir = str(self.models_dir)
        argostranslate.settings.package_dir = str(self.packages_dir)
        argostranslate.settings.index_dir = str(self.index_dir)
        argostranslate.settings.downloads_dir = str(self.downloads_dir)

        # إنشاء ملف .gitkeep للحفاظ على هيكل المجلدات
        (self.models_dir / '.gitkeep').touch(exist_ok=True)

        logger.info(f"تم إعداد مجلد Argos المحلي: {self.models_dir}")

    def _initialize(self):
        """تهيئة Argos Translate وتحديث الحزم"""
        try:
            # التحقق من وجود ملف الفهرس المحلي
            index_file = self.index_dir / 'index.json'

            # تحديث فهرس الحزم إذا لم يكن موجوداً
            if not index_file.exists() or index_file.stat().st_size == 0:
                logger.info("تحديث فهرس حزم Argos...")
                argostranslate.package.update_package_index()
            else:
                logger.info("استخدام فهرس الحزم المحلي")

            # الحصول على اللغات المثبتة
            self.installed_languages = argostranslate.translate.get_installed_languages()

            # الحصول على الحزم المتاحة
            self.available_packages = argostranslate.package.get_available_packages()

            logger.info(f"تم تهيئة Argos Translate بنجاح. اللغات المثبتة: {len(self.installed_languages)}")
            logger.info(f"مسار النماذج: {self.models_dir}")

        except Exception as e:
            logger.error(f"فشل في تهيئة Argos Translate: {e}")
            raise

    def get_model_directory(self) -> Path:
        """الحصول على مسار مجلد النماذج"""
        return self.models_dir

    def normalize_language_code(self, lang_code: str) -> str:
        """تطبيع رموز اللغات لتتوافق مع Argos"""
        # خريطة تحويل رموز اللغات
        lang_mapping = {
            'ar': 'ar',  # العربية
            'en': 'en',  # الإنجليزية
            'es': 'es',  # الإسبانية
            'fr': 'fr',  # الفرنسية
            'de': 'de',  # الألمانية
            'it': 'it',  # الإيطالية
            'pt': 'pt',  # البرتغالية
            'ru': 'ru',  # الروسية
            'zh-cn': 'zh',  # الصينية المبسطة
            'zh-tw': 'zh',  # الصينية التقليدية
            'zh': 'zh',  # الصينية
            'ja': 'ja',  # اليابانية
            'ko': 'ko',  # الكورية
            'hi': 'hi',  # الهندية
            'tr': 'tr',  # التركية
            'pl': 'pl',  # البولندية
            'nl': 'nl',  # الهولندية
            'sv': 'sv',  # السويدية
            'da': 'da',  # الدنماركية
            'no': 'no',  # النرويجية
            'fi': 'fi',  # الفنلندية
            'cs': 'cs',  # التشيكية
            'hu': 'hu',  # المجرية
            'el': 'el',  # اليونانية
            'he': 'he',  # العبرية
            'th': 'th',  # التايلاندية
            'vi': 'vi',  # الفيتنامية
            'id': 'id',  # الإندونيسية
            'ms': 'ms',  # الماليزية
            'auto': 'en',  # الكشف التلقائي -> افتراضي إنجليزي
        }

        return lang_mapping.get(lang_code.lower(), lang_code.lower())

    def get_installed_languages(self) -> List[Dict]:
        """الحصول على قائمة اللغات المثبتة"""
        languages = []
        try:
            for lang in self.installed_languages:
                languages.append({
                    'code': lang.code,
                    'name': lang.name
                })
        except Exception as e:
            logger.error(f"خطأ في الحصول على اللغات المثبتة: {e}")

        return languages

    def get_available_packages(self) -> List[Dict]:
        """الحصول على قائمة الحزم المتاحة للتنزيل"""
        packages = []
        try:
            for package in self.available_packages:
                packages.append({
                    'from_code': package.from_code,
                    'from_name': package.from_name,
                    'to_code': package.to_code,
                    'to_name': package.to_name,
                    'package': package
                })
        except Exception as e:
            logger.error(f"خطأ في الحصول على الحزم المتاحة: {e}")

        return packages

    def get_installed_packages(self) -> List[Dict]:
        """الحصول على قائمة الحزم المثبتة"""
        packages = []
        try:
            installed_packages = argostranslate.package.get_installed_packages()
            for package in installed_packages:
                packages.append({
                    'from_lang': package.from_code,
                    'to_lang': package.to_code,
                    'from_name': package.from_name,
                    'to_name': package.to_name
                })

            # عرض معلومات الحزم المثبتة
            logger.info(f"الحزم المثبتة في {self.packages_dir}: {len(packages)} حزمة")

        except Exception as e:
            logger.error(f"خطأ في الحصول على الحزم المثبتة: {e}")

        return packages

    def is_package_installed(self, from_code: str, to_code: str) -> bool:
        """التحقق من تثبيت حزمة معينة"""
        try:
            # تطبيع رموز اللغات
            from_code = self.normalize_language_code(from_code)
            to_code = self.normalize_language_code(to_code)

            # البحث عن اللغات في القائمة المثبتة
            from_lang = next((l for l in self.installed_languages if l.code == from_code), None)
            to_lang = next((l for l in self.installed_languages if l.code == to_code), None)

            if from_lang and to_lang:
                # التحقق من وجود الترجمة
                translation = from_lang.get_translation(to_lang)
                return translation is not None

            return False

        except Exception as e:
            logger.error(f"خطأ في التحقق من تثبيت الحزمة: {e}")
            return False

    def install_language_package(self, from_code: str, to_code: str,
                                 progress_callback: Optional[Callable] = None) -> bool:
        """تثبيت حزمة لغة إذا لم تكن مثبتة"""
        try:
            # تطبيع رموز اللغات
            from_code = self.normalize_language_code(from_code)
            to_code = self.normalize_language_code(to_code)

            if progress_callback:
                progress_callback("جاري تحديث فهرس الحزم...", 10)

            # تحديث فهرس الحزم
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()

            if progress_callback:
                progress_callback("جاري البحث عن الحزمة المطلوبة...", 30)

            # البحث عن الحزمة المطلوبة
            package = next(
                (p for p in available_packages
                 if p.from_code == from_code and p.to_code == to_code),
                None
            )

            if not package:
                logger.error(f"لم يتم العثور على حزمة الترجمة: {from_code} -> {to_code}")
                if progress_callback:
                    progress_callback("الحزمة غير متوفرة", -1)
                return False

            if progress_callback:
                progress_callback(f"جاري تنزيل حزمة {from_code} -> {to_code}...", 50)

            logger.info(f"تنزيل حزمة اللغة: {from_code} -> {to_code}")
            logger.info(f"سيتم الحفظ في: {self.downloads_dir}")

            # تنزيل الحزمة إلى المجلد المحلي
            download_path = package.download()

            # نقل الملف إلى مجلد التنزيلات المحلي إذا لزم الأمر
            if not str(download_path).startswith(str(self.downloads_dir)):
                local_download_path = self.downloads_dir / Path(download_path).name
                shutil.move(str(download_path), str(local_download_path))
                download_path = local_download_path

            if progress_callback:
                progress_callback("جاري تثبيت الحزمة...", 80)

            # تثبيت الحزمة
            argostranslate.package.install_from_path(download_path)

            # تحديث اللغات المثبتة
            self.installed_languages = argostranslate.translate.get_installed_languages()

            if progress_callback:
                progress_callback("تم تثبيت الحزمة بنجاح", 100)

            logger.info(f"تم تثبيت حزمة الترجمة بنجاح في: {self.packages_dir}")

            # حذف ملف التنزيل بعد التثبيت
            try:
                Path(download_path).unlink()
            except:
                pass

            return True

        except Exception as e:
            logger.error(f"خطأ في تثبيت حزمة اللغة: {e}")
            if progress_callback:
                progress_callback(f"فشل التثبيت: {e}", -1)
            return False

    def translate_text(self, text: str, from_code: str, to_code: str) -> str:
        """ترجمة نص واحد"""
        try:
            # تطبيع رموز اللغات
            from_code = self.normalize_language_code(from_code)
            to_code = self.normalize_language_code(to_code)

            # التحقق من صحة النص
            if not text or not text.strip():
                return text

            # إذا كانت اللغة المصدر والهدف متشابهة
            if from_code == to_code:
                return text

            # البحث عن اللغات المثبتة
            from_lang = next((l for l in self.installed_languages if l.code == from_code), None)
            to_lang = next((l for l in self.installed_languages if l.code == to_code), None)

            if not from_lang:
                logger.warning(f"اللغة المصدر غير مثبتة: {from_code}")
                return text

            if not to_lang:
                logger.warning(f"اللغة الهدف غير مثبتة: {to_code}")
                return text

            # الحصول على كائن الترجمة
            translation = from_lang.get_translation(to_lang)

            if not translation:
                logger.warning(f"حزمة الترجمة غير متوفرة: {from_code} -> {to_code}")
                return text

            # تنفيذ الترجمة
            result = translation.translate(text)

            # التحقق من نتيجة الترجمة
            if result and result.strip():
                logger.debug(f"ترجمة ناجحة: '{text[:50]}...' -> '{result[:50]}...'")
                return result
            else:
                logger.warning(f"فشل في ترجمة النص: {text[:50]}...")
                return text

        except Exception as e:
            logger.error(f"خطأ في الترجمة: {e}")
            return text

    def translate_subtitles(self, subtitles: List[Dict], from_code: str, to_code: str,
                            progress_callback: Optional[Callable] = None) -> List[Dict]:
        """ترجمة قائمة من الترجمات النصية"""
        try:
            # تطبيع رموز اللغات
            from_code = self.normalize_language_code(from_code)
            to_code = self.normalize_language_code(to_code)

            # التحقق من صحة البيانات
            if not subtitles:
                logger.warning("لا توجد ترجمات للترجمة")
                return subtitles

            if from_code == to_code:
                logger.info("اللغة المصدر والهدف متشابهة، لا حاجة للترجمة")
                return subtitles

            # التحقق من تثبيت الحزمة
            if not self.is_package_installed(from_code, to_code):
                logger.error(f"حزمة الترجمة غير مثبتة: {from_code} -> {to_code}")
                return subtitles

            # البحث عن اللغات
            from_lang = next((l for l in self.installed_languages if l.code == from_code), None)
            to_lang = next((l for l in self.installed_languages if l.code == to_code), None)

            if not from_lang or not to_lang:
                logger.error(f"اللغات غير متوفرة: {from_code} -> {to_code}")
                return subtitles

            # الحصول على كائن الترجمة
            translation = from_lang.get_translation(to_lang)
            if not translation:
                logger.error(f"كائن الترجمة غير متوفر: {from_code} -> {to_code}")
                return subtitles

            logger.info(f"بدء ترجمة {len(subtitles)} عنصر من {from_code} إلى {to_code}")

            # ترجمة كل عنصر
            total = len(subtitles)
            translated_count = 0
            failed_count = 0

            for i, sub in enumerate(subtitles):
                try:
                    # الحصول على النص للترجمة
                    original_text = sub.get('text', '')

                    if not original_text or not original_text.strip():
                        sub['translated_text'] = original_text
                        sub['translation_language'] = to_code
                        continue

                    # تنفيذ الترجمة
                    translated_text = translation.translate(original_text)

                    if translated_text and translated_text.strip():
                        sub['translated_text'] = translated_text
                        sub['translation_language'] = to_code
                        translated_count += 1
                    else:
                        # الاحتفاظ بالنص الأصلي في حالة فشل الترجمة
                        sub['translated_text'] = original_text
                        sub['translation_language'] = from_code
                        failed_count += 1
                        logger.warning(f"فشل في ترجمة العنصر {i}: {original_text[:50]}...")

                    # تحديث التقدم
                    if progress_callback and (i % 5 == 0 or i == total - 1):
                        progress = ((i + 1) / total) * 100
                        progress_callback(
                            f"جاري الترجمة... {i + 1}/{total} (نجح: {translated_count}, فشل: {failed_count})",
                            progress
                        )

                except Exception as e:
                    logger.error(f"خطأ في ترجمة العنصر {i}: {e}")
                    # الاحتفاظ بالنص الأصلي
                    sub['translated_text'] = sub.get('text', '')
                    sub['translation_language'] = from_code
                    failed_count += 1

            if progress_callback:
                progress_callback(f"اكتملت الترجمة: {translated_count} نجح، {failed_count} فشل", 100)

            logger.info(f"انتهت الترجمة: {translated_count} نجح، {failed_count} فشل")
            return subtitles

        except Exception as e:
            logger.error(f"خطأ في ترجمة الترجمات النصية: {e}")
            if progress_callback:
                progress_callback(f"فشلت الترجمة: {e}", -1)
            return subtitles

    def get_supported_languages(self) -> Dict[str, str]:
        """الحصول على اللغات المدعومة"""
        try:
            languages = {}
            for lang in self.installed_languages:
                languages[lang.code] = lang.name

            # إضافة اللغات الأساسية إذا لم تكن موجودة
            basic_languages = {
                'en': 'English',
                'ar': 'العربية',
                'es': 'Español',
                'fr': 'Français',
                'de': 'Deutsch',
                'it': 'Italiano',
                'pt': 'Português',
                'ru': 'Русский',
                'zh': '中文',
                'ja': '日本語',
                'ko': '한국어',
                'hi': 'हिन्दी',
                'tr': 'Türkçe',
                'pl': 'Polski'
            }

            for code, name in basic_languages.items():
                if code not in languages:
                    languages[code] = name

            return languages

        except Exception as e:
            logger.error(f"خطأ في الحصول على اللغات المدعومة: {e}")
            return {
                'en': 'English',
                'ar': 'العربية',
                'es': 'Español',
                'fr': 'Français'
            }

    def check_installation(self) -> Dict[str, any]:
        """فحص حالة التثبيت"""
        try:
            status = {
                'argos_installed': True,
                'languages_count': len(self.installed_languages),
                'packages_count': len(argostranslate.package.get_installed_packages()),
                'available_packages': len(self.available_packages),
                'languages': [{'code': l.code, 'name': l.name} for l in self.installed_languages],
                'model_path': str(self.models_dir),
                'packages_path': str(self.packages_dir)
            }

            logger.info(f"حالة Argos: {status['languages_count']} لغة، {status['packages_count']} حزمة مثبتة")
            logger.info(f"مسار النماذج: {status['model_path']}")

            return status

        except Exception as e:
            logger.error(f"خطأ في فحص التثبيت: {e}")
            return {
                'argos_installed': False,
                'error': str(e),
                'languages_count': 0,
                'packages_count': 0
            }

    def clean_old_packages(self):
        """تنظيف الحزم القديمة أو غير المستخدمة"""
        try:
            # حذف ملفات التنزيل المؤقتة
            for file_path in self.downloads_dir.glob('*.argosmodel'):
                try:
                    file_path.unlink()
                    logger.info(f"تم حذف ملف التنزيل المؤقت: {file_path}")
                except Exception as e:
                    logger.warning(f"فشل حذف الملف {file_path}: {e}")

        except Exception as e:
            logger.error(f"خطأ في تنظيف الحزم القديمة: {e}")

    @staticmethod
    def is_available() -> bool:
        """التحقق من توفر Argos Translate"""
        return ARGOS_AVAILABLE