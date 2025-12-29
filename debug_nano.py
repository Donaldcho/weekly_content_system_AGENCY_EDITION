
import sys
import os
sys.path.append(os.getcwd())

# Ensure we see errors
try:
    from backend.nano_banana import NanoBanana
    
    print("Initializing NanoBanana...")
    nb = NanoBanana()
    print(f"Model: {nb.model_name}")
    
    print("Attempting to generate image...")
    # This calls the method that was returning the yellow card
    # We want to catch the error locally to see it
    
    # We will modify the NanoBanana class in memory to print the error if it swallows it? 
    # The current code prints "slipped: {e}". I need to see that output.
    
    path = nb.generate_image("A cute blue robot holding a sign saying SUCCESS")
    print(f"Result Path: {path}")
    
    if "nano_banana" in path:
        print("Seems to have worked (or placeholder generated). Check console logs for 'slipped'.")
    else:
        print("Unknown result.")

except Exception as e:
    import traceback
    traceback.print_exc()
