<p align="center">
  <img src="/icon.png" width="128" alt="GamePadTester icon" />
</p>
<h1 align="center">GamePadTester</h1>
<p align="center">
  <a href="https://github.com/deuxdoom/GamePadTester/releases"><img src="https://img.shields.io/github/v/release/deuxdoom/GamePadTester?logo=github" alt="release"/></a>
  <a href="https://github.com/deuxdoom/GamePadTester/blob/main/LICENSE"><img src="https://img.shields.io/github/license/deuxdoom/GamePadTester" alt="license"/></a>
  <img src="https://img.shields.io/badge/OS-Windows-0078D6?logo=windows" alt="os"/>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python" alt="python"/>
  <img src="https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt" alt="pyside6"/>
  <a href="https://github.com/deuxdoom/GamePadTester/releases"><img src="https://img.shields.io/github/downloads/deuxdoom/GamePadTester/total?logo=github" alt="downloads"/></a>
</p>

> Windows XInput gamepad tester with clean GUI: polling-rate metrics, column-aligned D-Pad/ABXY, dual-stick circularity charts, rumble test, TXT export, and optional device names.

---

## ✨ Features
- **Polling-rate analysis**: mean/median (Hz & ms), stability %, sample count (select 1000 / 2000 / 4000)
- **Interactive diagram**: D-Pad & ABXY **column-aligned**, LB/RB, Option/Menu
- **Dual-stick circularity** visualization with Avg Error %
- **Rumble tester**: left/right motor sliders, instant toggle
- **TXT export**: save summary & raw intervals
- **Optional device name** via `pygame` (fallback to subtype when unavailable)
- **Crisp layout**: aspect-ratio container prevents center pad from getting squashed

## 📦 Install
    # 1) Create (optional) venv
    python -m venv .venv
    # Windows PowerShell
    . .\.venv\Scripts\Activate.ps1

    # 2) Install deps
    pip install -U pip
    pip install PySide6 pygame   # pygame is optional (friendly device names)

## 🚀 Run
    python GamePadTester.py

## 🖼️ Icon in README (docs/icon.png)
If you already have `icon.py` with `ICON_BASE64`, you can generate the PNG once:

    from icon import ICON_BASE64
    import base64, pathlib
    p = pathlib.Path('docs'); p.mkdir(exist_ok=True)
    (p/'icon.png').write_bytes(base64.b64decode(ICON_BASE64))
    print('Wrote docs/icon.png')

## 📷 Screenshots
Place screenshots under `docs/` and they will render below:

<p align="center">
  <img src="docs/screenshot-1.png" alt="main" width="45%"/>
  <img src="docs/screenshot-2.png" alt="sticks" width="45%"/>
</p>

## 📝 Notes
- Windows only (XInput backend)
- App/Taskbar icon is loaded from `icon.py` (BASE64)
- TXT saves to a user-selected path (default: alongside executable)

## 🔗 References
- XInput samples & polling ideas:
  - https://github.com/chrizonix/XInputTest
  - https://github.com/cakama3a/Polling

## 📄 License
See [LICENSE](LICENSE).
