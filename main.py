#!/usr/bin/env python3
# Copyright (c) 2025 Hayder Odhafa
# Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
"""
SubLab — Professional Video Subtitle Generator & Video Maker
Main entry point with first-run setup wizard
"""

import sys
import os
import logging
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger
from utils.config import Config


def check_gpu_availability() -> dict:
    gpu_info = {'cuda_available': False, 'device_name': 'CPU', 'memory': 'N/A'}
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info['cuda_available'] = True
            gpu_info['device_name'] = torch.cuda.get_device_name(0)
            gpu_info['memory'] = f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB"
    except ImportError:
        pass
    return gpu_info


def optimize_gpu_memory():
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.set_per_process_memory_fraction(0.8)
            if hasattr(torch.backends.cuda, 'matmul'):
                torch.backends.cuda.matmul.allow_tf32 = True
            if hasattr(torch.backends.cudnn, 'allow_tf32'):
                torch.backends.cudnn.allow_tf32 = True
    except Exception:
        pass


def check_models_directory():
    for d in [Path("models/whisper"), Path("models/vosk")]:
        d.mkdir(parents=True, exist_ok=True)
        (d / ".gitkeep").touch(exist_ok=True)


def main():
    logger = setup_logger()
    logger.info("Starting SubLab v3.0")

    config = Config()

    # ── Load saved language into i18n ──
    from utils.i18n import set_language
    saved_lang = config.get("ui_language", "en")
    set_language(saved_lang)

    # ── PyQt5 app must exist before any widget ──
    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from PyQt5.QtGui import QIcon

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    app.setApplicationName("SubLab")
    app.setApplicationVersion("3.0")

    icon_path = Path("icons/app_icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # ── First-run setup wizard ──
    from utils.setup_wizard import needs_setup, run_setup_wizard, add_ffmpeg_to_path

    if needs_setup(config):
        logger.info("Running first-run setup wizard")
        run_setup_wizard(config)
    else:
        # Ensure bundled ffmpeg is on PATH even if setup was done previously
        add_ffmpeg_to_path()

    # Re-read language (might have changed in wizard)
    set_language(config.get("ui_language", "en"))

    # ── GPU ──
    gpu_info = check_gpu_availability()
    if gpu_info['cuda_available']:
        config.set('device', 'cuda')
        logger.info(f"GPU: {gpu_info['device_name']}")
    else:
        config.set('device', 'cpu')

    optimize_gpu_memory()
    check_models_directory()

    # ── Launch main window ──
    try:
        from ui.main_window import SubLabMainWindow
        window = SubLabMainWindow(config, gpu_info)
        window.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        sys.exit(1)
    finally:
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        config.save()
        logger.info("Application closed")


if __name__ == "__main__":
    main()
