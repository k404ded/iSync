"""
Root entry point for Streamlit Community Cloud and local CLI.
Allows deployment using either `main.py` or `app/main.py`.
"""
import sys
from pathlib import Path

# Ensure workspace root is at the front of sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Execute the primary application
import app.main
