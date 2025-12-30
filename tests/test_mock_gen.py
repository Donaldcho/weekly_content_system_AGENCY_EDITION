
import sys
import os
sys.path.append(os.getcwd())
try:
    from backend.content_generator import ContentGenerator
    
    print("Initializing ContentGenerator...")
    gen = ContentGenerator()
    
    print("Testing _create_mock_image directly...")
    out = gen._create_mock_image("Test Prompt", "test_mock_output.png")
    
    if out:
        print(f"SUCCESS: Generated {out}")
    else:
        print("FAILURE: Returned None")

except Exception as e:
    print(f"CRITICAL EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
