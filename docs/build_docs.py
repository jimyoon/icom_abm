#!/usr/bin/env python3
"""
Script to build CHANCE-C documentation.
"""

import os
import sys
import subprocess
from pathlib import Path

def build_docs():
    """Build the Sphinx documentation."""
    docs_dir = Path(__file__).parent
    source_dir = docs_dir / "source"
    build_dir = docs_dir / "build"
    
    # Change to docs directory
    os.chdir(docs_dir)
    
    # Build HTML documentation
    try:
        subprocess.run([
            sys.executable, "-m", "sphinx.cmd.build",
            "-b", "html",
            "-d", str(build_dir / "doctrees"),
            str(source_dir),
            str(build_dir / "html")
        ], check=True)
        print("Documentation built successfully!")
        print(f"HTML files are in: {build_dir / 'html'}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error building documentation: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = build_docs()
    sys.exit(0 if success else 1) 