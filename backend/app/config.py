"""
config.py

Every setting and secret is read ONCE, here. Everywhere else in the app
imports `settings` from this file rather than reading os.environ directly.

Why: if you later change how settings load (from a .env file to AWS
Secrets Manager, say), you change one file instead of twenty.
"""

import os

from dotenv import load_dotenv

# Finds the .env file and loads its contents into the environment,
# so os.environ can see them.
load_dotenv(override=True)


class Settings:
    """
    Settings class to hold configuration values for the application.
    Reads values from environment variables and provides default values
    if not set.
    """

    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")


settings = Settings()
