"""Configuration for the Gemini API.

Set the GEMINI_API_KEY environment variable before running the application.
"""

import os


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
