# Aura - Secure Local Personal Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Privacy-Secure-green?style=for-the-badge&logo=lock" alt="Privacy Secure">
  <img src="https://img.shields.io/badge/Platform-Termux/Android-red?style=for-the-badge&logo=android" alt="Platform Termux">
  <img src="https://img.shields.io/badge/LLM-Sarvam-blue?style=for-the-badge&logo=brain" alt="LLM Sarvam">
</p>

**Aura** is a secure, privacy-focused AI personal assistant that runs entirely on your Android phone. It is a hardended fork of the concepts behind PicoClaw/OpenClaw, but with a strict "Closed Box" security model where **no data leaves your device** and **the agent has zero internet access** for its brain.

## 🔒 Security First

- **Air-Gapped Brain**: The LLM runs offline (local inference).
- **Zero Data Leakage**: No third-party plugins, no community sharing.
- **Policy Engine**: Strict allowlist/denylist for tools.
- **Human-in-the-Loop**: Sensitive actions (calls, messages) require user approval.

## 🚀 Features

- **Voice**: Voice commands (STT) and responses (TTS).
- **Calls**: Answer/Make calls when you are unavailable.
- **Messages**: Read/Reply to WhatsApp/SMS.
- **Calendar**: Manage events and reminders.
- **Privacy**: No cloud, no tracking, 100% local.

## 🛠️ Installation (Termux)

1. **Install Termux** from F-Droid (DO NOT use Play Store version).
2. **Run Setup**:
   ```bash
   pkg update && pkg install -y git
   git clone https://github.com/YOUR_USERNAME/aura-secure-assistant.git
   cd aura-secure-assistant
   bash scripts/setup_termux.sh
   ```
3. **Download Model**:
   - Download `sarvam-1.gguf` (or `sarvam-m`) and place it in `models/`.
4. **Configure**:
   - Edit `config.yaml` with your Telegram Bot Token.
5. **Run**:
   ```bash
   python -m src.interface.telegram_bot
   ```

## 🧠 Architecture

- **Interface**: Telegram Bot (Python)
- **Agent**: Local LLM (llama.cpp/Sarvam) + Policy Engine
- **System**: Termux API (Android Bridge)

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Security Model](docs/SECURITY.md)
- [Sarvam Integration](docs/SARVAM_INTEGRATION.md)

## 🤝 Contributing

This is a private project for personal use. However, feel free to fork and submit PRs for security fixes.
