<div align="center">

# 🎬 SubLab — Professional Subtitle Studio

**Auto-generate, translate, and burn subtitles into videos — all offline-capable.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green)]()
[![GPU](https://img.shields.io/badge/GPU-CUDA%20Accelerated-76b900?logo=nvidia)]()

</div>

---

## ✨ Features

| Feature | Details |
|---|---|
| 🗣️ **Speech Recognition** | OpenAI Whisper (7 model sizes) + Vosk (40+ languages, offline) |
| 🌐 **Translation** | Google Translate (online) + Argos Translate (offline) |
| 🎥 **Video Maker** | Burn subtitles directly into video with custom styles |
| 📂 **Batch Processing** | Process multiple video files at once |
| 📤 **Export Formats** | SRT, VTT, CSV, JSON |
| 🌍 **UI Languages** | English, Arabic, Russian, French, German, Spanish, Portuguese, Chinese, Japanese, Korean |
| 🌙 **Dark / Light Mode** | Full theme support |
| ⚡ **GPU Acceleration** | CUDA support for Whisper |
| 🛠️ **First-Run Wizard** | Auto-installs FFmpeg and required packages |

---

## 📸 Screenshots

> _Coming soon_

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Hayder-IRAQ/SubLab.git
cd SubLab
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **GPU users:** Install PyTorch with CUDA support first:
> ```bash
> pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
> ```

### 4. Run SubLab
```bash
python main.py
```

On first launch, the **Setup Wizard** will automatically:
- Detect your system
- Download FFmpeg if needed
- Verify all required packages
- Let you choose your preferred UI language

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `PyQt5` | GUI framework |
| `openai-whisper` | AI speech recognition |
| `vosk` | Offline speech recognition |
| `googletrans` | Online translation |
| `argostranslate` | Offline translation |
| `moviepy` | Video processing |
| `opencv-python` | Video frame handling |
| `arabic-reshaper` + `python-bidi` | Arabic text rendering |
| `torch` *(optional)* | GPU acceleration |

---

## 🗂️ Project Structure

```
SubLab/
├── main.py                  # Entry point & setup wizard
├── requirements.txt
├── audio/
│   └── extractor.py         # FFmpeg / OpenCV audio extraction
├── engines/
│   ├── whisper_engine.py    # OpenAI Whisper engine (GPU-accelerated)
│   └── vosk_engine.py       # Vosk offline engine (40+ languages)
├── translation/
│   ├── translator.py        # Unified translation manager
│   ├── google_translator.py # Google Translate backend
│   └── argos_translator.py  # Argos Translate backend (offline)
├── ui/
│   ├── main_window.py       # Main application window
│   ├── subtitle_editor.py   # Subtitle editing widget
│   ├── subtitle_translator_tab.py
│   ├── video_maker_tab.py
│   ├── video_generator.py
│   └── template_manager.py
├── utils/
│   ├── config.py            # Configuration management
│   ├── export.py            # SRT / VTT / CSV / JSON export
│   ├── i18n.py              # Internationalization (10 languages)
│   ├── logger.py            # Logging setup
│   ├── setup_wizard.py      # First-run wizard
│   └── time_utils.py        # Subtitle timestamp utilities
├── models/
│   ├── whisper/             # Whisper model cache
│   └── vosk/                # Vosk model files
├── icons/                   # Application icons
└── tests/                   # Unit & integration tests
```

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## 🎙️ Speech Engine Comparison

| | Whisper | Vosk |
|---|---|---|
| **Accuracy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Speed** | Medium (GPU: Fast) | Fast |
| **Offline** | ✅ | ✅ |
| **Languages** | 99+ | 40+ |
| **GPU Support** | ✅ CUDA | ❌ |
| **Model Size** | 39 MB – 1.5 GB | 32 MB – 2.3 GB |

---

## 🌐 Translation Engines

| | Google Translate | Argos Translate |
|---|---|---|
| **Internet Required** | ✅ | ❌ (fully offline) |
| **Languages** | 130+ | 30+ pairs |
| **Quality** | Excellent | Good |
| **Cost** | Free (unofficial API) | Free & open source |

---

## 🗣️ Supported Vosk Languages

English · Arabic · Chinese · Russian · French · German · Spanish · Portuguese · Italian · Dutch · Turkish · Japanese · Korean · Hindi · Polish · Ukrainian · Greek · Vietnamese · Farsi · Filipino · Kazakh · Swedish · Uzbek · and more…

---

## ⚙️ Configuration

Settings are saved automatically to:
- **Windows:** `%APPDATA%\VideoSubtitleGenerator\Settings.json`
- **Linux/macOS:** `~/.config/VideoSubtitleGenerator/Settings.json`

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License**.

You may use, share, and adapt this work for **non-commercial purposes only**, with appropriate credit.

[View License](LICENSE) · [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)

---

## 👤 Author

**Hayder Odhafa**  
GitHub: [@Hayder-IRAQ](https://github.com/Hayder-IRAQ)

---

<div align="center">
Made with ❤️ — SubLab v3.0 © 2025 Hayder Odhafa
</div>
