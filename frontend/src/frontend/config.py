"""Configuration for the Streamlit frontend."""

import os

BACKEND_URL: str = os.environ.get("BACKEND_URL", "http://localhost:8000")
