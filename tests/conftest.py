import os

# src.llm_client raises at import time if ANTHROPIC_API_KEY is missing. The
# tests mock every Claude call, so a dummy key is enough to let the modules
# import and the suite run locally and in CI without a real credential.
os.environ.setdefault("ANTHROPIC_API_KEY", "dummy-key-for-tests")
