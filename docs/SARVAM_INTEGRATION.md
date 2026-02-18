# Sarvam Integration Guide

## 1. Model Options

We will use **Sarvam Models** for the LLM Brain.
Since we want **Offline Privacy**, we will download the weights and run them locally using `llama.cpp` or `Ollama`.

### Recommended Models
1.  **Sarvam-M (24B)**: Best reasoning, but requires high RAM (16GB+).
2.  **Sarvam-1 (2B)**: Lightweight, runs on mobile, lower reasoning.

For a **Moto G45** (4-6GB RAM), we recommend **Sarvam-1 (2B)** or a quantized **Sarvam-M (4-bit)**.

## 2. How to Download & Convert

*Since Sarvam models are on Hugging Face, you can convert them to GGUF (llama.cpp format).*

### Step 1: Install Dependencies (Termux/PC)
```bash
pip install huggingface-hub
```

### Step 2: Download Model
```python
from huggingface_hub import snapshot_download
snapshot_download(repo_id="sarvamai/sarvam-1", local_dir="./models/sarvam-1")
```

### Step 3: Convert to GGUF
Use `llama.cpp` conversion tools to create a `.gguf` file.
*(Note: This requires a PC with more RAM for conversion, then transfer to phone).*

## 3. Configuration in Aura

Edit `config.yaml`:
```yaml
llm:
  model_path: "/sdcard/downloads/sarvam-1.gguf"
  context_size: 4096
  gpu_layers: 0 # Mobile phones often run faster on CPU for small models
```

## 4. Voice Models (STT/TTS)
We will use **Sarvam's Voice Models** if available offline, or use open alternatives:
- **STT**: Faster-Whisper (base model)
- **TTS**: Piper (English) / Coqui TTS (Indic)
