# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
# utils/i18n.py
"""
SubLab Internationalization — 10 languages
en: English, ar: العربية, ru: Русский, fr: Français, de: Deutsch,
es: Español, pt: Português, zh: 中文, ja: 日本語, ko: 한국어
"""

from typing import Dict, Optional

SUPPORTED_LANGUAGES = [
    ("en", "English"),
    ("ar", "العربية"),
    ("ru", "Русский"),
    ("fr", "Français"),
    ("de", "Deutsch"),
    ("es", "Español"),
    ("pt", "Português"),
    ("zh", "中文"),
    ("ja", "日本語"),
    ("ko", "한국어"),
]

RTL_LANGUAGES = {"ar", "he", "fa", "ur"}

_STRINGS: Dict[str, Dict[str, str]] = {
    "app.title": {"en":"SubLab — Professional Subtitle Studio","ar":"SubLab — استوديو الترجمات الاحترافي","ru":"SubLab — Профессиональная студия субтитров","fr":"SubLab — Studio de sous-titres professionnel","de":"SubLab — Professionelles Untertitel-Studio","es":"SubLab — Estudio profesional de subtítulos","pt":"SubLab — Estúdio profissional de legendas","zh":"SubLab — 专业字幕工作室","ja":"SubLab — プロフェッショナル字幕スタジオ","ko":"SubLab — 전문 자막 스튜디오"},
    "app.subtitle": {"en":"Auto Language Detection • Translation • Multi-File • Video Export","ar":"كشف تلقائي للغة • الترجمة • ملفات متعددة • تصدير فيديو","ru":"Автообнаружение языка • Перевод • Мультифайл • Экспорт видео","fr":"Détection auto • Traduction • Multi-fichier • Export vidéo","de":"Auto-Spracherkennung • Übersetzung • Multi-Datei • Video-Export","es":"Detección automática • Traducción • Multi-archivo • Exportar vídeo","pt":"Detecção automática • Tradução • Multi-arquivo • Exportar vídeo","zh":"自动语言检测 • 翻译 • 多文件 • 视频导出","ja":"自動言語検出 • 翻訳 • マルチファイル • ビデオエクスポート","ko":"자동 언어 감지 • 번역 • 멀티 파일 • 비디오 내보내기"},
    "app.ready": {"en":"Ready","ar":"جاهز","ru":"Готов","fr":"Prêt","de":"Bereit","es":"Listo","pt":"Pronto","zh":"就绪","ja":"準備完了","ko":"준비 완료"},
    "tab.generator": {"en":"🎬 Subtitle Generator","ar":"🎬 توليد الترجمات","ru":"🎬 Генератор субтитров","fr":"🎬 Générateur de sous-titres","de":"🎬 Untertitel-Generator","es":"🎬 Generador de subtítulos","pt":"🎬 Gerador de legendas","zh":"🎬 字幕生成器","ja":"🎬 字幕ジェネレーター","ko":"🎬 자막 생성기"},
    "tab.translator": {"en":"🌐 File Translator","ar":"🌐 ترجمة ملف جاهز","ru":"🌐 Переводчик файлов","fr":"🌐 Traducteur de fichiers","de":"🌐 Dateiübersetzer","es":"🌐 Traductor de archivos","pt":"🌐 Tradutor de arquivos","zh":"🌐 文件翻译器","ja":"🌐 ファイル翻訳","ko":"🌐 파일 번역기"},
    "tab.video_maker": {"en":"🎥 Video Maker","ar":"🎥 صانع الفيديو","ru":"🎥 Создатель видео","fr":"🎥 Créateur de vidéos","de":"🎥 Video-Ersteller","es":"🎥 Creador de vídeos","pt":"🎥 Criador de vídeos","zh":"🎥 视频制作器","ja":"🎥 ビデオメーカー","ko":"🎥 비디오 메이커"},
    "btn.select_files": {"en":"Select Files","ar":"اختر الملفات","ru":"Выбрать файлы","fr":"Sélectionner","de":"Dateien wählen","es":"Seleccionar","pt":"Selecionar","zh":"选择文件","ja":"ファイル選択","ko":"파일 선택"},
    "btn.process_all": {"en":"Process All","ar":"معالجة الكل","ru":"Обработать все","fr":"Tout traiter","de":"Alle verarbeiten","es":"Procesar todo","pt":"Processar tudo","zh":"全部处理","ja":"すべて処理","ko":"모두 처리"},
    "btn.stop": {"en":"Stop","ar":"إيقاف","ru":"Стоп","fr":"Arrêter","de":"Stopp","es":"Detener","pt":"Parar","zh":"停止","ja":"停止","ko":"중지"},
    "btn.clear": {"en":"Clear","ar":"مسح","ru":"Очистить","fr":"Effacer","de":"Löschen","es":"Limpiar","pt":"Limpar","zh":"清除","ja":"クリア","ko":"지우기"},
    "btn.dark_mode": {"en":"🌙 Dark","ar":"🌙 داكن","ru":"🌙 Тёмная","fr":"🌙 Sombre","de":"🌙 Dunkel","es":"🌙 Oscuro","pt":"🌙 Escuro","zh":"🌙 暗色","ja":"🌙 ダーク","ko":"🌙 다크"},
    "btn.light_mode": {"en":"☀️ Light","ar":"☀️ فاتح","ru":"☀️ Светлая","fr":"☀️ Clair","de":"☀️ Hell","es":"☀️ Claro","pt":"☀️ Claro","zh":"☀️ 亮色","ja":"☀️ ライト","ko":"☀️ 라이트"},
    "label.files_list": {"en":"Files to Process:","ar":"الملفات:","ru":"Файлы:","fr":"Fichiers :","de":"Dateien:","es":"Archivos:","pt":"Arquivos:","zh":"待处理文件：","ja":"ファイル：","ko":"파일:"},
    "label.speech_engine": {"en":"Speech Engine:","ar":"محرك الكلام:","ru":"Движок речи:","fr":"Moteur vocal :","de":"Sprach-Engine:","es":"Motor de voz:","pt":"Motor de fala:","zh":"语音引擎：","ja":"音声エンジン：","ko":"음성 엔진:"},
    "label.model": {"en":"Model:","ar":"النموذج:","ru":"Модель:","fr":"Modèle :","de":"Modell:","es":"Modelo:","pt":"Modelo:","zh":"模型：","ja":"モデル：","ko":"모델:"},
    "label.translation": {"en":"Translation:","ar":"الترجمة:","ru":"Перевод:","fr":"Traduction :","de":"Übersetzung:","es":"Traducción:","pt":"Tradução:","zh":"翻译：","ja":"翻訳：","ko":"번역:"},
    "label.translate_to": {"en":"To:","ar":"إلى:","ru":"На:","fr":"Vers :","de":"Nach:","es":"A:","pt":"Para:","zh":"目标：","ja":"翻訳先：","ko":"대상:"},
    "label.no_translation": {"en":"No Translation","ar":"بدون ترجمة","ru":"Без перевода","fr":"Pas de traduction","de":"Keine Übersetzung","es":"Sin traducción","pt":"Sem tradução","zh":"不翻译","ja":"翻訳なし","ko":"번역 없음"},
    "label.processing_log": {"en":"Processing Log:","ar":"سجل المعالجة:","ru":"Журнал обработки:","fr":"Journal :","de":"Protokoll:","es":"Registro:","pt":"Registro:","zh":"处理日志：","ja":"処理ログ：","ko":"처리 로그:"},
    "label.language": {"en":"Language:","ar":"اللغة:","ru":"Язык:","fr":"Langue :","de":"Sprache:","es":"Idioma:","pt":"Idioma:","zh":"语言：","ja":"言語：","ko":"언어:"},
    "msg.error": {"en":"Error","ar":"خطأ","ru":"Ошибка","fr":"Erreur","de":"Fehler","es":"Error","pt":"Erro","zh":"错误","ja":"エラー","ko":"오류"},
    "msg.success": {"en":"Success","ar":"نجاح","ru":"Успех","fr":"Succès","de":"Erfolg","es":"Éxito","pt":"Sucesso","zh":"成功","ja":"成功","ko":"성공"},
    "msg.no_files": {"en":"No files selected","ar":"لم يتم اختيار ملفات","ru":"Файлы не выбраны","fr":"Aucun fichier sélectionné","de":"Keine Dateien ausgewählt","es":"Sin archivos","pt":"Nenhum arquivo","zh":"未选择文件","ja":"ファイル未選択","ko":"파일 미선택"},
    "msg.no_engine": {"en":"Speech engine not loaded","ar":"محرك الكلام غير محمّل","ru":"Движок не загружен","fr":"Moteur non chargé","de":"Engine nicht geladen","es":"Motor no cargado","pt":"Motor não carregado","zh":"引擎未加载","ja":"エンジン未読込","ko":"엔진 미로드"},
    "msg.all_done": {"en":"All files processed successfully!","ar":"تمت معالجة جميع الملفات بنجاح!","ru":"Все файлы обработаны!","fr":"Tous les fichiers traités !","de":"Alle Dateien verarbeitet!","es":"¡Todos procesados!","pt":"Todos processados!","zh":"全部处理完成！","ja":"全ファイル処理完了！","ko":"모두 처리 완료!"},
    "msg.added_files": {"en":"Added {n} files","ar":"تمت إضافة {n} ملف","ru":"Добавлено {n} файлов","fr":"{n} fichiers ajoutés","de":"{n} Dateien hinzugefügt","es":"{n} archivos añadidos","pt":"{n} arquivos adicionados","zh":"已添加 {n} 个文件","ja":"{n} ファイルを追加","ko":"{n}개 파일 추가"},
    "msg.loaded_engine": {"en":"✅ Loaded {name} engine","ar":"✅ تم تحميل محرك {name}","ru":"✅ Загружен {name}","fr":"✅ Moteur {name} chargé","de":"✅ {name} geladen","es":"✅ Motor {name} cargado","pt":"✅ Motor {name} carregado","zh":"✅ 已加载 {name}","ja":"✅ {name} ロード完了","ko":"✅ {name} 로드됨"},
    "msg.restart_required": {"en":"Please restart SubLab for the language change to take full effect.","ar":"يرجى إعادة تشغيل SubLab لتطبيق تغيير اللغة بالكامل.","ru":"Перезапустите SubLab для применения.","fr":"Redémarrez SubLab pour appliquer.","de":"Bitte SubLab neu starten.","es":"Reinicie SubLab.","pt":"Reinicie o SubLab.","zh":"请重启 SubLab。","ja":"SubLabを再起動してください。","ko":"SubLab을 다시 시작하세요."},
    "msg.loading_model": {"en":"⏳ Loading model...","ar":"⏳ جاري تحميل النموذج...","ru":"⏳ Загрузка модели...","fr":"⏳ Chargement...","de":"⏳ Laden...","es":"⏳ Cargando...","pt":"⏳ Carregando...","zh":"⏳ 加载中...","ja":"⏳ 読込中...","ko":"⏳ 로드 중..."},
    "msg.model_still_loading": {"en":"The model is still being downloaded.\nPlease wait until complete.","ar":"النموذج لا يزال يُحمَّل.\nيرجى الانتظار حتى يكتمل التحميل.","ru":"Модель загружается.\nПодождите завершения.","fr":"Le modèle se télécharge.\nPatientez.","de":"Modell wird heruntergeladen.\nBitte warten.","es":"El modelo se está descargando.\nEspere.","pt":"O modelo está sendo baixado.\nAguarde.","zh":"模型下载中。\n请等待完成。","ja":"モデルダウンロード中。\n完了をお待ちください。","ko":"모델 다운로드 중.\n완료를 기다려 주세요."},
    "msg.loading_title": {"en":"Loading","ar":"جاري التحميل","ru":"Загрузка","fr":"Chargement","de":"Laden","es":"Cargando","pt":"Carregando","zh":"加载中","ja":"読込中","ko":"로드 중"},
    "msg.engine_error_title": {"en":"Engine Error","ar":"خطأ في المحرك","ru":"Ошибка движка","fr":"Erreur moteur","de":"Engine-Fehler","es":"Error del motor","pt":"Erro do motor","zh":"引擎错误","ja":"エンジンエラー","ko":"엔진 오류"},
    "msg.engine_load_failed": {"en":"Failed to load model:\n{error}\n\nCheck internet and try again.","ar":"فشل تحميل النموذج:\n{error}\n\nتحقق من الإنترنت وحاول مرة أخرى.","ru":"Ошибка загрузки:\n{error}\n\nПроверьте интернет.","fr":"Échec:\n{error}\n\nVérifiez la connexion.","de":"Fehler:\n{error}\n\nInternet prüfen.","es":"Error:\n{error}\n\nVerifique conexión.","pt":"Falha:\n{error}\n\nVerifique conexão.","zh":"加载失败:\n{error}\n\n请检查网络。","ja":"読込失敗:\n{error}\n\n接続を確認。","ko":"로드 실패:\n{error}\n\n인터넷 확인."},
    "dlg.model_download_title": {"en":"Model Download Required","ar":"يلزم تحميل النموذج","ru":"Требуется загрузка","fr":"Téléchargement requis","de":"Download erforderlich","es":"Descarga requerida","pt":"Download necessário","zh":"需要下载模型","ja":"ダウンロードが必要","ko":"다운로드 필요"},
    "dlg.model_not_found": {"en":"The model \"{model}\" ({size}) is not installed.\n\nDownload it now?","ar":"النموذج \"{model}\" ({size}) غير مثبت.\n\nهل تريد تحميله الآن؟","ru":"Модель \"{model}\" ({size}) не установлена.\n\nЗагрузить?","fr":"Le modèle \"{model}\" ({size}) manque.\n\nTélécharger ?","de":"Modell \"{model}\" ({size}) fehlt.\n\nJetzt laden?","es":"Modelo \"{model}\" ({size}) no instalado.\n\n¿Descargar?","pt":"Modelo \"{model}\" ({size}) ausente.\n\nBaixar?","zh":"模型\"{model}\"({size})未安装。\n\n立即下载？","ja":"モデル\"{model}\"({size})未インストール。\n\nダウンロード？","ko":"모델 \"{model}\"({size}) 미설치.\n\n다운로드?"},
    "dlg.downloading_model": {"en":"Downloading Model","ar":"جاري تحميل النموذج","ru":"Загрузка модели","fr":"Téléchargement","de":"Download","es":"Descargando","pt":"Baixando","zh":"下载模型中","ja":"ダウンロード中","ko":"다운로드 중"},
    "dlg.downloading_progress": {"en":"Downloading \"{model}\"... {pct}%","ar":"جاري تحميل \"{model}\"... {pct}%","ru":"Загрузка \"{model}\"... {pct}%","fr":"Téléchargement \"{model}\"... {pct}%","de":"Download \"{model}\"... {pct}%","es":"Descargando \"{model}\"... {pct}%","pt":"Baixando \"{model}\"... {pct}%","zh":"下载 \"{model}\"... {pct}%","ja":"\"{model}\" DL中... {pct}%","ko":"\"{model}\" 다운로드... {pct}%"},
    "dlg.download_complete": {"en":"Download complete! Loading...","ar":"اكتمل التحميل! جاري التحميل...","ru":"Загружено! Загрузка...","fr":"Terminé ! Chargement...","de":"Fertig! Laden...","es":"¡Completo! Cargando...","pt":"Concluído! Carregando...","zh":"下载完成！加载中...","ja":"完了！読込中...","ko":"완료! 로드 중..."},
    "dlg.download_cancelled": {"en":"Download cancelled.","ar":"تم إلغاء التحميل.","ru":"Загрузка отменена.","fr":"Annulé.","de":"Abgebrochen.","es":"Cancelado.","pt":"Cancelado.","zh":"已取消。","ja":"キャンセル。","ko":"취소됨."},
    "dlg.cancel": {"en":"Cancel","ar":"إلغاء","ru":"Отмена","fr":"Annuler","de":"Abbrechen","es":"Cancelar","pt":"Cancelar","zh":"取消","ja":"キャンセル","ko":"취소"},
    "tr_tab.title": {"en":"🌐 Translate Subtitle Files","ar":"🌐 ترجمة ملفات الترجمة الجاهزة","ru":"🌐 Перевод субтитров","fr":"🌐 Traduire les sous-titres","de":"🌐 Untertitel übersetzen","es":"🌐 Traducir subtítulos","pt":"🌐 Traduzir legendas","zh":"🌐 翻译字幕文件","ja":"🌐 字幕翻訳","ko":"🌐 자막 번역"},
    "tr_tab.description": {"en":"Select an SRT, CSV, or TXT file and translate it to any language","ar":"اختر ملف SRT أو CSV أو TXT وترجمه إلى أي لغة","ru":"Выберите файл и переведите на любой язык","fr":"Sélectionnez un fichier et traduisez-le","de":"Datei auswählen und übersetzen","es":"Seleccione un archivo y tradúzcalo","pt":"Selecione e traduza","zh":"选择字幕文件并翻译","ja":"ファイルを選択して翻訳","ko":"파일을 선택하여 번역"},
    "tr_tab.source_file": {"en":"📂 Source File","ar":"📂 الملف المصدر","ru":"📂 Исходный файл","fr":"📂 Fichier source","de":"📂 Quelldatei","es":"📂 Archivo fuente","pt":"📂 Arquivo fonte","zh":"📂 源文件","ja":"📂 ソースファイル","ko":"📂 원본 파일"},
    "tr_tab.no_file_selected": {"en":"No file selected","ar":"لم يتم اختيار ملف","ru":"Файл не выбран","fr":"Aucun fichier","de":"Keine Datei","es":"Sin archivo","pt":"Nenhum arquivo","zh":"未选择文件","ja":"ファイル未選択","ko":"파일 미선택"},
    "tr_tab.choose_file": {"en":"📁 Choose File","ar":"📁 اختر ملف","ru":"📁 Выбрать","fr":"📁 Choisir","de":"📁 Wählen","es":"📁 Elegir","pt":"📁 Escolher","zh":"📁 选择","ja":"📁 選択","ko":"📁 선택"},
    "tr_tab.translation_settings": {"en":"⚙️ Translation Settings","ar":"⚙️ إعدادات الترجمة","ru":"⚙️ Настройки","fr":"⚙️ Paramètres","de":"⚙️ Einstellungen","es":"⚙️ Ajustes","pt":"⚙️ Configurações","zh":"⚙️ 翻译设置","ja":"⚙️ 翻訳設定","ko":"⚙️ 번역 설정"},
    "tr_tab.translation_engine": {"en":"Translation Engine:","ar":"محرك الترجمة:","ru":"Движок:","fr":"Moteur :","de":"Engine:","es":"Motor:","pt":"Motor:","zh":"翻译引擎：","ja":"翻訳エンジン：","ko":"번역 엔진:"},
    "tr_tab.google_online": {"en":"🌐 Google Translate (Online)","ar":"🌐 Google Translate (أونلاين)","ru":"🌐 Google (Онлайн)","fr":"🌐 Google (En ligne)","de":"🌐 Google (Online)","es":"🌐 Google (En línea)","pt":"🌐 Google (Online)","zh":"🌐 Google翻译(在线)","ja":"🌐 Google(オンライン)","ko":"🌐 Google(온라인)"},
    "tr_tab.argos_offline": {"en":"📴 Argos Translate (Offline)","ar":"📴 Argos Translate (أوفلاين)","ru":"📴 Argos (Офлайн)","fr":"📴 Argos (Hors ligne)","de":"📴 Argos (Offline)","es":"📴 Argos (Sin conexión)","pt":"📴 Argos (Offline)","zh":"📴 Argos(离线)","ja":"📴 Argos(オフライン)","ko":"📴 Argos(오프라인)"},
    "tr_tab.translate_to": {"en":"Translate to:","ar":"الترجمة إلى:","ru":"Перевести на:","fr":"Traduire en :","de":"Übersetzen nach:","es":"Traducir a:","pt":"Traduzir para:","zh":"翻译为：","ja":"翻訳先：","ko":"번역 대상:"},
    "tr_tab.save_as": {"en":"Save as:","ar":"حفظ كـ:","ru":"Сохранить как:","fr":"Format :","de":"Speichern als:","es":"Guardar como:","pt":"Salvar como:","zh":"保存为：","ja":"保存形式：","ko":"저장 형식:"},
    "tr_tab.content_preview": {"en":"👁️ Content Preview","ar":"👁️ معاينة المحتوى","ru":"👁️ Предпросмотр","fr":"👁️ Aperçu","de":"👁️ Vorschau","es":"👁️ Vista previa","pt":"👁️ Pré-visualização","zh":"👁️ 内容预览","ja":"👁️ プレビュー","ko":"👁️ 미리보기"},
    "tr_tab.start_translation": {"en":"🚀 Start Translation","ar":"🚀 ابدأ الترجمة","ru":"🚀 Начать","fr":"🚀 Démarrer","de":"🚀 Starten","es":"🚀 Iniciar","pt":"🚀 Iniciar","zh":"🚀 开始翻译","ja":"🚀 翻訳開始","ko":"🚀 번역 시작"},
    "tr_tab.translating": {"en":"⏳ Translating...","ar":"⏳ جاري الترجمة...","ru":"⏳ Перевод...","fr":"⏳ Traduction...","de":"⏳ Übersetzung...","es":"⏳ Traduciendo...","pt":"⏳ Traduzindo...","zh":"⏳ 翻译中...","ja":"⏳ 翻訳中...","ko":"⏳ 번역 중..."},
    "tr_tab.operations_log": {"en":"📋 Operations Log","ar":"📋 سجل العمليات","ru":"📋 Журнал","fr":"📋 Journal","de":"📋 Protokoll","es":"📋 Registro","pt":"📋 Registro","zh":"📋 操作日志","ja":"📋 操作ログ","ko":"📋 작업 로그"},
    "tr_tab.loaded_n_subs": {"en":"✅ Loaded {n} subtitles","ar":"✅ تم تحميل {n} ترجمة","ru":"✅ Загружено {n}","fr":"✅ {n} chargés","de":"✅ {n} geladen","es":"✅ {n} cargados","pt":"✅ {n} carregadas","zh":"✅ 已加载 {n} 条","ja":"✅ {n} 個読込","ko":"✅ {n}개 로드"},
    "tr_tab.opened_file": {"en":"📂 Opened: {name} ({n} lines)","ar":"📂 تم فتح: {name} ({n} سطر)","ru":"📂 Открыт: {name} ({n})","fr":"📂 Ouvert: {name} ({n})","de":"📂 Geöffnet: {name} ({n})","es":"📂 Abierto: {name} ({n})","pt":"📂 Aberto: {name} ({n})","zh":"📂 已打开: {name} ({n}行)","ja":"📂 {name} ({n}行)","ko":"📂 {name} ({n}줄)"},
    "tr_tab.and_n_more": {"en":"... and {n} more","ar":"... و {n} آخر","ru":"... и ещё {n}","fr":"... et {n} de plus","de":"... und {n} mehr","es":"... y {n} más","pt":"... e mais {n}","zh":"... 还有 {n}","ja":"... 他{n}","ko":"... 외 {n}"},
    "tr_tab.unsupported_format": {"en":"❌ Unsupported format","ar":"❌ صيغة غير مدعومة","ru":"❌ Формат не поддерживается","fr":"❌ Format non supporté","de":"❌ Nicht unterstützt","es":"❌ No soportado","pt":"❌ Não suportado","zh":"❌ 不支持的格式","ja":"❌ 非対応","ko":"❌ 미지원"},
    "tr_tab.warning": {"en":"Warning","ar":"تنبيه","ru":"Предупреждение","fr":"Avertissement","de":"Warnung","es":"Advertencia","pt":"Aviso","zh":"警告","ja":"警告","ko":"경고"},
    "tr_tab.choose_file_first": {"en":"Please select a file first","ar":"يرجى اختيار ملف أولاً","ru":"Сначала выберите файл","fr":"Sélectionnez un fichier","de":"Bitte Datei wählen","es":"Seleccione un archivo","pt":"Selecione um arquivo","zh":"请先选择文件","ja":"ファイルを選択","ko":"파일을 선택하세요"},
    "tr_tab.choose_format": {"en":"Choose at least one save format","ar":"اختر صيغة حفظ واحدة على الأقل","ru":"Выберите формат","fr":"Choisissez un format","de":"Bitte Format wählen","es":"Elija un formato","pt":"Escolha um formato","zh":"请选择格式","ja":"形式を選択","ko":"형식을 선택하세요"},
    "tr_tab.choose_subtitle_file": {"en":"Choose Subtitle File","ar":"اختر ملف الترجمة","ru":"Выберите файл","fr":"Choisir fichier","de":"Datei wählen","es":"Elegir archivo","pt":"Escolher arquivo","zh":"选择字幕文件","ja":"字幕ファイル選択","ko":"자막 파일 선택"},
    "tr_tab.subtitle_files_filter": {"en":"Subtitle Files (*.srt *.csv *.txt);;SRT (*.srt);;CSV (*.csv);;TXT (*.txt)","ar":"ملفات الترجمة (*.srt *.csv *.txt);;SRT (*.srt);;CSV (*.csv);;TXT (*.txt)","ru":"Файлы субтитров (*.srt *.csv *.txt);;SRT (*.srt);;CSV (*.csv);;TXT (*.txt)","fr":"Sous-titres (*.srt *.csv *.txt);;SRT (*.srt);;CSV (*.csv);;TXT (*.txt)","de":"Untertitel (*.srt *.csv *.txt);;SRT (*.srt);;CSV (*.csv);;TXT (*.txt)","es":"Subtítulos (*.srt *.csv *.txt);;SRT (*.srt);;CSV (*.csv);;TXT (*.txt)","pt":"Legendas (*.srt *.csv *.txt);;SRT (*.srt);;CSV (*.csv);;TXT (*.txt)","zh":"字幕文件 (*.srt *.csv *.txt);;SRT (*.srt);;CSV (*.csv);;TXT (*.txt)","ja":"字幕 (*.srt *.csv *.txt);;SRT (*.srt);;CSV (*.csv);;TXT (*.txt)","ko":"자막 (*.srt *.csv *.txt);;SRT (*.srt);;CSV (*.csv);;TXT (*.txt)"},
    "tr_tab.choose_save_dir": {"en":"Choose Save Directory","ar":"اختر مجلد الحفظ","ru":"Папка сохранения","fr":"Dossier","de":"Speicherordner","es":"Carpeta","pt":"Pasta","zh":"选择保存目录","ja":"保存先","ko":"저장 폴더"},
    "tr_tab.translation_done": {"en":"✅ Translation Complete","ar":"✅ تمت الترجمة","ru":"✅ Перевод завершён","fr":"✅ Terminé","de":"✅ Fertig","es":"✅ Completo","pt":"✅ Concluído","zh":"✅ 翻译完成","ja":"✅ 完了","ko":"✅ 완료"},
    "tr_tab.translation_done_msg": {"en":"Translation completed!\nSaved to:\n{path}","ar":"تمت الترجمة بنجاح!\nتم الحفظ في:\n{path}","ru":"Перевод завершён!\nСохранено:\n{path}","fr":"Terminé !\n{path}","de":"Fertig!\n{path}","es":"¡Completo!\n{path}","pt":"Concluído!\n{path}","zh":"翻译完成！\n{path}","ja":"完了！\n{path}","ko":"완료!\n{path}"},
    "tr_tab.translation_failed": {"en":"❌ Translation Failed","ar":"❌ فشلت الترجمة","ru":"❌ Ошибка","fr":"❌ Échec","de":"❌ Fehler","es":"❌ Error","pt":"❌ Falha","zh":"❌ 翻译失败","ja":"❌ 失敗","ko":"❌ 실패"},
    "tr_tab.translation_failed_msg": {"en":"Translation failed. Check the log.","ar":"فشلت الترجمة. راجع السجل.","ru":"Ошибка. Проверьте журнал.","fr":"Échec. Vérifiez le journal.","de":"Fehler. Prüfen Sie das Protokoll.","es":"Error. Revise el registro.","pt":"Falha. Verifique o registro.","zh":"翻译失败，请检查日志。","ja":"失敗。ログ確認。","ko":"실패. 로그 확인."},
    "tr_tab.completed": {"en":"✅ Completed!","ar":"✅ اكتملت!","ru":"✅ Готово!","fr":"✅ Terminé !","de":"✅ Fertig!","es":"✅ ¡Listo!","pt":"✅ Pronto!","zh":"✅ 完成！","ja":"✅ 完了！","ko":"✅ 완료!"},
    "vm_tab.title": {"en":"🎬 Subtitle Video Maker","ar":"🎬 صانع فيديو الترجمات","ru":"🎬 Видео с субтитрами","fr":"🎬 Créateur vidéo","de":"🎬 Video-Ersteller","es":"🎬 Creador de vídeo","pt":"🎬 Criador de vídeo","zh":"🎬 字幕视频制作","ja":"🎬 字幕動画メーカー","ko":"🎬 자막 비디오 메이커"},
    "vm_tab.description": {"en":"Select audio and add SRT files to create subtitle video","ar":"اختر ملف صوت وأضف ملفات SRT لإنشاء فيديو بترجمات","ru":"Выберите аудио и SRT для создания видео","fr":"Sélectionnez audio et SRT pour créer une vidéo","de":"Audio und SRT wählen für Video","es":"Seleccione audio y SRT para crear vídeo","pt":"Selecione áudio e SRT para criar vídeo","zh":"选择音频和SRT文件创建字幕视频","ja":"音声とSRTから字幕動画を作成","ko":"오디오와 SRT로 자막 비디오 만들기"},
    "vm_tab.audio_file": {"en":"🔊 Audio File","ar":"🔊 ملف الصوت","ru":"🔊 Аудиофайл","fr":"🔊 Fichier audio","de":"🔊 Audiodatei","es":"🔊 Archivo de audio","pt":"🔊 Arquivo de áudio","zh":"🔊 音频文件","ja":"🔊 音声ファイル","ko":"🔊 오디오 파일"},
    "vm_tab.no_file_selected": {"en":"No file selected","ar":"لم يتم اختيار ملف","ru":"Файл не выбран","fr":"Aucun fichier","de":"Keine Datei","es":"Sin archivo","pt":"Nenhum arquivo","zh":"未选择文件","ja":"ファイル未選択","ko":"파일 미선택"},
    "vm_tab.choose": {"en":"📁 Choose","ar":"📁 اختيار","ru":"📁 Выбрать","fr":"📁 Choisir","de":"📁 Wählen","es":"📁 Elegir","pt":"📁 Escolher","zh":"📁 选择","ja":"📁 選択","ko":"📁 선택"},
    "vm_tab.srt_files": {"en":"📝 Subtitle Files (SRT)","ar":"📝 ملفات الترجمة (SRT)","ru":"📝 Файлы SRT","fr":"📝 Fichiers SRT","de":"📝 SRT-Dateien","es":"📝 Archivos SRT","pt":"📝 Arquivos SRT","zh":"📝 字幕文件(SRT)","ja":"📝 SRTファイル","ko":"📝 SRT 파일"},
    "vm_tab.add_srt_track": {"en":"➕ Add Subtitle Track","ar":"➕ إضافة مسار ترجمة","ru":"➕ Добавить дорожку","fr":"➕ Ajouter piste","de":"➕ Spur hinzufügen","es":"➕ Añadir pista","pt":"➕ Adicionar faixa","zh":"➕ 添加字幕轨道","ja":"➕ トラック追加","ko":"➕ 트랙 추가"},
    "vm_tab.track_count": {"en":"  📊 {filled}/{total} tracks selected","ar":"  📊 {filled}/{total} مسار محدد","ru":"  📊 {filled}/{total} дорожек","fr":"  📊 {filled}/{total} pistes","de":"  📊 {filled}/{total} Spuren","es":"  📊 {filled}/{total} pistas","pt":"  📊 {filled}/{total} faixas","zh":"  📊 已选{filled}/{total}","ja":"  📊 {filled}/{total}選択","ko":"  📊 {filled}/{total} 선택"},
    "vm_tab.video_settings": {"en":"⚙️ Video Settings","ar":"⚙️ إعدادات الفيديو","ru":"⚙️ Настройки видео","fr":"⚙️ Paramètres vidéo","de":"⚙️ Video-Einstellungen","es":"⚙️ Ajustes de vídeo","pt":"⚙️ Configurações","zh":"⚙️ 视频设置","ja":"⚙️ ビデオ設定","ko":"⚙️ 비디오 설정"},
    "vm_tab.video_style": {"en":"Video Style:","ar":"نمط الفيديو:","ru":"Стиль:","fr":"Style :","de":"Stil:","es":"Estilo:","pt":"Estilo:","zh":"视频样式：","ja":"スタイル：","ko":"스타일:"},
    "vm_tab.style_default": {"en":"🎨 Default (Light)","ar":"🎨 افتراضي (فاتح)","ru":"🎨 По умолчанию","fr":"🎨 Par défaut","de":"🎨 Standard","es":"🎨 Predeterminado","pt":"🎨 Padrão","zh":"🎨 默认(浅色)","ja":"🎨 デフォルト","ko":"🎨 기본"},
    "vm_tab.style_dark": {"en":"🌙 Dark","ar":"🌙 داكن","ru":"🌙 Тёмная","fr":"🌙 Sombre","de":"🌙 Dunkel","es":"🌙 Oscuro","pt":"🌙 Escuro","zh":"🌙 暗色","ja":"🌙 ダーク","ko":"🌙 다크"},
    "vm_tab.style_cinema": {"en":"🎬 Cinematic (1080p)","ar":"🎬 سينمائي (1080p)","ru":"🎬 Кино (1080p)","fr":"🎬 Cinéma (1080p)","de":"🎬 Kino (1080p)","es":"🎬 Cine (1080p)","pt":"🎬 Cinema (1080p)","zh":"🎬 电影(1080p)","ja":"🎬 シネマ(1080p)","ko":"🎬 시네마(1080p)"},
    "vm_tab.style_minimal": {"en":"✨ Minimal","ar":"✨ بسيط","ru":"✨ Минимальный","fr":"✨ Minimaliste","de":"✨ Minimal","es":"✨ Minimalista","pt":"✨ Minimalista","zh":"✨ 简约","ja":"✨ ミニマル","ko":"✨ 미니멀"},
    "vm_tab.output_file": {"en":"Output File:","ar":"ملف الإخراج:","ru":"Выходной файл:","fr":"Fichier sortie :","de":"Ausgabe:","es":"Salida:","pt":"Saída:","zh":"输出文件：","ja":"出力：","ko":"출력:"},
    "vm_tab.browse": {"en":"📁 Browse","ar":"📁 تصفح","ru":"📁 Обзор","fr":"📁 Parcourir","de":"📁 Durchsuchen","es":"📁 Explorar","pt":"📁 Procurar","zh":"📁 浏览","ja":"📁 参照","ko":"📁 찾기"},
    "vm_tab.generate_video": {"en":"🚀 Generate Video","ar":"🚀 إنشاء الفيديو","ru":"🚀 Создать видео","fr":"🚀 Générer","de":"🚀 Erstellen","es":"🚀 Generar","pt":"🚀 Gerar","zh":"🚀 生成视频","ja":"🚀 ビデオ生成","ko":"🚀 비디오 생성"},
    "vm_tab.generating": {"en":"⏳ Generating...","ar":"⏳ جارٍ الإنشاء...","ru":"⏳ Создание...","fr":"⏳ Génération...","de":"⏳ Generierung...","es":"⏳ Generando...","pt":"⏳ Gerando...","zh":"⏳ 生成中...","ja":"⏳ 生成中...","ko":"⏳ 생성 중..."},
    "vm_tab.remove_track_tooltip": {"en":"Remove this track","ar":"إزالة هذا المسار","ru":"Удалить дорожку","fr":"Supprimer","de":"Entfernen","es":"Eliminar","pt":"Remover","zh":"移除轨道","ja":"削除","ko":"제거"},
    "vm_tab.min_one_track": {"en":"At least one subtitle track required","ar":"يجب وجود مسار ترجمة واحد على الأقل","ru":"Минимум одна дорожка","fr":"Minimum une piste","de":"Mindestens eine Spur","es":"Mínimo una pista","pt":"Mínimo uma faixa","zh":"至少需要一个轨道","ja":"最低1トラック必要","ko":"최소 1개 트랙 필요"},
    "vm_tab.added_track": {"en":"➕ Added SRT track {n}","ar":"➕ تمت إضافة مسار SRT {n}","ru":"➕ Добавлена дорожка {n}","fr":"➕ Piste {n} ajoutée","de":"➕ Spur {n} hinzugefügt","es":"➕ Pista {n} añadida","pt":"➕ Faixa {n} adicionada","zh":"➕ 已添加轨道 {n}","ja":"➕ トラック{n}追加","ko":"➕ 트랙 {n} 추가"},
    "vm_tab.removed_track": {"en":"🗑️ Track removed (remaining: {n})","ar":"🗑️ تمت إزالة مسار (المتبقي: {n})","ru":"🗑️ Удалена (осталось: {n})","fr":"🗑️ Supprimée (reste: {n})","de":"🗑️ Entfernt (übrig: {n})","es":"🗑️ Eliminada (quedan: {n})","pt":"🗑️ Removida (restam: {n})","zh":"🗑️ 已移除(剩余:{n})","ja":"🗑️ 削除(残り:{n})","ko":"🗑️ 제거됨(남은:{n})"},
    "vm_tab.choose_audio": {"en":"Choose Audio File","ar":"اختر ملف الصوت","ru":"Выберите аудио","fr":"Choisir audio","de":"Audio wählen","es":"Elegir audio","pt":"Escolher áudio","zh":"选择音频","ja":"音声選択","ko":"오디오 선택"},
    "vm_tab.audio_selected": {"en":"🔊 Selected: {name}","ar":"🔊 تم اختيار: {name}","ru":"🔊 Выбрано: {name}","fr":"🔊 Sélectionné: {name}","de":"🔊 Gewählt: {name}","es":"🔊 Seleccionado: {name}","pt":"🔊 Selecionado: {name}","zh":"🔊 已选: {name}","ja":"🔊 選択: {name}","ko":"🔊 선택: {name}"},
    "vm_tab.save_video": {"en":"Save Video","ar":"حفظ الفيديو","ru":"Сохранить видео","fr":"Enregistrer","de":"Video speichern","es":"Guardar vídeo","pt":"Salvar vídeo","zh":"保存视频","ja":"ビデオ保存","ko":"비디오 저장"},
    "vm_tab.generation_complete": {"en":"✅ Complete!","ar":"✅ اكتمل!","ru":"✅ Готово!","fr":"✅ Terminé !","de":"✅ Fertig!","es":"✅ ¡Listo!","pt":"✅ Pronto!","zh":"✅ 完成！","ja":"✅ 完了！","ko":"✅ 완료!"},
    "vm_tab.generation_failed": {"en":"❌ Failed","ar":"❌ فشل","ru":"❌ Ошибка","fr":"❌ Échec","de":"❌ Fehler","es":"❌ Error","pt":"❌ Falha","zh":"❌ 失败","ja":"❌ 失敗","ko":"❌ 실패"},
    "vm_tab.video_saved": {"en":"Video created!\n📁 {path}","ar":"تم إنشاء الفيديو!\n📁 {path}","ru":"Видео создано!\n📁 {path}","fr":"Vidéo créée !\n📁 {path}","de":"Video erstellt!\n📁 {path}","es":"¡Vídeo creado!\n📁 {path}","pt":"Vídeo criado!\n📁 {path}","zh":"视频已创建！\n📁 {path}","ja":"ビデオ作成完了！\n📁 {path}","ko":"비디오 생성!\n📁 {path}"},
    "vm_tab.video_failed_msg": {"en":"Failed to generate video:\n{error}","ar":"فشل إنشاء الفيديو:\n{error}","ru":"Ошибка создания:\n{error}","fr":"Échec:\n{error}","de":"Fehler:\n{error}","es":"Error:\n{error}","pt":"Falha:\n{error}","zh":"视频生成失败:\n{error}","ja":"生成失敗:\n{error}","ko":"생성 실패:\n{error}"},
    "vm_tab.choose_srt": {"en":"Choose SRT #{n}","ar":"اختر SRT رقم {n}","ru":"Выберите SRT #{n}","fr":"SRT n°{n}","de":"SRT #{n}","es":"SRT #{n}","pt":"SRT #{n}","zh":"选择SRT #{n}","ja":"SRT #{n}","ko":"SRT #{n}"},
    "vm_tab.operations_log": {"en":"📋 Operations Log","ar":"📋 سجل العمليات","ru":"📋 Журнал","fr":"📋 Journal","de":"📋 Protokoll","es":"📋 Registro","pt":"📋 Registro","zh":"📋 操作日志","ja":"📋 操作ログ","ko":"📋 작업 로그"},
    "setup.title": {"en":"SubLab — First Run Setup","ar":"SubLab — إعداد التشغيل الأول","ru":"SubLab — Настройка","fr":"SubLab — Configuration","de":"SubLab — Ersteinrichtung","es":"SubLab — Configuración","pt":"SubLab — Configuração","zh":"SubLab — 首次设置","ja":"SubLab — 初回セットアップ","ko":"SubLab — 초기 설정"},
    "setup.checking": {"en":"Checking dependencies...","ar":"فحص المتطلبات...","ru":"Проверка...","fr":"Vérification...","de":"Prüfung...","es":"Verificando...","pt":"Verificando...","zh":"检查依赖...","ja":"確認中...","ko":"확인 중..."},
    "setup.ffmpeg_missing": {"en":"FFmpeg not found.\nClick 'Install' to download.","ar":"FFmpeg غير موجود.\nانقر 'تثبيت' للتحميل.","ru":"FFmpeg не найден.\nНажмите «Установить».","fr":"FFmpeg introuvable.\nCliquez «Installer».","de":"FFmpeg fehlt.\nKlicken Sie 'Installieren'.","es":"FFmpeg no encontrado.\nHaga clic 'Instalar'.","pt":"FFmpeg não encontrado.\nClique 'Instalar'.","zh":"未找到FFmpeg。\n点击'安装'。","ja":"FFmpegが見つかりません。\n「インストール」をクリック。","ko":"FFmpeg 없음.\n'설치' 클릭."},
    "setup.ffmpeg_ok": {"en":"✅ FFmpeg found","ar":"✅ تم العثور على FFmpeg","ru":"✅ FFmpeg найден","fr":"✅ FFmpeg trouvé","de":"✅ FFmpeg gefunden","es":"✅ FFmpeg encontrado","pt":"✅ FFmpeg encontrado","zh":"✅ 已找到FFmpeg","ja":"✅ FFmpeg発見","ko":"✅ FFmpeg 발견"},
    "setup.pip_missing": {"en":"Missing packages: {pkgs}\nClick 'Install'.","ar":"حزم مفقودة: {pkgs}\nانقر 'تثبيت'.","ru":"Не хватает: {pkgs}\nНажмите «Установить».","fr":"Manquants: {pkgs}\nCliquez «Installer».","de":"Fehlend: {pkgs}\nKlicken Sie 'Installieren'.","es":"Faltan: {pkgs}\nHaga clic 'Instalar'.","pt":"Faltando: {pkgs}\nClique 'Instalar'.","zh":"缺少: {pkgs}\n点击'安装'。","ja":"不足: {pkgs}\n「インストール」をクリック。","ko":"누락: {pkgs}\n'설치' 클릭."},
    "setup.pip_ok": {"en":"✅ All packages installed","ar":"✅ جميع الحزم مثبتة","ru":"✅ Все установлено","fr":"✅ Tout installé","de":"✅ Alles installiert","es":"✅ Todo instalado","pt":"✅ Tudo instalado","zh":"✅ 全部已安装","ja":"✅ 全てインストール済","ko":"✅ 모두 설치됨"},
    "setup.install": {"en":"Install","ar":"تثبيت","ru":"Установить","fr":"Installer","de":"Installieren","es":"Instalar","pt":"Instalar","zh":"安装","ja":"インストール","ko":"설치"},
    "setup.skip": {"en":"Skip","ar":"تخطي","ru":"Пропустить","fr":"Ignorer","de":"Überspringen","es":"Omitir","pt":"Pular","zh":"跳过","ja":"スキップ","ko":"건너뛰기"},
    "setup.continue": {"en":"Continue","ar":"متابعة","ru":"Продолжить","fr":"Continuer","de":"Weiter","es":"Continuar","pt":"Continuar","zh":"继续","ja":"続行","ko":"계속"},
    "setup.installing": {"en":"Installing... please wait","ar":"جارٍ التثبيت... انتظر","ru":"Установка... ждите","fr":"Installation...","de":"Installiere...","es":"Instalando...","pt":"Instalando...","zh":"安装中...","ja":"インストール中...","ko":"설치 중..."},
    "setup.done": {"en":"✅ Setup complete!","ar":"✅ اكتمل الإعداد!","ru":"✅ Настройка завершена!","fr":"✅ Terminé !","de":"✅ Fertig!","es":"✅ ¡Completo!","pt":"✅ Concluído!","zh":"✅ 设置完成！","ja":"✅ 完了！","ko":"✅ 완료!"},
    "setup.select_language": {"en":"Select Interface Language:","ar":"اختر لغة الواجهة:","ru":"Выберите язык:","fr":"Langue :","de":"Sprache:","es":"Idioma:","pt":"Idioma:","zh":"选择语言：","ja":"言語選択：","ko":"언어 선택:"},
}

_current_lang: str = "en"

def set_language(lang_code: str):
    global _current_lang
    if any(code == lang_code for code, _ in SUPPORTED_LANGUAGES):
        _current_lang = lang_code

def get_language() -> str:
    return _current_lang

def t(key: str, **kwargs) -> str:
    entry = _STRINGS.get(key)
    if not entry:
        return key
    text = entry.get(_current_lang) or entry.get("en", key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text

def is_rtl() -> bool:
    return _current_lang in RTL_LANGUAGES
