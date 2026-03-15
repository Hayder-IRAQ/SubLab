# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
"""
Video Generator Module — Production-grade subtitle video renderer
Supports moviepy v1 & v2, GPU encoding, Arabic/RTL text, configurable panels
"""

import re
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional, Callable, Dict
from dataclasses import dataclass, field

# Arabic text reshaping
try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    _reshaper = arabic_reshaper.ArabicReshaper(configuration={
        'language': 'Arabic',
        'support_ligatures': True,
        'support_zwj': True,
        'delete_harakat': False,
        'delete_tatweel': False,
        'support_arabic_indic_numbers': True,
    })
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    _reshaper = None


# ─── Text helpers ─────────────────────────────────────────────────────────────

def is_arabic(text: str) -> bool:
    for ch in text:
        if '\u0600' <= ch <= '\u06FF' or '\u0750' <= ch <= '\u077F' \
                or '\uFB50' <= ch <= '\uFDFF' or '\uFE70' <= ch <= '\uFEFF':
            return True
    return False


def fix_arabic_text(text: str) -> str:
    if ARABIC_SUPPORT and is_arabic(text):
        try:
            reshaped = _reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            try:
                return get_display(text)
            except Exception:
                return text
    return text


# ─── SRT Parser ──────────────────────────────────────────────────────────────

_SRT_PATTERN = re.compile(
    r'\d+\s*\n'
    r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*\n'
    r'(.*?)(?=\n\s*\n|\Z)',
    re.DOTALL
)


def _time_to_sec(t: str) -> float:
    t = t.replace(',', '.')
    h, m, rest = t.split(':')
    s, ms = rest.split('.')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_srt(path: str) -> List[Tuple[float, float, str]]:
    with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
        content = f.read()
    subtitles = []
    for m in _SRT_PATTERN.finditer(content):
        start = _time_to_sec(m.group(1))
        end = _time_to_sec(m.group(2))
        text = re.sub(r'<[^>]+>', '', m.group(3)).strip().replace('\n', ' ')
        if text:
            subtitles.append((start, end, text))
    return subtitles


def get_subtitle_at(subtitles: List[Tuple[float, float, str]], t: float) -> str:
    for start, end, text in subtitles:
        if start <= t <= end:
            return text
    return ""


# ─── Font Loader ─────────────────────────────────────────────────────────────

_font_cache: Dict[str, ImageFont.FreeTypeFont] = {}


def _find_font(candidates: List[str], size: int) -> ImageFont.FreeTypeFont:
    cache_key = f"{','.join(candidates)}:{size}"
    if cache_key in _font_cache:
        return _font_cache[cache_key]
    for fp in candidates:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, size)
                _font_cache[cache_key] = font
                return font
            except Exception:
                continue
    font = ImageFont.load_default()
    _font_cache[cache_key] = font
    return font


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return _find_font([
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ], size)


def load_arabic_font(size: int) -> ImageFont.FreeTypeFont:
    return _find_font([
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/tradbdo.ttf",
        "C:/Windows/Fonts/trado.ttf",
        "C:/Windows/Fonts/arabtype.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ], size)


# ─── Text Measurement & Wrapping ─────────────────────────────────────────────

def get_text_size(draw: ImageDraw.Draw, text: str, font) -> Tuple[int, int]:
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        return draw.textsize(text, font=font)


def wrap_text(text: str, font, max_width: int, draw: ImageDraw.Draw) -> str:
    words = text.split()
    if not words:
        return text
    lines = []
    current = []
    for word in words:
        test = ' '.join(current + [word])
        w, _ = get_text_size(draw, test, font)
        if w <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return '\n'.join(lines) if lines else text


# ─── Video Style Presets ─────────────────────────────────────────────────────

@dataclass
class VideoStyle:
    name: str = "default"
    width: int = 1280
    height: int = 720
    fps: int = 24
    bg_color: Tuple[int, int, int] = (255, 255, 255)
    panel_colors: List[Tuple[int, int, int]] = field(default_factory=lambda: [
        (235, 245, 255), (255, 248, 235), (235, 255, 240)
    ])
    text_colors: List[Tuple[int, int, int]] = field(default_factory=lambda: [
        (20, 70, 160), (110, 30, 110), (15, 90, 50)
    ])
    divider_color: Tuple[int, int, int] = (190, 190, 210)
    shadow_color: Tuple[int, int, int] = (160, 160, 160)
    font_size_large: int = 38
    font_size_small: int = 28
    arabic_font_size_large: int = 42
    arabic_font_size_small: int = 32
    show_progress_bar: bool = True
    shadow_offset: int = 2


STYLE_PRESETS = {
    "default": VideoStyle(),
    "dark": VideoStyle(
        name="dark",
        bg_color=(30, 30, 40),
        panel_colors=[(35, 40, 60), (40, 35, 55), (35, 45, 40)],
        text_colors=[(130, 180, 255), (200, 150, 255), (130, 220, 160)],
        divider_color=(70, 70, 90),
        shadow_color=(10, 10, 10),
    ),
    "cinema": VideoStyle(
        name="cinema",
        width=1920,
        height=1080,
        bg_color=(15, 15, 15),
        panel_colors=[(20, 20, 30), (25, 20, 25), (20, 25, 20)],
        text_colors=[(255, 215, 0), (255, 180, 120), (180, 255, 200)],
        divider_color=(50, 50, 60),
        shadow_color=(0, 0, 0),
        font_size_large=48,
        font_size_small=36,
        arabic_font_size_large=52,
        arabic_font_size_small=38,
    ),
    "minimal": VideoStyle(
        name="minimal",
        bg_color=(250, 250, 250),
        panel_colors=[(250, 250, 250), (250, 250, 250), (250, 250, 250)],
        text_colors=[(40, 40, 40), (40, 40, 40), (40, 40, 40)],
        divider_color=(220, 220, 220),
        shadow_color=(200, 200, 200),
        show_progress_bar=False,
    ),
}


# ─── GPU Codec Detection ────────────────────────────────────────────────────

def detect_gpu_codec() -> str:
    try:
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout + result.stderr
        for codec in ("h264_nvenc", "h264_amf", "h264_qsv"):
            if codec in output:
                return codec
    except Exception:
        pass
    return "libx264"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _cycle_list(lst: list, n: int) -> list:
    """Extend a list cyclically to length n."""
    if not lst:
        return [(128, 128, 128)] * n
    return [lst[i % len(lst)] for i in range(n)]


# ─── Video Generator ─────────────────────────────────────────────────────────

class VideoGenerator:
    def __init__(
        self,
        audio_path: str,
        srt_paths: List[str],
        output_path: str,
        style: Optional[VideoStyle] = None,
        progress_callback: Optional[Callable] = None,
    ):
        self.audio_path = audio_path
        self.srt_paths = srt_paths
        self.output_path = output_path
        self.style = style or VideoStyle()
        self.cb = progress_callback or (lambda msg, p=None: None)

    def create(self):
        try:
            from moviepy.editor import AudioFileClip, VideoClip
        except ImportError:
            from moviepy import AudioFileClip, VideoClip

        self.cb("🎵 تحميل الصوت...", 10)
        audio = AudioFileClip(self.audio_path)
        duration = audio.duration

        self.cb("📖 قراءة ملفات الترجمة...", 20)
        num_tracks = len(self.srt_paths)
        subtitles = [parse_srt(p) for p in self.srt_paths]

        self.cb(f"🎨 تحضير اللوحة ({num_tracks} مسار)...", 30)
        s = self.style

        # Auto-scale font size based on number of panels
        font_scale = min(1.0, 3.0 / max(num_tracks, 1))
        fl = max(16, int(s.font_size_large * font_scale))
        fs = max(14, int(s.font_size_small * font_scale))
        afl = max(18, int(s.arabic_font_size_large * font_scale))
        afs = max(16, int(s.arabic_font_size_small * font_scale))

        font_large = load_font(fl)
        font_small = load_font(fs)
        arabic_font_large = load_arabic_font(afl)
        arabic_font_small = load_arabic_font(afs)

        # Auto-scale height: 240px per panel, min 720
        effective_height = max(s.height, num_tracks * 240)
        panel_h = effective_height // num_tracks

        # Extend panel/text colors cyclically
        panel_colors = _cycle_list(s.panel_colors, num_tracks)
        text_colors = _cycle_list(s.text_colors, num_tracks)

        def make_frame(t):
            img = Image.new("RGB", (s.width, effective_height), s.bg_color)
            draw = ImageDraw.Draw(img)

            for i in range(num_tracks):
                y0 = i * panel_h
                y1 = (i + 1) * panel_h

                draw.rectangle([0, y0, s.width, y1], fill=panel_colors[i])

                if i > 0:
                    draw.rectangle([20, y0, s.width - 20, y0 + 2], fill=s.divider_color)

                text = get_subtitle_at(subtitles[i], t)
                if not text:
                    continue

                arabic = is_arabic(text)
                if arabic:
                    display_text = fix_arabic_text(text)
                    font = arabic_font_large if len(text) < 60 else arabic_font_small
                else:
                    display_text = text
                    font = font_large if len(text) < 60 else font_small

                wrapped = wrap_text(display_text, font, s.width - 100, draw)
                tw, th = get_text_size(draw, wrapped, font)
                cx = (s.width - tw) // 2
                cy = y0 + (panel_h - th) // 2

                off = s.shadow_offset
                draw.text((cx + off, cy + off), wrapped, font=font, fill=s.shadow_color)
                draw.text((cx, cy), wrapped, font=font, fill=text_colors[i])

                if s.show_progress_bar:
                    bar_w = int((s.width - 100) * (t % 1.0))
                    draw.rectangle([50, y1 - 6, 50 + bar_w, y1 - 3], fill=text_colors[i])

            return np.array(img)

        self.cb("🎬 إنشاء الفيديو...", 40)
        video = VideoClip(make_frame, duration=duration)

        try:
            video = video.with_audio(audio)
        except AttributeError:
            video = video.set_audio(audio)

        self.cb("💾 حفظ الملف...", 70)
        codec = detect_gpu_codec()
        self.cb(f"⚡ استخدام: {codec}", 72)

        ffmpeg_params = []
        if codec == "h264_nvenc":
            ffmpeg_params = [
                "-preset", "p4", "-rc", "vbr", "-cq", "23",
                "-b:v", "0", "-maxrate", "10M", "-bufsize", "20M",
            ]

        write_kwargs = dict(fps=s.fps, codec=codec, audio_codec="aac")
        if ffmpeg_params:
            write_kwargs["ffmpeg_params"] = ffmpeg_params

        self._write_with_fallback(video, write_kwargs)

        try:
            audio.close()
            video.close()
        except Exception:
            pass

        self.cb("✅ اكتمل!", 100)

    def _write_with_fallback(self, video, write_kwargs: dict):
        s = self.style
        try:
            video.write_videofile(self.output_path, **write_kwargs, verbose=False, logger=None)
        except TypeError:
            try:
                video.write_videofile(self.output_path, **write_kwargs)
            except Exception as e:
                self.cb(f"⚠️ GPU فشل ({e.__class__.__name__}), تراجع إلى CPU...", 73)
                video.write_videofile(
                    self.output_path, fps=s.fps,
                    codec="libx264", audio_codec="aac",
                )
        except Exception as e:
            self.cb(f"⚠️ GPU فشل ({e.__class__.__name__}), تراجع إلى CPU...", 73)
            try:
                video.write_videofile(
                    self.output_path, fps=s.fps,
                    codec="libx264", audio_codec="aac",
                    verbose=False, logger=None,
                )
            except TypeError:
                video.write_videofile(
                    self.output_path, fps=s.fps,
                    codec="libx264", audio_codec="aac",
                )
