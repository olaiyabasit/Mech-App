#!/usr/bin/env python
"""
Simple build script to copy Tailwind styles for development.
This is a workaround for the django-tailwind build timeout issue.
"""

import os
import shutil
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent
THEME_DIR = BASE_DIR / "theme"
STATIC_SRC = THEME_DIR / "static_src" / "src" / "styles.css"
STATIC_OUTPUT_DIR = THEME_DIR / "static" / "css"
STATIC_OUTPUT_FILE = STATIC_OUTPUT_DIR / "styles.css"

def build_tailwind():
    """Copy the Tailwind source file to the static output directory."""
    print("Building Tailwind CSS...")

    # Create output directory if it doesn't exist
    STATIC_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Copy the source CSS file
    if STATIC_SRC.exists():
        shutil.copy2(STATIC_SRC, STATIC_OUTPUT_FILE)
        print(f"✅ Copied {STATIC_SRC} to {STATIC_OUTPUT_FILE}")
    else:
        print(f"❌ Source file not found: {STATIC_SRC}")
        return False

    
    # Add basic CSS reset and Tailwind classes
    with open(STATIC_OUTPUT_FILE, 'a') as f:
        f.write("""

/* Additional basic styles for development */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: #000;
    color: #fff;
    text-decoration: none;
    border-radius: 0.25rem;
    border: 1px solid #000;
    transition: all 0.2s;
}

.btn:hover {
    background-color: #fff;
    color: #000;
}

.card {
    background: #fff;
    border: 1px solid #e5e5e5;
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.table {
    width: 100%;
    border-collapse: collapse;
}

.table th,
.table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e5e5e5;
}

.table th {
    font-weight: 600;
    background-color: #f9f9f9;
}
""")
    
    print("✅ Tailwind CSS build completed!")
    return True

if __name__ == "__main__":
    success = build_tailwind()
    exit(0 if success else 1)