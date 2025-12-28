import os
import shutil
from backend.rag import RAGEngine
from project_config import Config

# Setup
vault_dir = os.path.join(Config().ASSETS_DIR, "vault")
os.makedirs(vault_dir, exist_ok=True)

# Create dummy file
dummy_path = os.path.join(vault_dir, "test_policy.txt")
with open(dummy_path, "w") as f:
    f.write("This is a test policy for the Incremental Indexing verification.\n" * 50)

print("Created dummy file.")

# Run Ingestion
print("Running RAGEngine.ingest_vault()...")
rag = RAGEngine()
report = rag.ingest_vault()
print(f"Report 1: {report}")

# Modify file to force update (simple touch for now, but logical check handles new files)
# In our MVP logic, we check filenames. So let's add a NEW file.
dummy_path_2 = os.path.join(vault_dir, "test_policy_2.txt")
with open(dummy_path_2, "w") as f:
    f.write("This is a SECOND test policy.\n" * 10)

print("Added second file. Running ingestion again (should only process new file)...")
report_2 = rag.ingest_vault()
print(f"Report 2: {report_2}")

print("Done.")
