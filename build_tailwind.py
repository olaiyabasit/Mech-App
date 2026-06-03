#!/usr/bin/env python
"""
Production build script for Tailwind CSS v4.
Compiles Tailwind CSS using the standalone CLI via pytailwindcss.
"""

import os
import sys
import subprocess
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent
THEME_DIR = BASE_DIR / "theme"
STATIC_SRC = THEME_DIR / "static_src" / "src" / "styles.css"
STATIC_OUTPUT_DIR = THEME_DIR / "static" / "css"
STATIC_OUTPUT_FILE = STATIC_OUTPUT_DIR / "styles.css"

def build_tailwind():
    """Compile Tailwind CSS using pytailwindcss CLI."""
    print("🔧 Building Tailwind CSS for production...")
    print(f"📁 Source: {STATIC_SRC}")
    print(f"📁 Output: {STATIC_OUTPUT_FILE}")
    
    # Verify source file exists
    if not STATIC_SRC.exists():
        print(f"❌ Error: Source file not found: {STATIC_SRC}")
        return False
    
    # Create output directory if it doesn't exist
    STATIC_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # Use pytailwindcss to compile the CSS
        # The -i flag specifies input, -o specifies output
        # The --minify flag optimizes for production
        print("⚙️  Compiling Tailwind CSS...")
        
        result = subprocess.run(
            [
                sys.executable, "-m", "pytailwindcss",
                "-i", str(STATIC_SRC),
                "-o", str(STATIC_OUTPUT_FILE),
                "--minify"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check if output file was created
        if STATIC_OUTPUT_FILE.exists():
            file_size = STATIC_OUTPUT_FILE.stat().st_size
            print(f"✅ Tailwind CSS compiled successfully!")
            print(f"📊 Output file size: {file_size:,} bytes")
            
            # Verify the output has reasonable content
            if file_size < 1000:
                print(f"⚠️  Warning: Output file seems too small ({file_size} bytes)")
                print("    This might indicate a compilation issue.")
                return False
            
            return True
        else:
            print(f"❌ Error: Output file was not created: {STATIC_OUTPUT_FILE}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: Tailwind compilation failed!")
        print(f"   Exit code: {e.returncode}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error: Unexpected error during compilation: {e}")
        return False

if __name__ == "__main__":
    success = build_tailwind()
    
    if success:
        print("🎉 Build completed successfully!")
        sys.exit(0)
    else:
        print("💥 Build failed!")
        sys.exit(1)
