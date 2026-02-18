"""
Direct Telegram Test
"""

import os
import sys

os.environ["TELEGRAM_BOT_TOKEN"] = "7573691331:AAFTsne004fhKUgQQT6ydRVh6mazfkl7Ks0"
os.environ["LLM_PROVIDER"] = "mock"

sys.path.insert(0, ".")
import main

main.main()
