"""Core constants for AURA 2.0 - AGI Assistant"""

# Memory Tiers
MEMORY_EPHEMERAL_TTL = 300  # 5 minutes
MEMORY_WORKING_TTL = 86400  # 24 hours
MEMORY_PRUNE_DAYS = 30

# Brain Layers
WATCHER_CHECK_INTERVAL = 1  # seconds
CALL_AUTO_ANSWER_DELAY = 20  # seconds
THINKER_IDLE_TIMEOUT = 300  # 5 minutes

# Security
SECURITY_LEVEL_LOW = 0
SECURITY_LEVEL_MEDIUM = 1
SECURITY_LEVEL_HIGH = 2
SECURITY_LEVEL_CRITICAL = 3

# Paths
DATA_DIR = "data"
MEMORY_DIR = "data/memory"
LOGS_DIR = "data/logs"
MODELS_DIR = "~/llama.cpp/models"
LLAMA_CLI = "~/llama.cpp/build/bin/llama-cli"

# Hard-coded immutable security rules
NEVER_ALLOWED_ACTIONS = [
    "execute_shell",
    "modify_system_files",
    "install_unknown_apps",
    "share_passwords",
    "access_bank_apps",
    "transfer_money",
    "request_root",
]
