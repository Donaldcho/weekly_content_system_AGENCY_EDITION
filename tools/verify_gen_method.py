
import sys
import os
sys.path.append(os.getcwd())

from backend.content_generator import ContentGenerator

try:
    cg = ContentGenerator()
    if hasattr(cg, 'generate_image'):
        print("SUCCESS: generate_image method exists.")
    else:
        print("FAILURE: generate_image method MISSING.")
        print(f"Available methods: {[m for m in dir(cg) if not m.startswith('__')]}")
except Exception as e:
    print(f"ERROR: {e}")
