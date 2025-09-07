#!/usr/bin/env python3
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT, ".."))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "site_structure.txt")

EXCLUDE_DIRS = {"static", "staticfiles", "__pycache__"}
EXCLUDE_FILES = {"manage.py"}

VALID_EXTENSIONS = {".py", ".html"}

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
            # filter exclude dirs
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

            rel_dir = os.path.relpath(dirpath, PROJECT_ROOT)
            for filename in filenames:
                if filename in EXCLUDE_FILES:
                    continue
                _, ext = os.path.splitext(filename)
                if ext not in VALID_EXTENSIONS:
                    continue

                full_path = os.path.join(rel_dir, filename)
                f.write(f"\n# [{rel_dir}]\n")
                f.write(full_path + "\n")

if __name__ == "__main__":
    main()
