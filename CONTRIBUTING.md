# Contributing to SubLab

Thank you for considering a contribution to SubLab! Here's how to get started.

## How to Contribute

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. Create a **feature branch**: `git checkout -b feature/your-feature`
4. Make your changes following the code style below
5. **Run tests**: `pytest tests/ -v`
6. **Commit**: `git commit -m "feat: describe your change"`
7. **Push**: `git push origin feature/your-feature`
8. Open a **Pull Request** against `main`

## Code Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for all public methods
- Keep copyright headers in new files:
  ```python
  # Copyright (c) 2025 Hayder Odhafa
  # Licensed under CC BY-NC 4.0 (Non-Commercial). See LICENSE file for details.
  ```

## Reporting Bugs

Please open an issue with:
- Your operating system and Python version
- Steps to reproduce
- The full error traceback from the log file

## Adding a New Language to the UI

Edit `utils/i18n.py` — add your language code to `SUPPORTED_LANGUAGES` and provide translations for all keys in `_STRINGS`.

## License

By contributing, you agree that your contributions will be licensed under the same CC BY-NC 4.0 license as the project.
